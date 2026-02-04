import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import * as signalR from '@microsoft/signalr';
import { environment } from '../../environments/environment';
import { AnalysisResult, StockSummary, MarketSummary, PredictionResult } from '../models/stock.models';

export type { AnalysisResult, StockSummary, MarketSummary, PredictionResult };

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = `${environment.apiUrl}/api/stock`;
  private hubUrl = `${environment.apiUrl}/marketHub`;
  private hubConnection: signalR.HubConnection;
  
  // Real-time updates
  public marketUpdates$ = new BehaviorSubject<MarketSummary | null>(null);

  constructor(private http: HttpClient) {
    this.hubConnection = new signalR.HubConnectionBuilder()
      .withUrl(this.hubUrl)
      .withAutomaticReconnect()
      .build();

    this.hubConnection.start().catch(err => console.error('SignalR Error: ' + err));

    this.hubConnection.on('ReceiveMarketUpdate', (data: MarketSummary) => {
      this.marketUpdates$.next(data);
    });
  }

  analyze(symbol: string, unit: string, start: string, end: string): Observable<AnalysisResult> {
    return this.http.get<AnalysisResult>(`${this.apiUrl}/analyze?symbol=${symbol}&unit=${unit}&start=${start}&end=${end}`);
  }

  getTopPerformers(): Observable<StockSummary[]> {
    return this.http.get<StockSummary[]>(`${this.apiUrl}/top-performers`);
  }

  getMarketSummary(): Observable<MarketSummary> {
    return this.http.get<MarketSummary>(`${this.apiUrl}/market-summary`);
  }

  getStocks(): Observable<any[]> {
    return this.http.get<any[]>('/stocks.json');
  }

  predict(symbol: string, days: number = 30, lookback: number = 60): Observable<PredictionResult> {
    return this.http.get<PredictionResult>(
      `${this.apiUrl}/predict?symbol=${symbol}&days=${days}&lookback=${lookback}`
    );
  }
}
