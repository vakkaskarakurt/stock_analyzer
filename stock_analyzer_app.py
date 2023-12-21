# stock_analyzer_app.py
import yfinance as yf  # Yahoo Finance verilerini çekmek için kullanılan kütüphane
import pandas as pd  # Veri çerçeveleri ve veri manipülasyonu için pandas kütüphanesi
from datetime import datetime, timedelta  # Tarih ve saat işlemleri için gerekli kütüphaneler
import matplotlib.pyplot as plt  # Grafik çizimleri için kullanılan kütüphane
import tkinter as tk  # GUI uygulamaları oluşturmak için kullanılan kütüphane
from custom_exceptions import StockAnalyzerError  # Özel hata sınıfımız

class StockAnalyzer:
    @staticmethod
    def get_stock_and_currency_data(stock_code, currency_code, start_date, end_date):
        try:
            # Hisse senedi ve döviz verilerini çek
            stock_data = yf.download(stock_code, start_date, end_date)
            currency_data = yf.download(currency_code, start_date, end_date)

            # Verileri birleştir ve dönüştür
            merged_data = pd.merge(stock_data['Close'], currency_data['Close'], left_index=True, right_index=True, suffixes=(' (' + stock_code + '/TL)', ' (TL/USD)'))
            merged_data['Close (USD)'] = merged_data['Close'' (' + stock_code + '/TL)'] * merged_data['Close (TL/USD)']

            return merged_data
        except Exception as e:
            # Hata durumunda özel hata sınıfını kullanarak hatayı işle
            raise StockAnalyzerError(f"Veri çekme veya analiz hatası: {e}")

    @staticmethod
    def draw_price_chart(result_data, chart_canvas):
        # Grafik çizimini temizle
        plt.clf()

        # Grafik çizimi
        plt.plot(result_data.index, result_data['Close (USD)'], label='Çarpılmış Kapanış Fiyatları', color='#4CAF50', linestyle='-', linewidth=2)
        plt.title('USD Dönüştürülmüş Kapanış Fiyatları Grafiği', fontsize=16)
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel('USD Dönüştürülmüş Kapanış Fiyatları', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)

        # Grafik çizimini güncelle
        chart_canvas.draw()

    @staticmethod
    def calculate_date_range(time_range):
        # Zaman aralığına göre başlangıç ve bitiş tarihlerini hesapla
        end_date = datetime.now()
        if time_range == '1 Week':
            start_date = end_date - timedelta(days=7)
        elif time_range == '1 Month':
            start_date = end_date - timedelta(days=30)
        elif time_range == '3 Months':
            start_date = end_date - timedelta(days=90)
        elif time_range == '6 Months':
            start_date = end_date - timedelta(days=180)
        elif time_range == '1 Year':
            start_date = end_date - timedelta(days=365)
        elif time_range == '3 Years':
            start_date = end_date - timedelta(days=365*3)
        elif time_range == '5 Years':
            start_date = end_date - timedelta(days=365*5)
        else:
            start_date = end_date - timedelta(days=365*10)

        return start_date, end_date

    @staticmethod
    def fetch_and_display_results(stock_entry, result_text, chart_canvas, progress_bar, time_range):
        # Hisse senedi kodu girilip girilmediğini kontrol et
        if not stock_entry.get():
            raise StockAnalyzerError("Lütfen bir hisse senedi kodu girin.")

        try:
            # İlerleme çubuğunu başlat
            progress_bar.start()

            # Tarih aralığını hesapla
            start_date, end_date = StockAnalyzer.calculate_date_range(time_range)
            stock_code = stock_entry.get() + ".IS"  # Hisse senedi kodunu oluştur
            currency_code = "TRYUSD=X"  # Döviz kodu

            # Hisse senedi ve döviz verilerini çek ve işle
            result_data = StockAnalyzer.get_stock_and_currency_data(stock_code, currency_code, start_date, end_date)

            # Sonuçları metin kutusuna ekle
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, str(result_data))
            result_text.config(state=tk.DISABLED)

            result_text.see(tk.END)

            # Grafik çizimini yap
            StockAnalyzer.draw_price_chart(result_data, chart_canvas)
        except Exception as e:
            # Hata durumunda hatayı işle
            error_message = f"Veri çekme veya analiz hatası: {e}"
            StockAnalyzer.handle_errors(error_message)
        finally:
            # İlerleme çubuğunu durdur
            progress_bar.stop()

    @staticmethod
    def handle_errors(error_message):
        # Hata durumunda özel hata sınıfını kullanarak hatayı işle
        raise StockAnalyzerError(error_message)
