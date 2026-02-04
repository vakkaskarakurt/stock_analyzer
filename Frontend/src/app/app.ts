import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StockService, AnalysisResult, StockSummary, PredictionResult } from './services/stock.service';
import { MarketTickerComponent } from './components/market-ticker.component';
import { LeaderboardComponent } from './components/leaderboard.component';
import { TopPerformersComponent } from './components/top-performers.component';
import { ChartComponent } from './components/chart.component';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, MarketTickerComponent, LeaderboardComponent, TopPerformersComponent, ChartComponent],
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

  unit: string = 'GOLD'; // Sadece altın bazlı
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

  // Prediction
  predictionResult: PredictionResult | null = null;
  loadingPrediction: boolean = false;
  predictionDays: number = 30;

  constructor(private stockService: StockService) {}

  ngOnInit() {
    this.loadMarketSummary();
    this.loadWatchlist();
    this.loadTopPerformers();
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

  // Top Performers - otomatik yüklenir
  loadingTopPerformers: boolean = false;

  loadTopPerformers() {
    this.loadingTopPerformers = true;
    this.stockService.getTopPerformers().subscribe({
      next: (data) => {
        this.topPerformers = data;
        this.loadingTopPerformers = false;
      },
      error: () => { this.loadingTopPerformers = false; }
    });
  }

  // Hisse seçilince hem analiz hem tahmin yap
  onTopPerformerSelect(symbol: string) {
    this.symbol = symbol;
    this.showLeaders = false;
    this.unit = 'GOLD'; // Altın bazlı göster

    // Önce analiz yap
    this.analyze(symbol);

    // Sonra tahmin yap
    this.loadingPrediction = true;
    this.predictionResult = null;
    this.stockService.predict(symbol, this.predictionDays).subscribe({
      next: (data) => {
        this.predictionResult = data;
        this.loadingPrediction = false;
      },
      error: () => {
        this.loadingPrediction = false;
      }
    });
  }

  analyze(overrideSymbol?: string) {
    const sym = overrideSymbol || this.symbol;
    if (!sym) return;
    if (overrideSymbol) this.symbol = sym;

    this.loading = true;
    this.error = null;
    this.showLeaders = false;
    this.chartData = [];

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

  // Analiz + Tahmin birlikte
  analyzeWithPrediction() {
    if (!this.symbol) return;

    this.loading = true;
    this.loadingPrediction = true;
    this.error = null;
    this.showLeaders = false;
    this.chartData = [];
    this.predictionResult = null;

    const sym = this.symbol.toUpperCase();

    // Analiz isteği
    const analyzeReq = this.stockService.analyze(sym, this.unit, this.startDate, this.endDate);

    // Tahmin isteği
    const predictReq = this.stockService.predict(sym, this.predictionDays).pipe(
      catchError(err => {
        console.error('Tahmin hatası:', err);
        return of(null);
      })
    );

    // Her ikisini paralel çalıştır
    forkJoin([analyzeReq, predictReq]).subscribe({
      next: ([analysisData, predictionData]) => {
        if (!analysisData) {
          this.error = "Hisse verisi bulunamadı.";
          this.loading = false;
          this.loadingPrediction = false;
          return;
        }

        this.chartData = [analysisData];
        this.loading = false;

        if (predictionData) {
          this.predictionResult = predictionData;
        }
        this.loadingPrediction = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Bir hata oluştu!';
        this.loading = false;
        this.loadingPrediction = false;
      }
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

  // Prediction
  predict() {
    if (!this.symbol) return;

    this.loadingPrediction = true;
    this.predictionResult = null;
    this.error = null;

    this.stockService.predict(this.symbol, this.predictionDays).subscribe({
      next: (data) => {
        this.predictionResult = data;
        this.loadingPrediction = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Tahmin servisi çalışmıyor. Python servisini başlatın.';
        this.loadingPrediction = false;
      }
    });
  }

  closePrediction() {
    this.predictionResult = null;
  }

  getTrendIcon(): string {
    if (!this.predictionResult) return '';
    switch (this.predictionResult.trend) {
      case 'up': return 'bi-arrow-up-circle-fill';
      case 'down': return 'bi-arrow-down-circle-fill';
      default: return 'bi-dash-circle-fill';
    }
  }

  getTrendColor(): string {
    if (!this.predictionResult) return '';
    switch (this.predictionResult.trend) {
      case 'up': return 'text-success';
      case 'down': return 'text-danger';
      default: return 'text-warning';
    }
  }
}