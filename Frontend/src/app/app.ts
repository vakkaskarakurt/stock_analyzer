import { Component, OnInit } from '@angular/core';
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
export class AppComponent implements OnInit {
  symbol: string = '';
  compareSymbol: string = '';
  
  allStocks: any[] = [];
  filteredStocks: any[] = [];
  showSuggestions: boolean = false;
  isCompareSearch: boolean = false;

  unit: string = 'USD';
  startDate: string = '';
  endDate: string = '';
  loading: boolean = false;
  error: string | null = null;
  
  chartData: AnalysisResult[] = [];
  topPerformers: StockSummary[] = [];
  marketSummary: any = null;
  watchlist: string[] = [];
  
  loadingLeaders: boolean = false;
  showLeaders: boolean = false;
  comparisonMode: boolean = false;

  aiComment: string | null = null;
  loadingAi: boolean = false;

  constructor(private stockService: StockService) {}

  ngOnInit() {
    this.loadMarketSummary();
    this.loadWatchlist();
    this.stockService.getStocks().subscribe(data => this.allStocks = data);
    
    // SignalR Live Updates
    this.stockService.marketUpdates$.subscribe(data => {
      if (data) {
        this.marketSummary = data;
        console.log('Live Market Update Received via SignalR');
      }
    });
    
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 12);
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
  }

  analyze(overrideSymbol?: string) {
    const sym = overrideSymbol || this.symbol;
    if (!sym) return;
    if (overrideSymbol) this.symbol = sym;

    this.loading = true;
    this.error = null;
    this.showLeaders = false;
    this.chartData = [];
    this.aiComment = null;

    const mainReq = this.stockService.analyze(sym, this.unit, this.startDate, this.endDate);
    const compareReq = (this.comparisonMode && this.compareSymbol) 
      ? this.stockService.analyze(this.compareSymbol, this.unit, this.startDate, this.endDate).pipe(catchError(() => of(null)))
      : of(null);

    forkJoin([mainReq, compareReq]).subscribe({
      next: ([mainData, compareData]) => {
        if (!mainData) {
          this.error = "Hisse verisi bulunamadı.";
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
      next: (res) => { this.aiComment = res.comment; this.loadingAi = false; },
      error: () => { this.loadingAi = false; }
    });
  }

  // Watchlist Logic
  loadWatchlist() {
    const saved = localStorage.getItem('stock_watchlist');
    this.watchlist = saved ? JSON.parse(saved) : ['THYAO', 'EREGL', 'GARAN'];
  }

  toggleWatchlist(symbol: string) {
    const sym = symbol.toUpperCase();
    if (this.watchlist.includes(sym)) {
      this.watchlist = this.watchlist.filter(s => s !== sym);
    } else {
      this.watchlist.push(sym);
    }
    localStorage.setItem('stock_watchlist', JSON.stringify(this.watchlist));
  }

  // --- Helpers ---
  loadLeaders() {
    this.loadingLeaders = true;
    this.showLeaders = true;
    this.stockService.getTopPerformers().subscribe({
      next: (data) => { this.topPerformers = data; this.loadingLeaders = false; },
      error: () => { this.loadingLeaders = false; }
    });
  }

  loadMarketSummary() {
    this.stockService.getMarketSummary().subscribe(data => this.marketSummary = data);
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
    if (!val) { this.filteredStocks = []; this.showSuggestions = false; return; }
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