def dosya_icerigini_txtye_yaz(py_dosyalari, txt_dosyasi):
    with open(txt_dosyasi, 'w', encoding='utf-8') as hedef_dosya:
        for py_dosyasi in py_dosyalari:
            with open(py_dosyasi, 'r', encoding='utf-8') as kaynak_dosya:
                hedef_dosya.write(kaynak_dosya.read())

# Kullanım örneği:
py_dosyalar = ["main.py", "gui_manager.py", "stock_analyzer.py", "custom_exceptions.py"]
txt_dosyasi = "sonuc.txt"

dosya_icerigini_txtye_yaz(py_dosyalar, txt_dosyasi)
