import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import * as signalR from '@microsoft/signalr';

export interface StockPrice {
  date: DateTime;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface AnalysisResult {
  symbol: string;
  unit: string;
  prices: StockPrice[];
  changePercentage: number;
}

export interface StockSummary {
  symbol: string;
  changePercentage: number;
  currentPriceInGold: number;
}

type DateTime = string;

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = 'http://localhost:5035/api/stock';
  private hubConnection: signalR.HubConnection;
  
  // Real-time updates
  public marketUpdates$ = new BehaviorSubject<any>(null);

  constructor(private http: HttpClient) {
    this.hubConnection = new signalR.HubConnectionBuilder()
      .withUrl('http://localhost:5035/marketHub')
      .withAutomaticReconnect()
      .build();

    this.hubConnection.start().catch(err => console.error('SignalR Error: ' + err));

    this.hubConnection.on('ReceiveMarketUpdate', (data) => {
      this.marketUpdates$.next(data);
    });
  }

  analyze(symbol: string, unit: string, start: string, end: string): Observable<AnalysisResult> {
    return this.http.get<AnalysisResult>(`${this.apiUrl}/analyze?symbol=${symbol}&unit=${unit}&start=${start}&end=${end}`);
  }

  getTopPerformers(): Observable<StockSummary[]> {
    return this.http.get<StockSummary[]>(`${this.apiUrl}/top-performers`);
  }

  getMarketSummary(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/market-summary`);
  }

  getStocks(): Observable<any[]> {
    return this.http.get<any[]>('/stocks.json');
  }

  getAiComment(symbol: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/ai-comment?symbol=${symbol}`);
  }
}
