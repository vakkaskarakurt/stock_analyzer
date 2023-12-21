# main.py
import tkinter as tk
from gui_manager import GUIManager

def main():
    # Tkinter kütüphanesini kullanarak yeni bir pencere oluştur
    root = tk.Tk()

    # GUIManager sınıfından bir nesne oluştur ve bu nesneyi oluşturulan pencereye bağla
    app = GUIManager(root)

    # Pencereyi sürekli olarak çalıştırarak kullanıcı etkileşimine izin ver
    root.mainloop()

# Eğer bu dosya doğrudan çalıştırılıyorsa (bağımsız olarak, başka bir dosya tarafından içe aktarılmamışsa)
if __name__ == "__main__":
    # main fonksiyonunu çağırarak programı başlat
    main()
