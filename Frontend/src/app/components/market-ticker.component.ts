import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-market-ticker',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="data" class="border-bottom border-white border-opacity-10 py-2" style="background: rgba(0,0,0,0.3); backdrop-filter: blur(10px);">
      <div class="container d-flex gap-5 justify-content-center justify-content-lg-start overflow-auto">
        <!-- USD Card -->
        <div class="d-flex align-items-center gap-3">
          <div class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 px-2 py-1 rounded font-mono">USD/TRY</div>
          <span class="fw-bold text-white font-mono">{{ data.usdPrice | number:'1.2-2' }}</span>
          <span class="small fw-bold font-mono" [ngClass]="data.usdChange >= 0 ? 'text-success' : 'text-danger'">
            <i class="bi" [ngClass]="data.usdChange >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
            %{{ data.usdChange | number:'1.2-2' }}
          </span>
        </div>
        <!-- Gold Card -->
        <div class="d-flex align-items-center gap-3 border-start border-white border-opacity-10 ps-5">
          <div class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 px-2 py-1 rounded font-mono">XAU/USD</div>
          <span class="fw-bold text-white font-mono">\${{ data.goldPrice | number:'1.0-0' }}</span>
          <span class="small fw-bold font-mono" [ngClass]="data.goldChange >= 0 ? 'text-success' : 'text-danger'">
            <i class="bi" [ngClass]="data.goldChange >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
            %{{ data.goldChange | number:'1.2-2' }}
          </span>
        </div>
      </div>
    </div>
  `
})
export class MarketTickerComponent {
  @Input() data: any;
}