# CAN Bus Payload Anomali Simülasyonu

Bu proje, elektrikli araç (EV) ile şarj istasyonu arasındaki CAN Bus trafiğinde payload temelli anomali tespitini (Man-in-the-Middle senaryosu) kural tabanlı bir IDS mantığı ile simüle eder ve görselleştirir.

## 🚀 Özellikler
- Normal ve saldırı (anomali) payload akışı üretimi
- Matplotlib ile görsel analiz (PNG çıktı: `simulation_result.png`)
- Anomali noktalarının kırmızı 'X' ile işaretlenmesi
- Tüm veri akışının CSV kaydı: `full_stream.csv`
- Anomali log dosyası (güvenlik uyarıları): `ids_alert_log.csv`
- Kütüphaneler yoksa metinsel özet fallback'i

## 📦 Kurulum
Önce bağımlılıkları yükleyin:

```powershell
pip install -r requirements.txt
```

(Alternatif hızlı kurulum)
```powershell
pip install matplotlib pandas
```

## ▶️ Çalıştırma
```powershell
python main.py
```
Çalıştırdıktan sonra:
- Konsolda simülasyon süreci mesajları görünür.
- `simulation_result.png` oluşur (grafik).
- `full_stream.csv` tüm akışın detaylarını içerir.
- `ids_alert_log.csv` tespit edilen anomalileri satır satır listeler.

### Streamlit Arayüzünü Başlatma
Adım adım canlı görselleştirme ve kontrol paneli için:
```powershell
streamlit run app.py
```
Ardından tarayıcıda açılan sayfadan:
- "Sonraki Paket" ile tek tek ilerleyebilir
- "Otomatik Çalıştır" kutusunu işaretleyerek belirlediğin hızda akışı otomatik görebilirsin
- Anomali paketler kırmızı X ile işaretlenir
- Metrikler: Toplam paket / Anomali sayısı / Anomali oranı
- CSV ve log dosyalarını butonlarla indirebilirsin
Sıfırlamak için "Sıfırla" butonunu kullan.

### 📦 Exe (Windows) Oluşturma
PyInstaller ile tek dosya çalıştırılabilir paketler üretebilirsin.

1. Bağımlılıkları kur:
```powershell
pip install -r requirements.txt
```
2. Build script çalıştır:
```powershell
pwsh -ExecutionPolicy Bypass -File build_exe.ps1
```
3. Çıktılar `dist/` klasöründe bulunur:
	- `CANSim.exe` : Konsol modunda simülasyon (grafik açılır)
	- `CANSimUI.exe` : Streamlit arayüzünü başlatır (tarayıcıyı açar)

Notlar:
- Defender uyarı verirse imzalanmamış olduğundan kaynaklı; izin verilebilir.
- Farklı port gerekiyor ise:
```powershell
$env:STREAMLIT_SERVER_PORT=8600; .\dist\CANSimUI.exe
```
- Daha küçük boyut: `--onefile --clean --noconsole` (UI için) seçebilirsin.


## 📂 Üretilen Dosyalar
| Dosya | Amaç |
|-------|------|
| `simulation_result.png` | Görselleştirilmiş veri akışı ve anomaliler |
| `full_stream.csv` | Her paket için zaman damgası, değer ve anomali bayrağı |
| `ids_alert_log.csv` | Kritik anomali olay logları (timestamp, level, event, payload) |
| `app.py` | Streamlit arayüzü (adım adım canlı görselleştirme) |

## 🧠 Algoritma Mantığı
Her payload değeri için eşik kontrolü yapılır:
- Güvenli aralık: \(0 \le I \le 100\)
- Değer bu aralığın dışındaysa `is_anomaly = True` kabul edilir ve loglanır.

## 📊 Rapor Bölümü Örneği
### 4.1. Payload Anomali Tespit Analizi
"Gerçekleştirilen simülasyonda, elektrikli araç şarj istasyonu ile EV arasındaki CAN Bus haberleşmesi modellenmiştir. 0x210 ID'li akım kontrol mesajları izlenmiş ve Matplotlib kütüphanesi ile görselleştirilmiştir (Şekil 1).

Grafik incelendiğinde:
- Yeşil Alan (Güvenli Bölge): \(0 \le I \le 100\) Amper aralığını temsil etmektedir. Protokol standartlarına uygun olan normal veri paketleri (Mavi noktalar) bu aralıkta seyretmektedir.
- Kırmızı İşaretler (Anomali): Saldırganın enjekte ettiği manipüle edilmiş paketler, IDS algoritması tarafından anında tespit edilmiştir. Özellikle \(I = 255\) ve \(I = 400\) gibi sistemin fiziksel kapasitesini zorlayacak değerler 'İçerik Anomali' (Content Anomaly) kuralına takılmıştır.

Sonuç: Geliştirilen kural tabanlı IDS (Intrusion Detection System), tanımlanan eşik değerler dışındaki tüm paketleri %100 başarıyla işaretlemiş ve sistem yöneticisine uyarı (alert) üretmiştir."

## 🔍 Geliştirme / İleri Çalışmalar
- Zaman serisi tabanlı istatistiksel eşikler (moving average, z-score)
- CAN ID bazlı farklı eşikler
- Gerçek zamanlı dashboard (Streamlit / Dash)
- Anomaliler için otomatik e-posta/Slack uyarısı

## ❗ Sorun Giderme
| Problem | Çözüm |
|---------|-------|
| `Import "matplotlib.pyplot" could not be resolved` | Ortamda matplotlib yok; `pip install matplotlib` çalıştırın. |
| Türkçe karakterler CSV'de bozuk | Dosyayı `UTF-8` ile açtığınızdan emin olun. |
| Grafik açılmıyor (headless sunucu) | `plt.savefig()` kullanımı zaten dosyayı üretir; `plt.show()` opsiyonel. |

## 📄 Lisans
Bu proje eğitim amaçlıdır.

---
Herhangi bir soruda destek isteyebilirsin. İyi çalışmalar!
