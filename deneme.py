import yfinance as yf
from datetime import datetime
import pandas as pd

stock_code = "HEKTS.IS"
start_date = "2023-11-14"
end_date = datetime.now().strftime("%Y-%m-%d")
end_date = "2023-11-15"

currency_code = "TRYUSD=X"

# Hisse senedi ve döviz kuru verilerini yfinance kullanarak çek
stock_data = yf.download(stock_code, start=start_date, end=end_date, interval="30m")
currency_data = yf.download(currency_code, start=start_date, end=end_date, interval="1h")


print(stock_data)
print(currency_data)

# Tarih indekslerini aynı zaman dilimine dönüştürme
stock_data.index = stock_data.index.tz_localize(None)
currency_data.index = currency_data.index.tz_localize(None)

# Veri çerçevelerini tarih sütununa göre birleştirme
merged_data = pd.merge(stock_data, currency_data, how='inner', left_index=True, right_index=True)
merged_data["Close (USD)"] = merged_data["Close_x"] * merged_data["Close_y"]

print(merged_data["Close (USD)"])
