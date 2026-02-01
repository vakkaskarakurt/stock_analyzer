import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface StockPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface AnalysisResult {
  symbol: string;
  unit: string;
  changePercentage: number;
  prices: StockPrice[];
}

export interface StockSummary {
  symbol: string;
  changePercentage: number;
  currentPriceInGold: number;
}

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = 'http://localhost:5035/api/stock';

  constructor(private http: HttpClient) { }

  analyze(symbol: string, unit: string, start: string, end: string): Observable<AnalysisResult> {
    return this.http.get<AnalysisResult>(`${this.apiUrl}/analyze?symbol=${symbol}&unit=${unit}&startDate=${start}&endDate=${end}`);
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