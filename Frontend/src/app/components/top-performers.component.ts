import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockSummary } from '../services/stock.service';

@Component({
  selector: 'app-top-performers',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card-glass p-4 mb-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="text-white fw-bold m-0 d-flex align-items-center gap-2">
          <i class="bi bi-trophy-fill text-warning"></i>
          Altın Bazlı En Çok Kazananlar
        </h5>
        <span class="badge bg-warning bg-opacity-10 text-warning font-mono small">1 YILLIK</span>
      </div>

      <!-- Loading State -->
      <div *ngIf="loading" class="text-center py-4">
        <div class="spinner-border text-warning" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted small mt-2 mb-0">Veriler yükleniyor...</p>
      </div>

      <!-- Data Grid -->
      <div *ngIf="!loading && data.length > 0" class="row g-3">
        <div *ngFor="let stock of data.slice(0, 12); let i = index" class="col-6 col-md-4 col-lg-2">
          <div class="stock-card"
               [class.top-3]="i < 3"
               [class.gold]="i === 0"
               [class.silver]="i === 1"
               [class.bronze]="i === 2"
               (click)="onStockClick(stock)">

            <!-- Rank Badge -->
            <div class="rank-badge" *ngIf="i < 3">
              <span *ngIf="i === 0">🥇</span>
              <span *ngIf="i === 1">🥈</span>
              <span *ngIf="i === 2">🥉</span>
            </div>
            <div class="rank-number" *ngIf="i >= 3">{{ i + 1 }}</div>

            <!-- Symbol -->
            <div class="symbol">{{ stock.symbol }}</div>

            <!-- Change -->
            <div class="change" [class.positive]="stock.changePercentage >= 0" [class.negative]="stock.changePercentage < 0">
              {{ stock.changePercentage >= 0 ? '+' : '' }}{{ stock.changePercentage | number:'1.1-1' }}%
            </div>

            <!-- Gold Value -->
            <div class="gold-value">
              <i class="bi bi-coin"></i>
              {{ stock.currentPriceInGold | number:'1.4-4' }}
            </div>

            <!-- Action Hint -->
            <div class="action-hint">
              <i class="bi bi-graph-up-arrow"></i> Analiz
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div *ngIf="!loading && data.length === 0" class="text-center py-4">
        <i class="bi bi-inbox text-muted fs-1"></i>
        <p class="text-muted small mt-2 mb-0">Veri bulunamadı</p>
      </div>

      <!-- Show More -->
      <div *ngIf="!loading && data.length > 12" class="text-center mt-4">
        <button class="btn btn-sm btn-outline-warning rounded-pill px-4" (click)="showAll.emit()">
          <i class="bi bi-grid-3x3-gap me-2"></i>Tümünü Gör ({{ data.length }})
        </button>
      </div>
    </div>
  `,
  styles: [`
    .stock-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 16px 12px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .stock-card:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 193, 7, 0.3);
      transform: translateY(-4px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }

    .stock-card:hover .action-hint {
      opacity: 1;
      transform: translateY(0);
    }

    .stock-card.top-3 {
      border-width: 2px;
    }

    .stock-card.gold {
      background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(0, 0, 0, 0.3) 100%);
      border-color: rgba(255, 193, 7, 0.5);
    }

    .stock-card.silver {
      background: linear-gradient(135deg, rgba(192, 192, 192, 0.1) 0%, rgba(0, 0, 0, 0.3) 100%);
      border-color: rgba(192, 192, 192, 0.4);
    }

    .stock-card.bronze {
      background: linear-gradient(135deg, rgba(205, 127, 50, 0.1) 0%, rgba(0, 0, 0, 0.3) 100%);
      border-color: rgba(205, 127, 50, 0.4);
    }

    .rank-badge {
      font-size: 1.2rem;
      margin-bottom: 4px;
    }

    .rank-number {
      font-size: 0.7rem;
      color: #6c757d;
      font-family: monospace;
      margin-bottom: 4px;
    }

    .symbol {
      font-size: 1.1rem;
      font-weight: 700;
      color: white;
      margin-bottom: 4px;
    }

    .change {
      font-size: 1rem;
      font-weight: 600;
      font-family: monospace;
      margin-bottom: 4px;
    }

    .change.positive {
      color: #22c55e;
    }

    .change.negative {
      color: #ef4444;
    }

    .gold-value {
      font-size: 0.7rem;
      color: #ffc107;
      font-family: monospace;
      opacity: 0.8;
    }

    .gold-value i {
      font-size: 0.6rem;
      margin-right: 2px;
    }

    .action-hint {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: linear-gradient(transparent, rgba(255, 193, 7, 0.9));
      color: black;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 20px 8px 8px;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.3s ease;
    }

    .action-hint i {
      margin-right: 4px;
    }
  `]
})
export class TopPerformersComponent {
  @Input() data: StockSummary[] = [];
  @Input() loading: boolean = false;
  @Output() stockSelected = new EventEmitter<string>();
  @Output() showAll = new EventEmitter<void>();

  onStockClick(stock: StockSummary) {
    this.stockSelected.emit(stock.symbol);
  }
}
