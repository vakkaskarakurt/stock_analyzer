# custom_exceptions.py

# Bu dosya, özel istisna sınıflarını içerir.

# StockAnalyzerError adında bir istisna sınıfı tanımlanıyor.
class StockAnalyzerError(Exception):
    # StockAnalyzerError, temel Exception sınıfından türetilmiştir.
    # Bu, özel bir hata türü oluşturmak için kullanılır.

    # Bu sınıf şu anda herhangi bir ek özellik içermiyor,
    # sadece temel Exception sınıfını miras alıyor.

    pass
# Yorum satırı: "pass" ifadesi, sınıfın herhangi bir ek özellik içermediğini belirtir.
# Bu durumda, sadece temel Exception sınıfını kullanıyoruz.

# Bu dosya, genellikle StockAnalyzer uygulamasının hata durumlarını işlemek
# ve daha okunabilir hata mesajları sağlamak için kullanılır.
