def dosya_icerigini_txtye_yaz(py_dosyalari, txt_dosyasi):
    with open(txt_dosyasi, 'w') as hedef_dosya:
        for py_dosyasi in py_dosyalari:
            with open(py_dosyasi, 'r') as kaynak_dosya:
                hedef_dosya.write(f"\n\n# {py_dosyasi}\n\n")
                hedef_dosya.write(kaynak_dosya.read())

# Kullanım örneği:
py_dosyalar = ["main.py", "gui_manager.py", "stock_analyzer.py","custom_exceptions.py"]  # İşlem yapılacak .py dosyalarının listesi
txt_dosyasi = "sonuc.txt"  # İçeriklerin yazılacağı txt dosyasının adı

dosya_icerigini_txtye_yaz(py_dosyalar, txt_dosyasi)
