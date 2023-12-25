# stock_analyzer.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from custom_exceptions import StockAnalyzerError

class StockAnalyzer:
    MINUTE_INTERVAL = "30m"
    DAY_INTERVAL = "1d"
    CURRENCY_CODE = "TRYUSD=X"
    TIME_RANGES = {
        '1 Hafta': timedelta(days=7),
        '1 Ay': timedelta(days=30),
        '3 Ay': timedelta(days=90),
        '6 Ay': timedelta(days=180),
        '1 Yıl': timedelta(days=365),
        '3 Yıl': timedelta(days=365*3),
        '5 Yıl': timedelta(days=365*5),
        '10 Yıl': timedelta(days=365*10)
    }

    @staticmethod
    def get_price_data(stock_code, currency_code, start_date, end_date, time_range):
        try:
            time_range_timedelta = StockAnalyzer.TIME_RANGES[time_range]
            if time_range_timedelta <= timedelta(days=30):
                stock_data = yf.download(stock_code, start=start_date, end=end_date, interval=StockAnalyzer.MINUTE_INTERVAL)
                currency_data = yf.download(currency_code, start=start_date, end=end_date, interval=StockAnalyzer.MINUTE_INTERVAL)
            else:
                stock_data = yf.download(stock_code, start=start_date, end=end_date, interval=StockAnalyzer.DAY_INTERVAL)
                currency_data = yf.download(currency_code, start=start_date, end=end_date, interval=StockAnalyzer.DAY_INTERVAL)

            # Tarih indekslerini aynı zaman dilimine dönüştürme
            stock_data.index = stock_data.index.tz_localize(None)
            currency_data.index = currency_data.index.tz_localize(None)

            # Veri çerçevelerini tarih sütununa göre birleştirme
            merged_data = pd.merge(stock_data['Close'], currency_data['Close'], left_index=True, right_index=True, suffixes=(' (' + stock_code + '/TL)', ' (TL/USD)'))
            merged_data['Close (USD)'] = merged_data['Close (' + stock_code + '/TL)'] * merged_data['Close (TL/USD)']
            return merged_data

        except Exception as e:
            raise StockAnalyzerError(f"An error occurred: {e}")

    @staticmethod
    def determine_time_range(end_date, time_range):
        return end_date - StockAnalyzer.TIME_RANGES[time_range]

    @staticmethod
    def time_range_button_clicked(stock_entry, result_text, chart_canvas, progress_bar, time_range):
        if not stock_entry.get():
            raise StockAnalyzerError("Lütfen bir hisse senedi kodu girin.")

        try:
            progress_bar.start()
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = StockAnalyzer.determine_time_range(datetime.now(), time_range)
            stock_code = stock_entry.get() + ".IS"
            currency_code = StockAnalyzer.CURRENCY_CODE
            result_data = StockAnalyzer.get_price_data(stock_code, currency_code, start_date, end_date, time_range)
            StockAnalyzer.update_result_text(result_text, result_data)
            StockAnalyzer.plot_chart(result_data, chart_canvas)

        except StockAnalyzerError as e:
            raise StockAnalyzerError(f"An error occurred: {e}")

        finally:
            progress_bar.stop()

    @staticmethod
    def update_result_text(result_text, result_data):
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(result_data))
        result_text.config(state=tk.DISABLED)
        result_text.see(tk.END)

    @staticmethod
    def plot_chart(result_data, chart_canvas):
        plt.clf()
        plt.plot(result_data.index, result_data['Close (USD)'], label='Çarpılmış Kapanış Fiyatları', color='#4CAF50', linestyle='-', linewidth=2)
        plt.title('USD Dönüştürülmüş Kapanış Fiyatları Grafiği', fontsize=16)
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel('USD Dönüştürülmüş Kapanış Fiyatları', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        chart_canvas.draw()

# Additional import statements and GUI-related code go here
