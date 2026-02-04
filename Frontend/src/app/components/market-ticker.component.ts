import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-market-ticker',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="data" class="border-bottom border-white border-opacity-10 py-2" style="background: rgba(0,0,0,0.3); backdrop-filter: blur(10px);">
      <div class="container d-flex gap-5 justify-content-center overflow-auto">
        <!-- Gold Card -->
        <div class="d-flex align-items-center gap-3">
          <div class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 px-2 py-1 rounded font-mono">
            <i class="bi bi-coin me-1"></i>ALTIN (Ons)
          </div>
          <span class="fw-bold text-warning font-mono">\${{ data.goldPrice | number:'1.0-0' }}</span>
          <span class="small fw-bold font-mono" [ngClass]="data.goldChange >= 0 ? 'text-success' : 'text-danger'">
            <i class="bi" [ngClass]="data.goldChange >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
            %{{ data.goldChange | number:'1.2-2' }}
          </span>
        </div>

        <!-- BIST 100 / Gold Card -->
        <div class="d-flex align-items-center gap-3 border-start border-white border-opacity-10 ps-5">
          <div class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25 px-2 py-1 rounded font-mono">BIST 100</div>
          <span class="fw-bold text-white font-mono">{{ data.bist100Price | number:'1.0-0' }}</span>
          <span class="small fw-bold font-mono" [ngClass]="data.bist100Change >= 0 ? 'text-success' : 'text-danger'">
            <i class="bi" [ngClass]="data.bist100Change >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
            %{{ data.bist100Change | number:'1.2-2' }}
          </span>
        </div>
      </div>
    </div>
  `
})
export class MarketTickerComponent {
  @Input() data: any;
}