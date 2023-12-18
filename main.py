# main.py
import tkinter as tk
from stock_analyzer_app import StockAnalyzerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerApp(root)
    root.mainloop()
