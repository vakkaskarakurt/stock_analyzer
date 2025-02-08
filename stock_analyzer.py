import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from custom_exceptions import StockAnalyzerError

class StockAnalyzer:
    @staticmethod
    def get_stock_data(stock_code, start_date, end_date):
        try:
            stock = yf.download(f"{stock_code}.IS", start=start_date, end=end_date)
            currency = yf.download("TRYUSD=X", start=start_date, end=end_date)
            
            if stock.empty or currency.empty:
                raise StockAnalyzerError("Veri bulunamadı")
                
            df = pd.DataFrame()
            df['Stock Price (TRY)'] = stock['Close']
            df['USD/TRY'] = currency['Close']
            df['Stock Price (USD)'] = df['Stock Price (TRY)'] / df['USD/TRY']
            
            return df
            
        except Exception as e:
            raise StockAnalyzerError(f"Veri çekme hatası: {str(e)}")

    @staticmethod
    def create_plot(data, stock_code):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data.index, data['Stock Price (USD)'], label=f'{stock_code} (USD)', 
                color='#2196F3', linewidth=2)
        
        ax.set_title(f'{stock_code} Hisse Senedi USD Değeri', pad=20)
        ax.set_xlabel('Tarih')
        ax.set_ylabel('USD Değeri')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig

    @staticmethod
    def get_time_delta(period):
        time_deltas = {
            '1 Hafta': timedelta(days=7),
            '1 Ay': timedelta(days=30),
            '3 Ay': timedelta(days=90),
            '6 Ay': timedelta(days=180),
            '1 Yıl': timedelta(days=365),
            '3 Yıl': timedelta(days=365*3),
            '5 Yıl': timedelta(days=365*5),
            '10 Yıl': timedelta(days=365*10)
        }
        return time_deltas.get(period, timedelta(days=30))