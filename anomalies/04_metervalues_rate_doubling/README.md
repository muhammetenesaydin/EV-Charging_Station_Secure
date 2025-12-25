# Anomali 4: MeterValues Frekans İkiye Katlama

## Açıklama
Bu senaryo, normalde 1 Hz (saniyede 1 mesaj) olan MeterValues mesajlarının aniden 2 Hz'e (saniyede 2 mesaj) çıkarılmasını simüle eder.

## Güvenlik Etkisi
- **Saldırı Türü**: Veri Manipülasyonu / Fatura Sahtekarlığı
- **Risk Seviyesi**: ORTA
- **Etki**: Yanlış faturalama, sistem kaynaklarının tükenmesi, veri tabanı şişmesi

## Nasıl Çalışır
1. Normal durumda MeterValues mesajları 1 Hz'de gönderilir
2. Saldırgan frekansı 2 Hz'e çıkarır
3. IDS frekans değişimini tespit eder
4. Tolerans: ±%20 (0.8-1.2 Hz normal kabul edilir)

## Tespit Yöntemi
- Her mesaj için zaman damgası kaydedilir
- Ardışık mesajlar arası süre hesaplanır
- Beklenen frekansla karşılaştırılır
- Tolerans dışı değişimler için alarm üretilir

## Testi Çalıştırma

### IDS'i Başlat (Terminal 1)
```bash
python ids/ids_core.py
```

### Saldırı Senaryosunu Çalıştır (Terminal 2)
```bash
python anomalies/04_metervalues_rate_doubling/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 4: Frekans anomalisi tespit edildi - MeterValues: 2.1 Hz (beklenen: 1.0 Hz ±%20)
```

## Konfigürasyon
- `normal_rate_hz`: Normal frekans (varsayılan: 1.0)
- `attack_rate_hz`: Saldırı frekansı (varsayılan: 2.0)
- `tolerance`: Tolerans oranı (varsayılan: 0.2 = %20)
- `duration_seconds`: Saldırı süresi (varsayılan: 10)
