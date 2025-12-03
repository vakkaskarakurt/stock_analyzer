import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import time
import os
import pickle
import warnings

# Uyarıları kapat
warnings.filterwarnings('ignore')

# Modern renkler
COLORS = {
    'bg': '#1e1e1e',
    'fg': '#ffffff',
    'accent': '#0d7377',
    'green': '#32de84',
    'red': '#ff6b6b',
    'gray': '#2d2d2d',
    'light_gray': '#3d3d3d'
}

class StockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BIST Analiz")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg'])
        
        self.cache = {}
        self.load_cache()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Üst panel
        top_frame = tk.Frame(self.root, bg=COLORS['bg'], pady=20)
        top_frame.pack(fill='x', padx=20)
        
        # Başlık
        title = tk.Label(top_frame, text="BIST Hisse Analizi", 
                        font=('Segoe UI', 28, 'bold'), 
                        bg=COLORS['bg'], fg=COLORS['accent'])
        title.pack()
        
        # Kontrol paneli - 1. Satır (Hisse + Birim)
        control_frame1 = tk.Frame(self.root, bg=COLORS['bg'])
        control_frame1.pack(fill='x', padx=20, pady=10)
        
        # Hisse kodu
        tk.Label(control_frame1, text="Hisse:", font=('Segoe UI', 12), 
                bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left', padx=5)
        
        self.stock_entry = tk.Entry(control_frame1, font=('Segoe UI', 14), 
                                    width=10, bg=COLORS['gray'], fg=COLORS['fg'],
                                    insertbackground=COLORS['fg'], relief='flat')
        self.stock_entry.pack(side='left', padx=5, ipady=5)
        self.stock_entry.bind('<Return>', lambda e: self.analyze_custom())
        
        # Birim seçimi
        tk.Label(control_frame1, text="Birim:", font=('Segoe UI', 12), 
                bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left', padx=(20, 5))
        
        self.unit_var = tk.StringVar(value='USD')
        
        for text, value in [('USD', 'USD'), ('Altin', 'GOLD')]:
            rb = tk.Radiobutton(control_frame1, text=text, variable=self.unit_var, 
                               value=value, font=('Segoe UI', 11),
                               bg=COLORS['bg'], fg=COLORS['fg'], 
                               selectcolor=COLORS['gray'],
                               activebackground=COLORS['bg'],
                               activeforeground=COLORS['accent'])
            rb.pack(side='left', padx=5)
        
        # Kontrol paneli - 2. Satır (Tarih Seçiciler)
        control_frame2 = tk.Frame(self.root, bg=COLORS['bg'])
        control_frame2.pack(fill='x', padx=20, pady=5)
        
        # Başlangıç tarihi
        tk.Label(control_frame2, text="Baslangic:", font=('Segoe UI', 12), 
                bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left', padx=5)
        
        self.start_date = DateEntry(control_frame2, 
                                    width=12, 
                                    font=('Segoe UI', 12),
                                    background=COLORS['accent'],
                                    foreground='white',
                                    borderwidth=2,
                                    date_pattern='dd/mm/yyyy',
                                    maxdate=datetime.now())
        self.start_date.set_date(datetime.now() - timedelta(days=30))
        self.start_date.pack(side='left', padx=5, ipady=3)
        
        # Bitiş tarihi
        tk.Label(control_frame2, text="Bitis:", font=('Segoe UI', 12), 
                bg=COLORS['bg'], fg=COLORS['fg']).pack(side='left', padx=(20, 5))
        
        self.end_date = DateEntry(control_frame2, 
                                 width=12, 
                                 font=('Segoe UI', 12),
                                 background=COLORS['accent'],
                                 foreground='white',
                                 borderwidth=2,
                                 date_pattern='dd/mm/yyyy',
                                 maxdate=datetime.now())
        self.end_date.set_date(datetime.now())
        self.end_date.pack(side='left', padx=5, ipady=3)
        
        # Analiz Et butonu
        analyze_btn = tk.Button(control_frame2, text="Analiz Et", 
                               command=self.analyze_custom,
                               font=('Segoe UI', 12, 'bold'),
                               bg=COLORS['green'], fg=COLORS['fg'],
                               activebackground=COLORS['accent'],
                               relief='flat', cursor='hand2',
                               width=12)
        analyze_btn.pack(side='left', padx=20, ipady=5)
        
        # Hızlı tarih butonları - Separator
        separator = tk.Frame(self.root, bg=COLORS['light_gray'], height=2)
        separator.pack(fill='x', padx=20, pady=10)
        
        # Label
        quick_label = tk.Label(self.root, text="Hizli Secim:", 
                              font=('Segoe UI', 11), 
                              bg=COLORS['bg'], fg=COLORS['fg'])
        quick_label.pack(anchor='w', padx=20, pady=(5, 5))
        
        # Periyot butonları
        btn_frame = tk.Frame(self.root, bg=COLORS['bg'])
        btn_frame.pack(fill='x', padx=20, pady=5)
        
        periods = [
            ('1H', '1 Hafta'), 
            ('1A', '1 Ay'), 
            ('3A', '3 Ay'), 
            ('6A', '6 Ay'),
            ('1Y', '1 Yil'), 
            ('3Y', '3 Yil'), 
            ('5Y', '5 Yil'), 
            ('10Y', '10 Yil')
        ]
        
        for label, period in periods:
            btn = tk.Button(btn_frame, text=label, 
                          command=lambda p=period: self.analyze_period(p),
                          font=('Segoe UI', 11, 'bold'),
                          bg=COLORS['accent'], fg=COLORS['fg'],
                          activebackground=COLORS['green'],
                          relief='flat', cursor='hand2',
                          width=8, height=1)
            btn.pack(side='left', padx=3, ipady=8)
        
        # Durum çubuğu
        status_frame = tk.Frame(self.root, bg=COLORS['gray'])
        status_frame.pack(fill='x', padx=20, pady=(10, 5))
        
        self.status_label = tk.Label(status_frame, text="Hazir", 
                                     font=('Segoe UI', 10),
                                     bg=COLORS['gray'], fg=COLORS['fg'],
                                     anchor='w')
        self.status_label.pack(side='left', padx=10, pady=5, fill='x', expand=True)
        
        # Cache temizle butonu
        clear_btn = tk.Button(status_frame, text="Cache Temizle",
                            command=self.clear_cache,
                            font=('Segoe UI', 9),
                            bg=COLORS['red'], fg=COLORS['fg'],
                            relief='flat', cursor='hand2')
        clear_btn.pack(side='right', padx=5, pady=5)
        
        # Grafik alanı
        chart_frame = tk.Frame(self.root, bg=COLORS['bg'])
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(14, 7), facecolor=COLORS['bg'])
        self.ax.set_facecolor(COLORS['gray'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Başlangıç mesajı
        self.ax.text(0.5, 0.5, 'Hisse kodu girin ve tarih secin', 
                    ha='center', va='center', fontsize=18, color=COLORS['fg'],
                    transform=self.ax.transAxes)
        self.canvas.draw()
    
    def analyze_period(self, period):
        """Hızlı periyot butonları için"""
        stock = self.stock_entry.get().upper().strip()
        
        if not stock:
            messagebox.showerror("Hata", "Hisse kodu girin!")
            return
        
        # Tarihleri otomatik ayarla
        end_date = datetime.now()
        days = {
            '1 Hafta': 7, '1 Ay': 30, '3 Ay': 90, '6 Ay': 180,
            '1 Yil': 365, '3 Yil': 1095, '5 Yil': 1825, '10 Yil': 3650
        }
        start_date = end_date - timedelta(days=days[period])
        
        # Tarih seçicileri güncelle
        self.start_date.set_date(start_date)
        self.end_date.set_date(end_date)
        
        # Analizi çalıştır
        self.analyze(start_date, end_date)
    
    def analyze_custom(self):
        """Kullanıcının seçtiği tarihlerle analiz"""
        stock = self.stock_entry.get().upper().strip()
        
        if not stock:
            messagebox.showerror("Hata", "Hisse kodu girin!")
            return
        
        # Tarihleri al
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        
        # Tarih kontrolü
        if start_date >= end_date:
            messagebox.showerror("Hata", "Baslangic tarihi bitis tarihinden once olmali!")
            return
        
        if end_date > datetime.now().date():
            messagebox.showerror("Hata", "Bitis tarihi bugunun tarihinden sonra olamaz!")
            return
        
        # Datetime'a çevir
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time())
        
        # Analizi çalıştır
        self.analyze(start_datetime, end_datetime)
    
    def analyze(self, start_date, end_date):
        """Ana analiz fonksiyonu"""
        stock = self.stock_entry.get().upper().strip()
        
        self.status_label.config(text="Yukleniyor...")
        self.root.update()
        
        try:
            unit = self.unit_var.get()
            
            # Cache kontrol
            cache_key = f"{stock}_{start_date.date()}_{end_date.date()}_{unit}"
            
            if cache_key in self.cache:
                data = self.cache[cache_key]
                self.status_label.config(text="Cache'den yuklendi")
            else:
                # Veri çek
                data = self.fetch_data(stock, start_date, end_date, unit)
                self.cache[cache_key] = data
                self.save_cache()
                self.status_label.config(text="Basarili")
            
            # Grafik çiz
            self.plot_data(stock, data, unit, start_date, end_date)
            
        except Exception as e:
            self.status_label.config(text="Hata!")
            messagebox.showerror("Hata", str(e))
    
    def fetch_data(self, stock, start, end, unit):
        """Veri çekme"""
        try:
            # Hisse verisi
            self.status_label.config(text="Hisse verisi cekiliyor...")
            self.root.update()
            
            stock_data = yf.download(f"{stock}.IS", start=start, end=end, 
                                    progress=False, auto_adjust=True)
            time.sleep(1)
            
            if stock_data.empty:
                raise Exception(f"{stock} bulunamadi!")
            
            # USD kuru
            self.status_label.config(text="Dolar kuru cekiliyor...")
            self.root.update()
            
            usd_data = None
            for ticker in ["TRY=X", "USDTRY=X"]:
                try:
                    usd_data = yf.download(ticker, start=start, end=end, 
                                          progress=False, auto_adjust=True, timeout=10)
                    if not usd_data.empty:
                        break
                    time.sleep(0.5)
                except:
                    continue
            
            if usd_data is None or usd_data.empty:
                # Son çare: TRYUSD tersini al
                try:
                    usd_temp = yf.download("TRYUSD=X", start=start, end=end, 
                                          progress=False, auto_adjust=True)
                    usd_data = pd.DataFrame()
                    usd_data['Close'] = 1 / usd_temp['Close']
                except:
                    raise Exception("USD kuru cekilemedi! Lutfen tekrar deneyin.")
            
            time.sleep(1)
            
            df = pd.DataFrame()
            df['TRY'] = stock_data['Close']
            df['USD_RATE'] = usd_data['Close']
            df = df.dropna()
            
            if df.empty:
                raise Exception("Veri eslesmiyor! Farkli tarih araliği deneyin.")
            
            df['USD'] = df['TRY'] / df['USD_RATE']
            
            if unit == 'GOLD':
                # Altın fiyatı
                self.status_label.config(text="Altin fiyati cekiliyor...")
                self.root.update()
                
                gold_data = yf.download("GC=F", start=start, end=end, 
                                       progress=False, auto_adjust=True)
                time.sleep(1)
                
                if gold_data.empty:
                    raise Exception("Altin fiyati cekilemedi!")
                
                df['GOLD_PRICE'] = gold_data['Close']
                df = df.dropna()
                
                if df.empty:
                    raise Exception("Altin verisi eslesmiyor!")
                
                df['GOLD'] = df['USD'] / df['GOLD_PRICE']
                return df['GOLD']
            
            return df['USD']
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or 'too many' in error_msg:
                raise Exception("Cok fazla istek! 5-10 dakika bekleyin.")
            elif 'timeout' in error_msg or 'timed out' in error_msg:
                raise Exception("Baglanti zaman asimi! Internet baglantinizi kontrol edin.")
            else:
                raise Exception(f"Hata: {str(e)}")
    
    def plot_data(self, stock, data, unit, start_date, end_date):
        """Grafik çiz"""
        self.ax.clear()
        
        # Değişim hesapla
        first = data.iloc[0]
        last = data.iloc[-1]
        change = ((last - first) / first) * 100
        
        # Renk seç
        color = COLORS['green'] if change >= 0 else COLORS['red']
        arrow = '^' if change >= 0 else 'v'
        
        # Grafik
        self.ax.plot(data.index, data.values, color=color, linewidth=2.5)
        
        # Başlık
        unit_text = 'Ons Altin' if unit == 'GOLD' else 'USD'
        date_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        title = f'{stock} - {unit_text}\n{date_range}\n{arrow} Degisim: %{change:.2f}'
        self.ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
        
        # Grid
        self.ax.grid(True, alpha=0.2, linestyle='--')
        
        # Etiketler
        self.ax.set_xlabel('Tarih', fontsize=14, fontweight='bold')
        self.ax.set_ylabel(unit_text, fontsize=14, fontweight='bold')
        
        # Değer göstergeleri
        self.ax.annotate(f'{first:.4f}', xy=(data.index[0], first),
                        xytext=(10, 20), textcoords='offset points',
                        fontsize=11, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', 
                                 facecolor=color, alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
        
        self.ax.annotate(f'{last:.4f}', xy=(data.index[-1], last),
                        xytext=(-10, 20), textcoords='offset points',
                        ha='right', fontsize=11, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', 
                                 facecolor=color, alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color=color, lw=2))
        
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        self.fig.tight_layout()
        self.canvas.draw()
    
    def load_cache(self):
        """Cache yükle"""
        try:
            if os.path.exists('cache.pkl'):
                with open('cache.pkl', 'rb') as f:
                    self.cache = pickle.load(f)
        except:
            self.cache = {}
    
    def save_cache(self):
        """Cache kaydet"""
        try:
            with open('cache.pkl', 'wb') as f:
                pickle.dump(self.cache, f)
        except:
            pass
    
    def clear_cache(self):
        """Cache temizle"""
        self.cache = {}
        try:
            if os.path.exists('cache.pkl'):
                os.remove('cache.pkl')
            messagebox.showinfo("Basarili", "Cache temizlendi!")
            self.status_label.config(text="Cache temizlendi")
        except Exception as e:
            messagebox.showerror("Hata", f"Cache temizleme hatasi: {e}")
    
    def run(self):
        """Programı başlat"""
        self.root.mainloop()

if __name__ == "__main__":
    app = StockApp()
    app.run()