# Trendyol Ürün Yorumları Özeti
Bu proje, Trendyol'daki ürün yorumlarını çekip özetleyen bir uygulamadır. Kullanıcı seçtiği trednyol ürününün bağlantısını gönderir ve yorumlarını özet halinde ekranda alır. 

## Görünüm

![Screenshot 2024-09-03 201232](https://github.com/user-attachments/assets/18f6f251-de54-47e1-86af-70f4e0c5b58f)

## Kurulum

Proje Python 3.12.5 ile çalışmaktadır.

**Not:** Bu kodu çalıştırmak için OpenAi'nin sunduğu API KEY'e sahip olmalısınız.



Gerekli kütüphaneleri yükleyin:

```bash
pip install streamlit
pip install openai
pip install selenium

Projeyi çalıştırmak için aşağıdaki komutu kullanın:
streamlit run proje_ek.py


### Kullanım

1. Uygulamayı başlattıktan sonra, ekranda çıkan arama çubuğuna ürünün bağlantısını ekleyin.
2. Seçilen ürüne ait yorumlar otomatik olarak çekilecektir.
3. Yorumlar özetlendikten sonra ekranda özet olarak görüntülenecektir.
