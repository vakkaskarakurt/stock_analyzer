import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

stock_code = "HEKTS.IS"
start_date = "2023-12-20"
end_date = "2023-12-26"

currency_code = "TRYUSD=X"

# Hisse senedi ve döviz verilerini indir
stock_data = yf.download(stock_code, start=start_date, end=end_date, interval="30m")["Close"]
currency_data = yf.download(currency_code, start=start_date, end=end_date, interval="30m")["Close"]

# Verileri 'outer' birleştir
merged_data = pd.merge(stock_data, currency_data, left_index=True, right_index=True)
merged_data["Close (USD)"] = merged_data["Close_x"] * merged_data["Close_y"]

# Hafta sonlarını sil
merged_data = merged_data[~merged_data.index.dayofweek.isin([5, 6])]  # 5: Cumartesi, 6: Pazar

# Silinmeyen index'lerdeki günleri sil
merged_data = merged_data.dropna(subset=["Close (USD)"])

# Index'i sıfırla sadece veri olmayanlar için
merged_data.reset_index(drop=True, inplace=True)

# Çizim yap 
plt.figure(figsize=(10, 6))
plt.plot(merged_data.index, merged_data["Close (USD)"], label="Close (USD)")
plt.title("Stock Closing Price (USD)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
