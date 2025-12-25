# Anomali 6: Hata Patlaması (Error Burst)

## Açıklama
CAN ID 0x301 (hata mesajı) üzerinden çok kısa sürede (1 saniyede 50+ mesaj) tekrarlayan hata mesajları gönderilerek DoS saldırısı simüle edilir.

## Güvenlik Etkisi
- **Saldırı Türü**: Denial of Service (DoS)
- **Risk Seviyesi**: YÜKSEK
- **Etki**: Sistem kaynaklarının tükenmesi, gerçek hataların gözden kaçması, log taşması

## Nasıl Çalışır
1. Saldırgan CAN ID 0x301'de saniyede 50 hata mesajı gönderir
2. Normal durumda hata mesajları nadirdir (dakikada 0-5)
3. IDS, kısa sürede çok sayıda hata mesajı tespit eder

## Tespit Yöntemi
- 1 saniyelik zaman penceresi içinde mesaj sayısı izlenir
- Eşik değer: 10 mesaj/saniye
- Eşik aşıldığında alarm üretilir

## Testi Çalıştırma

```bash
python anomalies/06_error_burst/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 6: Mesaj patlaması tespit edildi - ID 0x301: 50 mesaj 1.0s içinde (eşik: 10)
```

## Konfigürasyon
- `can_id`: Hata mesajı CAN ID (varsayılan: 0x301)
- `burst_count`: Gönderilecek mesaj sayısı (varsayılan: 50)
- `burst_duration`: Patlama süresi (varsayılan: 1.0 saniye)
- `threshold`: Tespit eşiği (varsayılan: 10 mesaj/saniye)
