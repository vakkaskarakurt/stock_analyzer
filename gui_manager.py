# gui_manager.py
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from stock_analyzer import StockAnalyzer, StockAnalyzerError
from matplotlib import pyplot as plt

class GUIManager:
    def __init__(self, root):
        """Initialize the GUI Manager."""
        self.root = root
        root.title("USD Cinsinden Türk Hisseleri")
        self.set_window_properties()
        self.create_widgets()

    def set_window_properties(self):
        """Set window properties."""
        self.root.geometry("800x1080")
        self.root.minsize(800, 1080)
        self.root.resizable(True, True)

    def create_widgets(self):
        """Create GUI widgets."""
        self.create_title_label()
        self.create_stock_entry()
        self.start_date_entry = self.create_date_entry("Başlangıç Tarihi:", 2)
        self.end_date_entry = self.create_date_entry("Bitiş Tarihi:", 3)
        self.create_time_range_buttons(['1 Hafta', '1 Ay', '3 Ay', '6 Ay', '1 Yıl', '3 Yıl', '5 Yıl', '10 Yıl'])
        self.create_result_text()
        self.create_chart_canvas()
        self.create_progress_bar()
        self.create_generate_chart_button()
        self.configure_grid()

    def configure_grid(self):
        """Configure grid."""
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

    def create_title_label(self):
        """Create title label."""
        title_label = ttk.Label(self.root, text="USD Cinsinden Türk Hisseleri", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=8, pady=20, sticky="nsew")

    def create_stock_entry(self):
        """Create stock entry."""
        ttk.Label(self.root, text="Hisse Kodu:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, pady=10, sticky="e")
        self.stock_entry = ttk.Entry(self.root, font=('Helvetica', 12))
        self.stock_entry.grid(row=1, column=1, pady=10, sticky="nsew")

    def create_date_entry(self, label_text, row):
        """Create date entry."""
        ttk.Label(self.root, text=label_text, font=('Helvetica', 12, 'bold')).grid(row=row, column=0, pady=10, sticky="e")
        date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=row, column=1, pady=10, sticky="nsew")
        return date_entry

    def create_time_range_buttons(self, button_texts):
        """Create time range buttons."""
        self.time_range_buttons = [ttk.Button(self.root, text=text, command=lambda text=text: self.time_range_button_clicked(text), style='TButton') for text in button_texts]

        for i, button in enumerate(self.time_range_buttons):
            button.grid(row=4, column=i, padx=10, pady=10, sticky="nsew")

    def create_result_text(self):
        """Create result text."""
        self.result_text_widget = tk.Text(self.root, height=15, width=60, state=tk.DISABLED)
        self.result_text_widget.grid(row=5, column=0, columnspan=8, pady=10, sticky="nsew")

    def create_chart_canvas(self):
        """Create chart canvas."""
        fig, ax = plt.subplots(figsize=(10, 4))
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.chart_widget = self.chart_canvas.get_tk_widget()
        self.chart_widget.grid(row=6, column=0, columnspan=8, pady=10, padx=10, sticky="nsew")

    def create_progress_bar(self):
        """Create progress bar."""
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=200)
        self.progress_bar.grid(row=7, column=0, columnspan=8, pady=10, sticky="nsew")

    def create_generate_chart_button(self):
        """Create generate chart button."""
        ttk.Button(self.root, text="Grafik Oluştur", command=self.generate_chart).grid(row=4, column=len(self.time_range_buttons), padx=10, pady=10, sticky="nsew")

    def time_range_button_clicked(self, time_range):
        """Handle time range button click."""
        try:
            StockAnalyzer.time_range_button_clicked(self.stock_entry, self.result_text_widget, self.chart_canvas, self.progress_bar, time_range)
        except StockAnalyzerError as e:
            self.show_error_message(f"Hata oluştu: {e}")

    def generate_chart(self):
        """Generate chart."""
        try:
            analyzer = StockAnalyzer()
            analyzer.generate_chart(self.stock_entry.get(), self.start_date_entry.get_date(), self.end_date_entry.get_date(), self.chart_canvas, self.progress_bar)
        except StockAnalyzerError as e:
            self.show_error_message(f"Hata oluştu: {e}")

    def show_error_message(self, message):
        """Show error message."""
        # You can customize this method to show error messages to the user (e.g., using a messagebox)
        print(message)

