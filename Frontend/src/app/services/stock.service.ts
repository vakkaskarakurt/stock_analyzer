import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface StockPrice {
  date: string;
  price: number;
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
  private apiUrl = 'http://localhost:5035/api/stock'; // Using HTTP port from dotnet run output

  constructor(private http: HttpClient) { }

  analyze(symbol: string, unit: string, start?: string, end?: string): Observable<AnalysisResult> {
    let url = `${this.apiUrl}/analyze?symbol=${symbol}&unit=${unit}`;
    if (start) url += `&start=${start}`;
    if (end) url += `&end=${end}`;
    return this.http.get<AnalysisResult>(url);
  }

  getTopPerformers(): Observable<StockSummary[]> {
    return this.http.get<StockSummary[]>(`${this.apiUrl}/top-performers`);
  }
}
