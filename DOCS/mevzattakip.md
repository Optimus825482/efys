Bir mevzuat takip botu (crawler/scraper) yapacaksanız, özellikle Enerji, OSB ve Resmi Gazete odaklı belirli kaynakları sürekli taramanız gerekir. Türkiye'de mevzuat dağınık olduğu için tek bir kaynak yetmez.

İşte botunuzun sürekli "ping" atması (kontrol etmesi) gereken URL'ler, Veri Kaynakları ve Takip Stratejisi:

1. Hedef Kaynaklar (Target Sources)
Botunuzun aşağıdaki siteleri belirli aralıklarla (örneğin her sabah 08:30'da) taraması gerekir:

A. Resmi Gazete (En Kritik Kaynak)
Her şeyin başladığı yerdir.

URL: https://www.resmigazete.gov.tr/

Ne Aranacak? "Enerji", "EPDK", "Organize Sanayi Bölgeleri", "Elektrik Piyasası", "Tarife", "Tebliğ" anahtar kelimeleri.

Bot Stratejisi: Site her gece 00:00'dan sonra güncellenir. Bot, o günün "Mükerrer" sayısı olup olmadığını da kontrol etmelidir.

B. EPDK (Enerji Piyasası Düzenleme Kurumu)
Elektrik tarifeleri ve kurul kararları burada yayınlanır.

URL (Duyurular): https://www.epdk.gov.tr/Detay/Icerik/3-0-0/duyurular

URL (Kurul Kararları): https://www.epdk.gov.tr/Detay/Icerik/3-0-21/kurul-kararlari

URL (Mevzuat): https://www.epdk.gov.tr/Detay/Icerik/3-1/elektrik-piyasasi-mevzuati

Ne Aranacak? "YEKDEM", "Dağıtım Bedeli", "Son Kaynak Tedarik Tarifesi", "OSB" kelimeleri. PDF dosyaları içinde OCR (metin tarama) yapılması gerekebilir çünkü bazen resim olarak taranmış PDF yüklerler.

C. Mevzuat.gov.tr (Cumhurbaşkanlığı Mevzuat Sistemi)
Değişen kanunların son hali buraya işlenir.

URL: https://www.mevzuat.gov.tr/

Takip Edilecek Kanun/Yönetmelikler:

4562 Sayılı OSB Kanunu

6446 Sayılı Elektrik Piyasası Kanunu

OSB Uygulama Yönetmeliği

Elektrik Piyasası Tarifeler Yönetmeliği

D. TEİAŞ (Türkiye Elektrik İletim A.Ş.)
İletim bedelleri ve sistem kullanım tarifeleri için.

URL: https://www.teias.gov.tr/tr/duyurular

Ne Aranacak? "İletim tarifesi", "Sistem kullanım bedeli", "Güç kalitesi".

2. Bot Mimarisinin Mantığı (Logic Flow)
Basit bir requests ve BeautifulSoup (Python) botu yeterli olmayabilir. Daha sağlam bir yapı için şu akışı öneririm:

Tarama (Scraping):

Bot belirtilen URL'lere gider.

Son 24 saatte eklenen yeni içerik (HTML <li>, <div> veya <a> etiketleri) var mı bakar.

Filtreleme (Keyword Filtering):

Her yeni içeriği veritabanındaki anahtar kelimelerle eşleştirir.

Keywords: ["Elektrik", "Tarife", "Dağıtım Bedeli", "OSB", "Organize Sanayi", "EPDK", "Sayaç", "Reaktif", "YEKDEM"]

İçerik Analizi (Parsing):

Eğer içerik bir Link ise: Linke tıklar, başlığı çeker.

Eğer içerik bir PDF ise: Python pdfplumber veya PyPDF2 kütüphanesi ile PDF'i indirir, içindeki metni okur ve anahtar kelime arar.

Bildirim (Notification):

Eşleşme varsa, Telegram, E-posta veya Slack üzerinden yöneticiye mesaj atar.

Örnek Mesaj: "🚨 DİKKAT: Resmi Gazete'de 'OSB Elektrik Tarifesi' hakkında yeni bir tebliğ yayınlandı. Link: ..."

3. Örnek Python Kod İskeleti (Basit Başlangıç)
Python ve feedparser (RSS için) veya requests kullanarak Resmi Gazete başlıklarını kontrol eden basit bir mantık:

Python
import requests
from bs4 import BeautifulSoup
from datetime import date

# Bugünün tarihini al (Resmi Gazete URL yapısı tarihe göredir)
today = date.today().strftime("%d.%m.%Y") # Örn: 29.01.2026
url = "https://www.resmigazete.gov.tr/"

keywords = ["ENERJİ", "EPDK", "ELEKTRİK", "OSB", "ORGANİZE SANAYİ"]

def check_resmi_gazete():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Başlıkları (Kanun, Yönetmelik, Tebliğ) çek
            titles = soup.find_all("a") 
            
            found_news = []
            
            for title in titles:
                text = title.get_text().upper()
                link = title.get('href')
                
                # Anahtar kelime kontrolü
                if any(keyword in text for keyword in keywords):
                    if link and "http" not in link: # Relative link düzeltme
                        link = "https://www.resmigazete.gov.tr/" + link
                    found_news.append(f"{text} - {link}")
            
            return found_news
            
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []

# Botu çalıştır
yeni_haberler = check_resmi_gazete()

if yeni_haberler:
    print(f"--- {today} TARİHLİ KRİTİK MEVZUATLAR ---")
    for haber in yeni_haberler:
        print(haber)
else:
    print("İlgili konularda yeni bir mevzuat bulunamadı.")
4. İleri Seviye Tavsiyeler
RSS Beslemeleri: Resmi Gazete ve EPDK'nın RSS (XML) beslemeleri varsa HTML kazımak (scrape) yerine bunları kullanmak daha stabildir.

Diff Checker: Mevzuat.gov.tr'deki bir kanun maddesi değiştiğinde, eski metin ile yeni metni kıyaslayıp (Diff) sadece değişen cümleyi size gösteren bir modül ekleyin. Bu, "Ne değişti?" sorusunu anında çözer.

YEKDEM Takibi: EPİAŞ Şeffaflık Platformu (seffaflik.epias.com.tr) üzerinden PTF (Piyasa Takas Fiyatı) verilerini API ile çekebilirsiniz. Bu bot değil, doğrudan API entegrasyonu olur ve faturayı anlık tahmin etmenizi sağlar.

Botun sunucu maliyeti neredeyse sıfır olur (AWS Lambda veya basit bir VDS üzerinde çalışabilir) ama size kazandıracağı zaman ve yasal riskten koruma değeri çok yüksektir.