import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StockService, AnalysisResult, StockSummary } from './services/stock.service';
import { MarketTickerComponent } from './components/market-ticker.component';
import { LeaderboardComponent } from './components/leaderboard.component';
import { ChartComponent } from './components/chart.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, MarketTickerComponent, LeaderboardComponent, ChartComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  symbol: string = '';
  compareSymbol: string = '';
  
  // Autocomplete
  allStocks: any[] = [];
  filteredStocks: any[] = [];
  showSuggestions: boolean = false;
  isCompareSearch: boolean = false;

  unit: string = 'USD';
  startDate: string = '';
  endDate: string = '';
  loading: boolean = false;
  error: string | null = null;
  
  // Results
  chartData: AnalysisResult[] = [];
  
  // Dashboard Data
  topPerformers: StockSummary[] = [];
  marketSummary: any = null;
  
  // UI Flags
  loadingLeaders: boolean = false;
  showLeaders: boolean = false;
  comparisonMode: boolean = false;

  // AI
  aiComment: string | null = null;
  loadingAi: boolean = false;

  constructor(private stockService: StockService) {
    this.loadMarketSummary();
    this.stockService.getStocks().subscribe(data => this.allStocks = data);
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 12);
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
  }

  analyze() {
    if (!this.symbol) return;

    this.loading = true;
    this.error = null;
    this.showLeaders = false;
    this.chartData = [];
    this.aiComment = null; // Reset comment

    const mainReq = this.stockService.analyze(this.symbol, this.unit, this.startDate, this.endDate);
    const compareReq = (this.comparisonMode && this.compareSymbol) 
      ? this.stockService.analyze(this.compareSymbol, this.unit, this.startDate, this.endDate).pipe(catchError(() => of(null)))
      : of(null);

    forkJoin([mainReq, compareReq]).subscribe({
      next: ([mainData, compareData]) => {
        if (!mainData) {
          this.error = "Ana hisse verisi bulunamadı.";
          this.loading = false;
          return;
        }

        const results = [mainData];
        if (compareData) results.push(compareData as AnalysisResult);
        
        this.chartData = results;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Bir hata oluştu!';
        this.loading = false;
      }
    });
  }

  fetchAiComment(symbol: string) {
    this.loadingAi = true;
    this.stockService.getAiComment(symbol).subscribe({
      next: (res) => {
        this.aiComment = res.comment;
        this.loadingAi = false;
      },
      error: (err) => {
        console.error(err);
        this.loadingAi = false;
      }
    });
  }

  // --- Helpers ---
  loadLeaders() {
    this.loadingLeaders = true;
    this.showLeaders = true;
    this.error = null;
    this.stockService.getTopPerformers().subscribe({
      next: (data) => { this.topPerformers = data; this.loadingLeaders = false; },
      error: (err) => { this.error = err.message; this.loadingLeaders = false; }
    });
  }

  loadMarketSummary() {
    this.stockService.getMarketSummary().subscribe({
      next: (data) => this.marketSummary = data,
      error: (err) => console.error(err)
    });
  }

  setPeriod(months: number) {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - months);
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
    if (this.symbol) this.analyze();
  }

  onSearchInput(isCompare: boolean = false) {
    this.isCompareSearch = isCompare;
    const val = isCompare ? this.compareSymbol : this.symbol;
    if (!val) {
      this.filteredStocks = [];
      this.showSuggestions = false;
      return;
    }
    const query = val.toUpperCase();
    this.filteredStocks = this.allStocks.filter(s => 
      s.symbol.includes(query) || s.name.toUpperCase().includes(query)
    ).slice(0, 5);
    this.showSuggestions = true;
  }

  selectStock(stock: any) {
    if (this.isCompareSearch) this.compareSymbol = stock.symbol;
    else this.symbol = stock.symbol;
    this.showSuggestions = false;
    this.analyze();
  }

  hideSuggestions() { setTimeout(() => this.showSuggestions = false, 200); }
}
