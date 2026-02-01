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

export interface MarketSummary {
  usdPrice: number;
  usdChange: number;
  goldPrice: number;
  goldChange: number;
  bist100Price: number;
  bist100Change: number;
  nasdaqPrice: number;
  nasdaqChange: number;
}
