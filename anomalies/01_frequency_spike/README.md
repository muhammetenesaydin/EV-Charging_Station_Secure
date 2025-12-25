# Anomali 1: Frekans Sıçraması (Frequency Spike)

## Açıklama
Bu senaryo, CAN bus üzerinde anormal bir frekans sıçramasını simüle eder. Normalde hiç görünmeyen veya seyrek görünen bir CAN ID (örneğin `0x9FF`), aniden aşırı yüksek bir hızda mesaj göndermeye başlar.

## Güvenlik Etkisi
- **Saldırı Türü**: Hizmet Reddi (DoS)
- **Risk Seviyesi**: YÜKSEK
- **Etki**: CAN bus'ı tıkayabilir, meşru mesajların gecikmesine veya kaybolmasına neden olabilir

## Nasıl Çalışır
1. Saldırgan `0x9FF` ID'li CAN mesajlarını 100 Hz (saniyede 100 mesaj) hızında gönderir
2. Bu ID üzerindeki normal trafik 0-10 Hz olmalıdır
3. IDS, frekans eşik değerini (20 Hz) aştığında tespit eder

## Tespit Yöntemi
- Kayan zaman penceresi kullanarak her CAN ID için mesaj frekansını izle
- Frekans yapılandırılmış eşiği aştığında alarm ver
- Mesaj zaman damgalarını bir kuyrukta takip et

## Testi Çalıştırma

### IDS'i Başlat (Terminal 1)
```bash
python ids/ids_core.py
```

### Saldırı Senaryosunu Çalıştır (Terminal 2)
```bash
python anomalies/01_frequency_spike/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 1: CAN ID 0x9FF üzerinde frekans sıçraması tespit edildi - 100.0 msg/s (eşik: 20.0 msg/s)
🚨 GÜVENLİK YANITI TETİKLENDİ 🚨
Anomali Türü: Frekans Sıçraması
Detaylar: CAN ID 0x9FF
```

## Konfigürasyon
Ayarlanabilir parametreler için `config.json` dosyasına bakın:
- `can_id`: Saldırılacak CAN ID (varsayılan: 0x9FF)
- `frequency_hz`: Saldırı frekansı (varsayılan: 100)
- `duration_seconds`: Saldırı süresi (varsayılan: 5)
