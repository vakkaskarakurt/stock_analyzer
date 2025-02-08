import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from stock_analyzer import StockAnalyzer
from custom_exceptions import StockAnalyzerError

class GUIManager:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_frames()
        self.create_widgets()
        self.setup_grid()

    def setup_window(self):
        self.root.title("BIST Hisse Senedi USD Analizi")
        self.root.state('zoomed')  # Tam ekran başlat
        self.root.minsize(1200, 800)  # Minimum pencere boyutu

    def create_frames(self):
        # Ana frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Üst kontrol frame'i
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Butonlar frame'i
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Grafik frame'i
        self.chart_frame = ttk.Frame(self.main_frame)
        self.chart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def create_widgets(self):
        # Stil ayarları
        style = ttk.Style()
        style.configure('Big.TButton', font=('Helvetica', 12))
        style.configure('Big.TLabel', font=('Helvetica', 14))
        style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'))

        # Başlık
        title_label = ttk.Label(self.control_frame, 
                              text="BIST Hisse Senedi USD Analizi", 
                              style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=4, pady=20)

        # Hisse kodu girişi
        stock_frame = ttk.Frame(self.control_frame)
        stock_frame.grid(row=1, column=0, columnspan=4, pady=15)
        
        ttk.Label(stock_frame, text="Hisse Kodu:", 
                 style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        self.stock_entry = ttk.Entry(stock_frame, 
                                   font=('Helvetica', 14), 
                                   width=15)
        self.stock_entry.pack(side=tk.LEFT, padx=10)

        # Tarih seçiciler
        date_frame = ttk.Frame(self.control_frame)
        date_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        ttk.Label(date_frame, text="Başlangıç:", 
                 style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        self.start_date = DateEntry(date_frame, 
                                  width=12, 
                                  font=('Helvetica', 12))
        self.start_date.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(date_frame, text="Bitiş:", 
                 style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        self.end_date = DateEntry(date_frame, 
                                width=12, 
                                font=('Helvetica', 12))
        self.end_date.pack(side=tk.LEFT, padx=10)

        # Hızlı tarih seçim butonları
        self.create_period_buttons()

        # Grafik alanı
        self.create_chart_area()

        # İlerleme çubuğu
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

    def create_period_buttons(self):
        periods = ['1 Hafta', '1 Ay', '3 Ay', '6 Ay', '1 Yıl', 
                  '3 Yıl', '5 Yıl', '10 Yıl']
        
        for i, period in enumerate(periods):
            btn = ttk.Button(self.button_frame, 
                           text=period,
                           command=lambda p=period: self.update_chart_for_period(p),
                           style='Big.TButton',
                           width=15)
            btn.grid(row=0, column=i, padx=5, pady=10, ipadx=10, ipady=5)
            self.button_frame.grid_columnconfigure(i, weight=1)

    def create_chart_area(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 10))  # Figür boyutunu büyüttük
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)

    def setup_grid(self):
        # Ana pencere grid yapılandırması
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Ana frame grid yapılandırması
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Pencere yeniden boyutlandırma olayını bağla
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        if hasattr(self, 'canvas'):
            # Minimum boyutlar
            min_width = 10
            min_height = 6
            
            # Mevcut frame boyutlarını al
            width = max(min_width, self.chart_frame.winfo_width() / 100)
            height = max(min_height, self.chart_frame.winfo_height() / 100)
            
            # Grafik boyutunu güncelle
            self.fig.set_size_inches(width, height)
            
            # Grafik başlık ve etiket boyutlarını güncelle
            self.update_chart_fonts()
            
            self.canvas.draw()

    def update_chart_fonts(self):
        # Grafik başlık ve etiketlerinin font boyutlarını güncelle
        if hasattr(self, 'ax'):
            width = self.chart_frame.winfo_width()
            scale_factor = width / 1000  # Baz genişlik 1000 pixel
            
            title_size = max(16, int(16 * scale_factor))
            label_size = max(12, int(12 * scale_factor))
            tick_size = max(10, int(10 * scale_factor))
            
            title_obj = self.ax.get_title()
            if title_obj:
                self.ax.set_title(title_obj, fontsize=title_size)
            
            self.ax.set_xlabel(self.ax.get_xlabel(), fontsize=label_size)
            self.ax.set_ylabel(self.ax.get_ylabel(), fontsize=label_size)
            self.ax.tick_params(axis='both', which='major', labelsize=tick_size)

    def update_chart_for_period(self, period):
        if not self.stock_entry.get():
            messagebox.showerror("Hata", "Lütfen bir hisse kodu girin")
            return

        try:
            self.progress.start()
            end_date = datetime.now()
            start_date = end_date - StockAnalyzer.get_time_delta(period)
            self.update_chart(start_date, end_date)
        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            self.progress.stop()

    def update_chart(self, start_date, end_date):
        try:
            stock_code = self.stock_entry.get().upper()
            data = StockAnalyzer.get_stock_data(stock_code, start_date, end_date)
            
            self.ax.clear()
            self.ax.plot(data.index, data['Stock Price (USD)'], 
                        label=f'{stock_code} (USD)', 
                        color='#2196F3', 
                        linewidth=2)
            
            # Font boyutlarını büyüttük
            self.ax.set_title(f'{stock_code} Hisse Senedi USD Değeri', 
                            pad=20, 
                            fontsize=24)  # Başlık boyutu 24pt
            self.ax.set_xlabel('Tarih', fontsize=20)  # X ekseni etiketi 20pt
            self.ax.set_ylabel('USD Değeri', fontsize=20)  # Y ekseni etiketi 20pt
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend(fontsize=18)  # Legend boyutu 18pt
            
            # Eksen değerlerinin boyutunu artır
            self.ax.tick_params(axis='both', which='major', labelsize=16)  # Eksen değerleri 16pt
            plt.setp(self.ax.get_xticklabels(), rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except StockAnalyzerError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")