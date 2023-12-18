# stock_analyzer.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import tkinter as tk

class StockAnalyzer:
    @staticmethod
    def fetch_and_calculate_prices(stock_code, currency_code, start_date, end_date):
        stock_data = yf.download(stock_code, start_date, end_date)
        currency_data = yf.download(currency_code, start_date, end_date)

        merged_data = pd.merge(stock_data['Close'], currency_data['Close'], left_index=True, right_index=True, suffixes=(' (' + stock_code + '/TL)', ' (TL/USD)'))
        merged_data['Close (USD)'] = merged_data['Close'' (' + stock_code + '/TL)'] * merged_data['Close (TL/USD)']

        return merged_data

    @staticmethod
    def plot_chart(result_data, chart_canvas):
        plt.clf()
        plt.plot(result_data.index, result_data['Close (USD)'], label='Multiplied Closing Prices', color='#4CAF50', linestyle='-', linewidth=2)
        plt.title('USD Converted Closing Prices Chart', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('USD Converted Closing Prices', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)

        chart_canvas.draw()

    @staticmethod
    def time_range_button_clicked(stock_entry, result_text, chart_canvas, progress_bar, time_range):
        progress_bar.start()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=7) if time_range == '1 Week' else \
                     end_date - timedelta(days=30) if time_range == '1 Month' else \
                     end_date - timedelta(days=90) if time_range == '3 Months' else \
                     end_date - timedelta(days=180) if time_range == '6 Months' else \
                     end_date - timedelta(days=365) if time_range == '1 Year' else \
                     end_date - timedelta(days=365*3) if time_range == '3 Years' else \
                     end_date - timedelta(days=365*5) if time_range == '5 Years' else \
                     end_date - timedelta(days=365*10)

        stock_code = stock_entry.get() + ".IS"
        currency_code = "TRYUSD=X"

        result_data = StockAnalyzer.fetch_and_calculate_prices(stock_code, currency_code, start_date, end_date)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, str(result_data))
        result_text.config(state=tk.DISABLED)

        result_text.see(tk.END)

        StockAnalyzer.plot_chart(result_data, chart_canvas)
        progress_bar.stop()
