# stock_analyzer_app.py
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt  # Import matplotlib.pyplot

from stock_analyzer import StockAnalyzer

class StockAnalyzerApp:
    def __init__(self, root):
        self.root = root
        root.title("Turkish Stock Prices in USD")
        root.geometry("875x1200")
        root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Stock Code:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=10)
        self.stock_entry = ttk.Entry(self.root, font=('Helvetica', 12))
        self.stock_entry.grid(row=0, column=1, pady=10)

        self.create_date_entry("Start Date:", 1)
        self.create_date_entry("End Date:", 2)

        time_range_button_texts = ['1 Week', '1 Month', '3 Months', '6 Months', '1 Year', '3 Years', '5 Years', '10 Years']
        self.create_time_range_buttons(time_range_button_texts)

        self.create_result_text()
        self.create_chart_canvas()
        self.create_progress_bar()

    def create_date_entry(self, label_text, row):
        ttk.Label(self.root, text=label_text, font=('Helvetica', 12, 'bold')).grid(row=row, column=0, pady=10, sticky="e")
        date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=row, column=1, pady=10)
        return date_entry

    def create_time_range_buttons(self, button_texts):
        self.time_range_buttons = [ttk.Button(self.root, text=text, command=lambda text=text: self.time_range_button_clicked(text), style='TButton') for text in button_texts]

        for i, button in enumerate(self.time_range_buttons):
            button.grid(row=3, column=i, padx=10, pady=10)

    def create_result_text(self):
        self.result_text = tk.Text(self.root, height=15, width=60, state=tk.DISABLED)
        self.result_text.grid(row=4, column=0, columnspan=8, pady=10)

    def create_chart_canvas(self):
        self.chart_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.root)
        self.chart_widget = self.chart_canvas.get_tk_widget()
        self.chart_widget.grid(row=5, column=0, columnspan=8, pady=10, padx=10)

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=200)
        self.progress_bar.grid(row=6, column=0, columnspan=8, pady=10)

    def time_range_button_clicked(self, time_range):
        StockAnalyzer.time_range_button_clicked(self.stock_entry, self.result_text, self.chart_canvas, self.progress_bar, time_range)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerApp(root)
    root.mainloop()
