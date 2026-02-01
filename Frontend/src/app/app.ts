import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StockService, AnalysisResult, StockSummary } from './services/stock.service';
import { createChart, IChartApi, ISeriesApi, ColorType, LineSeries, CandlestickSeries } from 'lightweight-charts';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent implements OnDestroy {
  @ViewChild('chartContainer') chartContainer!: ElementRef;
  private chart: IChartApi | null = null;

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
  result: AnalysisResult | null = null;
  
  topPerformers: StockSummary[] = [];
  marketSummary: any = null;
  loadingLeaders: boolean = false;
  showLeaders: boolean = false;
  comparisonMode: boolean = false;

  constructor(private stockService: StockService) {
    this.loadMarketSummary();
    this.stockService.getStocks().subscribe(data => this.allStocks = data);
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 12);
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.remove();
    }
  }

  analyze() {
    if (!this.symbol) return;

    this.loading = true;
    this.error = null;
    this.showLeaders = false;

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

        this.result = mainData;
        const datasets = [mainData];
        if (compareData) datasets.push(compareData as AnalysisResult);
        
        setTimeout(() => this.renderChart(datasets), 100);
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Bir hata oluştu!';
        this.loading = false;
      }
    });
  }

  private renderChart(results: AnalysisResult[]) {
    if (!this.chartContainer) return;

    if (this.chart) {
      this.chart.remove();
      this.chart = null;
    }

    this.chart = createChart(this.chartContainer.nativeElement, {
      layout: {
        background: { type: ColorType.Solid, color: '#111111' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      width: this.chartContainer.nativeElement.clientWidth,
      height: 400,
    });

    const isComparison = results.length > 1;

    if (isComparison) {
      // Comparison: Line Charts
      results.forEach((res, index) => {
        const lineSeries = this.chart!.addSeries(LineSeries, {
          color: index === 0 ? '#0dcaf0' : '#ffc107',
          lineWidth: 2,
          title: res.symbol
        });
        
        const firstPrice = res.prices[0].close;
        const data = res.prices.map(p => ({
          time: p.date.split('T')[0],
          value: ((p.close - firstPrice) / firstPrice) * 100
        }));
        lineSeries.setData(data);
      });
    } else {
      // Single: Candlestick Chart
      const candleSeries = this.chart.addSeries(CandlestickSeries, {
        upColor: '#26a69a', 
        downColor: '#ef5350', 
        borderVisible: false, 
        wickUpColor: '#26a69a', 
        wickDownColor: '#ef5350' 
      });

      const data = results[0].prices.map(p => ({
        time: p.date.split('T')[0],
        open: Number(p.open),
        high: Number(p.high),
        low: Number(p.low),
        close: Number(p.close)
      }));
      candleSeries.setData(data);
    }

    this.chart.timeScale().fitContent();
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