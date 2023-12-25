# main.py
import tkinter as tk
from gui_manager import GUIManager

def main():
    root = tk.Tk()
    app = GUIManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()