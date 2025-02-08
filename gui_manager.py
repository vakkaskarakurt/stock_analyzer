import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from stock_analyzer import StockAnalyzer
from custom_exceptions import StockAnalyzerError

# import timedelta
from datetime import timedelta

class GUIManager:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_frames()
        self.create_widgets()
        self.setup_grid()

    def setup_window(self):
        self.root.title("BIST Hisse Senedi Analizi")
        self.root.state('zoomed')
        self.root.minsize(1200, 800)

    def create_frames(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.chart_frame = ttk.Frame(self.main_frame)
        self.chart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def create_widgets(self):
        # Stil ayarları
        style = ttk.Style()
        style.configure('Big.TButton', font=('Helvetica', 12))
        style.configure('Big.TLabel', font=('Helvetica', 14))
        style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'))
        style.configure('Big.TRadiobutton', font=('Helvetica', 12))

        # Başlık
        title_label = ttk.Label(self.control_frame, 
                                text="BIST Hisse Senedi Analizi", 
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
        max_date = datetime.now()
        end_date = max_date
        start_date = end_date - timedelta(days=30)

        date_frame = ttk.Frame(self.control_frame)
        date_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        ttk.Label(date_frame, text="Başlangıç:", 
                    style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        self.start_date = DateEntry(date_frame, 
                                    width=12, 
                                    font=('Helvetica', 12),
                                    maxdate=max_date)
        self.start_date.set_date(start_date)
        self.start_date.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(date_frame, text="Bitiş:", 
                    style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        self.end_date = DateEntry(date_frame, 
                                width=12, 
                                font=('Helvetica', 12),
                                maxdate=max_date)
        self.end_date.set_date(end_date)
        self.end_date.pack(side=tk.LEFT, padx=10)

        # Birim seçim çerçevesi
        unit_frame = ttk.Frame(self.control_frame)
        unit_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        ttk.Label(unit_frame, text="Birim:", 
                    style='Big.TLabel').pack(side=tk.LEFT, padx=10)
        
        self.unit_var = tk.StringVar(value='USD')
        ttk.Radiobutton(unit_frame, text="USD Bazlı", 
                        variable=self.unit_var, value='USD',
                        style='Big.TRadiobutton',
                        command=lambda: self.update_chart(self.start_date.get_date(), 
                                                        self.end_date.get_date())).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(unit_frame, text="Altın Bazlı", 
                        variable=self.unit_var, value='GOLD',
                        style='Big.TRadiobutton',
                        command=lambda: self.update_chart(self.start_date.get_date(), 
                                                        self.end_date.get_date())).pack(side=tk.LEFT, padx=10)

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
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)

    def setup_grid(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        if hasattr(self, 'canvas'):
            width = max(10, self.chart_frame.winfo_width() / 100)
            height = max(6, self.chart_frame.winfo_height() / 100)
            self.fig.set_size_inches(width, height)
            self.update_chart_fonts()
            self.canvas.draw()

    def update_chart_fonts(self):
        if hasattr(self, 'ax'):
            width = self.chart_frame.winfo_width()
            scale_factor = width / 1000
            
            title_size = max(24, int(24 * scale_factor))
            label_size = max(20, int(20 * scale_factor))
            tick_size = max(16, int(16 * scale_factor))
            
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
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                
            if hasattr(start_date, 'strftime'):
                start_date = datetime.combine(start_date, datetime.min.time())
            if hasattr(end_date, 'strftime'):
                end_date = datetime.combine(end_date, datetime.min.time())

            base_unit = self.unit_var.get()
            data = StockAnalyzer.get_stock_data(stock_code, start_date, end_date, base_unit)
            
            self.ax.clear()
            
            if base_unit == 'GOLD':
                y_data = data['Stock Price (GOLD)']
                label = f'{stock_code} (Ons Altın)'
                ylabel = 'Ons Altın Değeri'
            else:
                y_data = data['Stock Price (USD)']
                label = f'{stock_code} (USD)'
                ylabel = 'USD Değeri'
            
            # Başlangıç ve bitiş değerlerini al
            first_value = y_data.iloc[0]
            last_value = y_data.iloc[-1]
            
            # Yüzde değişimi hesapla
            percent_change = ((last_value - first_value) / first_value) * 100
            
            # Grafik başlığını yüzde değişim ile güncelle
            title = f'{stock_code} Hisse Senedi {ylabel}\n'
            title += f'Değişim: %{percent_change:.2f} '
            title += '📈' if percent_change > 0 else '📉'
            
            self.ax.plot(data.index, y_data, 
                        label=label, 
                        color='#2196F3' if percent_change >= 0 else '#f44336', 
                        linewidth=2)
            
            self.ax.set_title(title, 
                            pad=20, 
                            fontsize=24)
            self.ax.set_xlabel('Tarih', fontsize=20)
            self.ax.set_ylabel(ylabel, fontsize=20)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend(fontsize=18)
            
            # Başlangıç ve bitiş değerlerini grafik üzerinde göster
            self.ax.annotate(f'Başlangıç: {first_value:.2f}',
                            xy=(data.index[0], first_value),
                            xytext=(10, 10),
                            textcoords='offset points',
                            fontsize=12)
            
            self.ax.annotate(f'Bitiş: {last_value:.2f}',
                            xy=(data.index[-1], last_value),
                            xytext=(-10, 10),
                            textcoords='offset points',
                            ha='right',
                            fontsize=12)
            
            self.ax.tick_params(axis='both', which='major', labelsize=16)
            plt.setp(self.ax.get_xticklabels(), rotation=45)
            
            self.fig.tight_layout()
            self.canvas.draw()
                
        except StockAnalyzerError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")