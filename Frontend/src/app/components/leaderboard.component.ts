import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockSummary } from '../services/stock.service';

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="animate-fade-in mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="fw-bold text-white m-0 d-flex align-items-center gap-2">
                <i class="bi bi-award text-warning"></i> 
                <span>Gold Standard <span class="text-muted fw-light">Rankings</span></span>
            </h3>
            <button class="btn btn-sm btn-outline-glass rounded-circle" (click)="close.emit()"><i class="bi bi-x-lg"></i></button>
        </div>

        <!-- Loading State -->
        <div *ngIf="loading" class="text-center py-5 card-glass">
            <div class="spinner-grow text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
            <h5 class="text-white fw-light tracking-wide">Crunching Market Data...</h5>
        </div>

        <!-- Data View -->
        <div *ngIf="!loading && data.length > 0">
            <!-- Top 3 Podium (Visual) -->
            <div class="row g-4 mb-5">
                <!-- 2. GÜMÜŞ -->
                <div class="col-md-4 order-2 order-md-1 mt-md-5" *ngIf="data[1]">
                    <div class="card-glass h-100 position-relative border-0 shadow-lg" style="background: linear-gradient(135deg, rgba(173, 173, 173, 0.1) 0%, rgba(0,0,0,0.4) 100%); border-top: 2px solid #adadad !important;">
                       <div class="card-body text-center p-4">
                          <div class="badge bg-secondary text-white px-3 py-1 rounded-pill mb-3 font-mono small">#2 SILVER</div>
                          <h2 class="fw-bold text-white mb-0">{{ data[1].symbol }}</h2>
                          <div class="text-success font-mono fs-4 my-2">+%{{ data[1].changePercentage | number:'1.0-2' }}</div>
                       </div>
                    </div>
                </div>

                <!-- 1. ALTIN -->
                <div class="col-md-4 order-1 order-md-2" *ngIf="data[0]">
                    <div class="card-glass h-100 position-relative shadow-lg border-0" style="background: linear-gradient(180deg, rgba(255, 193, 7, 0.15) 0%, rgba(0,0,0,0.5) 100%); border-top: 4px solid #ffc107 !important; transform: scale(1.05);">
                       <div class="card-body text-center py-5">
                          <div class="text-warning font-mono small tracking-widest mb-3">🏅 CHAMPION 🏅</div>
                          <h1 class="display-3 fw-bold text-white mb-0 text-glow">{{ data[0].symbol }}</h1>
                          <div class="badge bg-warning text-black fs-4 px-4 py-2 mt-3 mb-2 font-mono shadow">
                            +%{{ data[0].changePercentage | number:'1.0-2' }}
                          </div>
                          <div class="text-warning small text-uppercase tracking-widest opacity-75 font-mono">ANNUAL GOLD YIELD</div>
                       </div>
                    </div>
                </div>

                <!-- 3. BRONZ -->
                <div class="col-md-4 order-3 order-md-3 mt-md-5" *ngIf="data[2]">
                    <div class="card-glass h-100 position-relative border-0 shadow-lg" style="background: linear-gradient(135deg, rgba(205, 127, 50, 0.1) 0%, rgba(0,0,0,0.4) 100%); border-top: 2px solid #cd7f32 !important;">
                       <div class="card-body text-center p-4">
                          <div class="badge text-white px-3 py-1 rounded-pill mb-3 font-mono small" style="background-color: #a05a2c !important;">#3 BRONZE</div>
                          <h2 class="fw-bold text-white mb-0">{{ data[2].symbol }}</h2>
                          <div class="text-success font-mono fs-4 my-2">+%{{ data[2].changePercentage | number:'1.0-2' }}</div>
                       </div>
                    </div>
                </div>
            </div>

            <!-- Full Ranking Table (Glass Table) -->
            <div class="card-glass border-0 overflow-hidden mb-5">
                <div class="card-header bg-transparent border-bottom border-white border-opacity-10 py-3 px-4">
                    <h6 class="m-0 text-muted font-mono small tracking-widest">BIST PERFORMANCE (GOLD ADJUSTED)</h6>
                </div>
                <div class="table-responsive" style="max-height: 500px;">
                    <table class="table table-dark table-hover mb-0 align-middle glass-table">
                        <thead class="sticky-top bg-black">
                            <tr class="text-muted small font-mono">
                                <th class="ps-4 py-3 border-0">RANK</th>
                                <th class="py-3 border-0">SYMBOL</th>
                                <th class="text-end py-3 pe-4 border-0">ANNUAL RETURN (GOLD)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr *ngFor="let item of data; let i = index" class="border-bottom border-white border-opacity-5">
                                <td class="ps-4 py-3 font-mono">
                                    <span class="rank-badge" [ngClass]="{'gold': i==0, 'silver': i==1, 'bronze': i==2}">{{ i + 1 }}</span>
                                </td>
                                <td class="py-3">
                                    <div class="d-flex align-items-center gap-2">
                                        <span class="fw-bold text-white">{{ item.symbol }}</span>
                                        <span class="badge font-mono bg-info bg-opacity-10 text-info" style="font-size: 0.6rem;">BIST</span>
                                    </div>
                                </td>
                                <td class="text-end pe-4 py-3 font-mono fs-5">
                                    <span [ngClass]="item.changePercentage >= 0 ? 'text-success' : 'text-danger'">
                                        {{ item.changePercentage >= 0 ? '+' : '' }}{{ item.changePercentage | number:'1.2-2' }}%
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
  `,
  styles: [`
    .text-glow { text-shadow: 0 0 30px rgba(255, 193, 7, 0.4); }
    .tracking-widest { letter-spacing: 0.2em; }
    
    .glass-table tbody tr {
        transition: background-color 0.2s ease;
        background-color: transparent;
    }
    .glass-table tbody tr:hover {
        background-color: rgba(255, 255, 255, 0.03) !important;
    }

    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .rank-badge.gold { background: #ffc107; color: black; border: none; box-shadow: 0 0 10px rgba(255, 193, 7, 0.4); }
    .rank-badge.silver { background: #adadad; color: black; border: none; }
    .rank-badge.bronze { background: #cd7f32; color: black; border: none; }

    /* Sticky Header Fix */
    .table thead th {
        box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.1);
        background: #050505;
    }
  `]
})
export class LeaderboardComponent {
  @Input() data: StockSummary[] = [];
  @Input() loading: boolean = false;
  @Output() close = new EventEmitter<void>();
}