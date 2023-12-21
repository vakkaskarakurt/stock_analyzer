# main.py
import tkinter as tk
from gui_manager import GUIManager

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIManager(root)
    root.mainloop()
