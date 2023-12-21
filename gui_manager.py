import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from stock_analyzer import StockAnalyzer, StockAnalyzerError
from matplotlib import pyplot as plt

class GUIManager:
    def __init__(self, root):
        self.root = root
        root.title("USD Cinsinden Türk Hisseleri")
        root.geometry("875x1200")
        root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Başlık Etiketi
        title_label = ttk.Label(self.root, text="USD Cinsinden Türk Hisseleri", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=8, pady=20)

        # Hisse Kodu Giriş Alanı
        ttk.Label(self.root, text="Hisse Kodu:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, pady=10)
        self.stock_entry = ttk.Entry(self.root, font=('Helvetica', 12))
        self.stock_entry.grid(row=1, column=1, pady=10)

        # Başlangıç ve Bitiş Tarih Giriş Alanları
        self.create_date_entry("Başlangıç Tarihi:", 2)
        self.create_date_entry("Bitiş Tarihi:", 3)

        # Zaman Aralığı Düğmeleri
        time_range_button_texts = ['1 Hafta', '1 Ay', '3 Ay', '6 Ay', '1 Yıl', '3 Yıl', '5 Yıl', '10 Yıl']
        self.create_time_range_buttons(time_range_button_texts)

        # Sonuç Metin Alanı
        self.create_result_text()

        # Grafik Alanı
        self.create_chart_canvas()

        # İlerleme Çubuğu
        self.create_progress_bar()

    def create_date_entry(self, label_text, row):
        ttk.Label(self.root, text=label_text, font=('Helvetica', 12, 'bold')).grid(row=row, column=0, pady=10, sticky="e")
        date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=row, column=1, pady=10)
        return date_entry

    def create_time_range_buttons(self, button_texts):
        self.time_range_buttons = [ttk.Button(self.root, text=text, command=lambda text=text: self.time_range_button_clicked(text), style='TButton') for text in button_texts]

        for i, button in enumerate(self.time_range_buttons):
            button.grid(row=4, column=i, padx=10, pady=10)

    def create_result_text(self):
        self.result_text = tk.Text(self.root, height=15, width=60, state=tk.DISABLED)
        self.result_text.grid(row=5, column=0, columnspan=8, pady=10)

    def create_chart_canvas(self):
        self.chart_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.root)
        self.chart_widget = self.chart_canvas.get_tk_widget()
        self.chart_widget.grid(row=6, column=0, columnspan=8, pady=10, padx=10)

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=200)
        self.progress_bar.grid(row=7, column=0, columnspan=8, pady=10)

    def time_range_button_clicked(self, time_range):
        try:
            StockAnalyzer.time_range_button_clicked(self.stock_entry, self.result_text, self.chart_canvas, self.progress_bar, time_range)
        except StockAnalyzerError as e:
            print(f"Hata oluştu: {e}")

# Uygulama Oluştur
root = tk.Tk()
app = GUIManager(root)
root.mainloop()
