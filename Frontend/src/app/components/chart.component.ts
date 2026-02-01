import { Component, Input, Output, EventEmitter, ViewChild, ElementRef, AfterViewInit, OnDestroy, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { createChart, IChartApi, ColorType, LineSeries, CandlestickSeries } from 'lightweight-charts';
import { AnalysisResult, StockPrice } from '../models/stock.models';

@Component({
  selector: 'app-stock-chart',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="row justify-content-center animate-fade-in">
       <div class="col-lg-12">
          <div class="card-glass shadow-lg">
             <div class="card-header bg-transparent border-bottom border-white border-opacity-10 d-flex justify-content-between align-items-center py-3 px-4">
                <div>
                   <h5 class="text-white m-0 fw-bold d-flex align-items-center gap-2">
                     <span class="fs-4">{{ data[0].symbol }}</span>
                     <span *ngIf="data.length > 1" class="text-muted fs-6">vs {{ data[1].symbol }}</span>
                   </h5>
                   <small class="text-muted font-mono">
                     {{ data.length > 1 ? 'COMPARISON VIEW' : data[0].unit + ' MARKET VIEW' }}
                   </small>
                </div>
                <div class="d-flex gap-3 align-items-center">
                    <!-- Indicators Toggle -->
                    <div class="d-flex gap-2 me-2" *ngIf="data.length === 1">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="smaSwitch" [(ngModel)]="showSMA" (change)="renderChart()">
                            <label class="form-check-label text-secondary small fw-bold" for="smaSwitch">SMA 20</label>
                        </div>
                        <div class="form-check form-switch border-start border-secondary ps-4">
                            <input class="form-check-input" type="checkbox" id="rsiSwitch" [(ngModel)]="showRSI" (change)="renderChart()">
                            <label class="form-check-label text-secondary small fw-bold" for="rsiSwitch">RSI 14</label>
                        </div>
                    </div>

                    <button class="btn btn-sm btn-outline-glass px-3 rounded-pill" (click)="requestAi.emit(data[0].symbol)" [disabled]="loadingAi">
                        <i class="bi bi-stars me-2" [ngClass]="{'text-warning': !loadingAi}"></i> {{ loadingAi ? 'Analyzing...' : 'AI Insight' }}
                    </button>
                    
                    <div class="badge rounded-pill px-3 py-2 font-mono fs-6" 
                         [ngClass]="data[0].changePercentage >= 0 ? 'bg-success bg-opacity-25 text-success border border-success' : 'bg-danger bg-opacity-25 text-danger border border-danger'">
                       {{ data[0].changePercentage >= 0 ? '▲' : '▼' }} %{{ data[0].changePercentage | number:'1.2-2' }}
                    </div>
                </div>
             </div>
             <div class="card-body p-0 position-relative">
                <div #chartContainer style="height: 500px; width: 100%;"></div>
             </div>
             <!-- AI Comment Section -->
             <div *ngIf="aiComment" class="card-footer bg-transparent border-top border-white border-opacity-10 p-4">
                 <div class="d-flex align-items-start gap-3">
                     <div class="bg-primary bg-opacity-10 p-2 rounded-circle text-primary">
                        <i class="bi bi-robot fs-4"></i>
                     </div>
                     <div>
                         <h6 class="fw-bold mb-1 text-white">Gemini Market Intelligence</h6>
                         <p class="text-light opacity-75 mb-0 small lh-lg" [innerHTML]="aiComment"></p>
                     </div>
                 </div>
             </div>
          </div>
       </div>
    </div>
  `
})
export class ChartComponent implements AfterViewInit, OnDestroy, OnChanges {
  @Input() data: AnalysisResult[] = [];
  @Input() aiComment: string | null = null;
  @Input() loadingAi: boolean = false;
  @Output() requestAi = new EventEmitter<string>();

  @ViewChild('chartContainer') chartContainer!: ElementRef;
  
  private chart: IChartApi | null = null;
  showSMA: boolean = false;
  showRSI: boolean = false;

  ngAfterViewInit() {
    this.renderChart();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['data'] && !changes['data'].firstChange) {
      this.renderChart();
    }
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.remove();
    }
  }

  renderChart() {
    if (!this.chartContainer || this.data.length === 0) return;

    if (this.chart) {
      this.chart.remove();
      this.chart = null;
    }

    this.chart = createChart(this.chartContainer.nativeElement, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
      },
      width: this.chartContainer.nativeElement.clientWidth,
      height: 500,
      timeScale: { borderColor: 'rgba(255, 255, 255, 0.1)' },
    });

    const isComparison = this.data.length > 1;

    if (isComparison) {
      this.data.forEach((res, index) => {
        const lineSeries = this.chart!.addSeries(LineSeries, {
          color: index === 0 ? '#00f2fe' : '#ff9800',
          lineWidth: 2,
          title: res.symbol,
        });
        
        const firstPrice = res.prices[0].close;
        const chartData = res.prices.map((p: StockPrice) => ({
          time: p.date.split('T')[0],
          value: ((p.close - firstPrice) / firstPrice) * 100
        }));
        lineSeries.setData(chartData);
      });
    } else {
      const candleSeries = this.chart.addSeries(CandlestickSeries, {
        upColor: '#0ecb81', downColor: '#f6465d', borderVisible: false, 
        wickUpColor: '#0ecb81', wickDownColor: '#f6465d' 
      });

      const chartData = this.data[0].prices.map((p: StockPrice) => ({
        time: p.date.split('T')[0],
        open: Number(p.open),
        high: Number(p.high),
        low: Number(p.low),
        close: Number(p.close)
      }));
      candleSeries.setData(chartData);

      if (this.showSMA) {
        const smaData = calculateSMA(chartData, 20);
        const smaSeries = this.chart.addSeries(LineSeries, { 
            color: '#fbbf24', lineWidth: 2, title: 'SMA 20'
        });
        smaSeries.setData(smaData);
      }

      if (this.showRSI) {
        const rsiData = calculateRSI(chartData, 14);
        const rsiSeries = this.chart.addSeries(LineSeries, {
            color: '#e91e63', // Pink
            lineWidth: 1,
            title: 'RSI 14',
            priceScaleId: 'rsi-scale' // Separate scale
        });
        
        this.chart.priceScale('rsi-scale').applyOptions({
            scaleMargins: { top: 0.8, bottom: 0 }, // Bottom 20%
            borderColor: 'rgba(255, 255, 255, 0.1)',
        });
        
        rsiSeries.setData(rsiData);
      }
    }

    this.chart.timeScale().fitContent();
  }
}

// Helpers
interface ChartPoint { time: string; open?: number; high?: number; low?: number; close: number; value?: number; }

function calculateSMA(data: ChartPoint[], count: number) {
  var result = [];
  for (var i = count - 1; i < data.length; i++){
    var sum = 0;
    for (var j = 0; j < count; j++) sum += data[i - j].close;
    result.push({ time: data[i].time, value: sum / count });
  }
  return result;
}

function calculateRSI(data: ChartPoint[], count: number) {
    let result = [];
    let gains = [];
    let losses = [];
    
    for (let i = 1; i < data.length; i++) {
        let diff = data[i].close - data[i-1].close;
        gains.push(Math.max(0, diff));
        losses.push(Math.max(0, -diff));
    }

    let avgGain = gains.slice(0, count).reduce((a, b) => a + b) / count;
    let avgLoss = losses.slice(0, count).reduce((a, b) => a + b) / count;

    for (let i = count; i < data.length; i++) {
        let rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        result.push({ time: data[i].time, value: 100 - (100 / (100 + rs)) });

        avgGain = (avgGain * (count - 1) + gains[i-1]) / count;
        avgLoss = (avgLoss * (count - 1) + losses[i-1]) / count;
    }
    return result;
}
