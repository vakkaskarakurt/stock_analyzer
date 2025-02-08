import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from custom_exceptions import StockAnalyzerError

class StockAnalyzer:
    @staticmethod
    def get_stock_data(stock_code, start_date, end_date, base='USD'):
        try:
            # Veri çekme işlemi
            stock = yf.download(f"{stock_code}.IS", start=start_date, end=end_date)
            try:
                # TRY=X ile dolar kurunu al
                usd = yf.download("TRY=X", start=start_date, end=end_date)
            except:
                # Başarısız olursa USDTRY=X'i dene
                try:
                    usd = yf.download("USDTRY=X", start=start_date, end=end_date)
                except:
                    # O da başarısız olursa TRYUSD=X'i dene ve tersini al
                    usd_temp = yf.download("TRYUSD=X", start=start_date, end=end_date)
                    usd = pd.DataFrame()
                    usd['Close'] = 1 / usd_temp['Close']  # TL/USD değerini USD/TL'ye çevir
            
            if base == 'GOLD':
                gold = yf.download("GC=F", start=start_date, end=end_date)
                
                df = pd.DataFrame()
                df['Stock Price (TRY)'] = stock['Close']
                df['USD/TRY'] = usd['Close']
                df['Gold (USD/Ounce)'] = gold['Close']
                
                # NaN değeri olan satırları sil
                df = df.dropna()
                
                # Altın bazlı değeri hesapla
                df['Stock Price (GOLD)'] = (df['Stock Price (TRY)'] / df['USD/TRY']) / df['Gold (USD/Ounce)']
                
                return df
            else:
                df = pd.DataFrame()
                df['Stock Price (TRY)'] = stock['Close']
                df['USD/TRY'] = usd['Close']
                
                # NaN değeri olan satırları sil
                df = df.dropna()
                
                # USD değerini hesapla
                df['Stock Price (USD)'] = df['Stock Price (TRY)'] / df['USD/TRY']
                
                return df
                
        except Exception as e:
            raise StockAnalyzerError(f"Veri çekme hatası: {str(e)}")

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