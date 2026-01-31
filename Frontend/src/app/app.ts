import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StockService, AnalysisResult, StockSummary } from './services/stock.service';
import { BaseChartDirective, provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective],
  providers: [provideCharts(withDefaultRegisterables())],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  symbol: string = '';
  unit: string = 'USD';
  startDate: string = '';
  endDate: string = '';
  loading: boolean = false;
  error: string | null = null;
  result: AnalysisResult | null = null;
  
  // Top Performers
  topPerformers: StockSummary[] = [];
  loadingLeaders: boolean = false;
  showLeaders: boolean = false;

  // Chart Properties
  public lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: [
      {
        data: [],
        label: 'Fiyat',
        fill: true,
        tension: 0.5,
        borderColor: '#0d7377',
        backgroundColor: 'rgba(13, 115, 119, 0.2)'
      }
    ]
  };

  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        grid: { color: 'rgba(255,255,255,0.1)' },
        ticks: { color: '#ffffff' }
      },
      x: {
        grid: { color: 'rgba(255,255,255,0.1)' },
        ticks: { color: '#ffffff' }
      }
    },
    plugins: {
      legend: { display: false }
    }
  };

  constructor(private stockService: StockService) {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 1);

    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
  }

  analyze() {
    if (!this.symbol) return;

    this.loading = true;
    this.error = null;
    this.showLeaders = false;

    this.stockService.analyze(this.symbol, this.unit, this.startDate, this.endDate).subscribe({
      next: (data) => {
        this.result = data;
        this.updateChart(data);
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Bir hata oluştu!';
        this.loading = false;
      }
    });
  }

  loadLeaders() {
    this.loadingLeaders = true;
    this.showLeaders = true;
    this.error = null;
    
    this.stockService.getTopPerformers().subscribe({
      next: (data) => {
        this.topPerformers = data;
        this.loadingLeaders = false;
      },
      error: (err) => {
        this.error = 'Lider tablosu yüklenemedi: ' + err.message;
        this.loadingLeaders = false;
      }
    });
  }

  setPeriod(months: number) {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - months);
    
    this.endDate = end.toISOString().split('T')[0];
    this.startDate = start.toISOString().split('T')[0];
    
    if (this.symbol) {
      this.analyze();
    }
  }

  private updateChart(data: AnalysisResult) {
    this.lineChartData = {
      labels: data.prices.map(p => new Date(p.date).toLocaleDateString()),
      datasets: [
        {
          data: data.prices.map(p => p.price),
          label: `${data.symbol} (${data.unit})`,
          fill: true,
          tension: 0.3,
          borderColor: data.changePercentage >= 0 ? '#32de84' : '#ff6b6b',
          backgroundColor: data.changePercentage >= 0 ? 'rgba(50, 222, 132, 0.2)' : 'rgba(255, 107, 107, 0.2)',
          pointRadius: 0,
          borderWidth: 3
        }
      ]
    };
  }
}
