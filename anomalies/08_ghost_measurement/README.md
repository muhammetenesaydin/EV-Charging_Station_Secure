# Anomali 8: "Hayalet" Ölçüm Değişimi

## Açıklama
MeterValues mesajlarında ani, fiziksel olarak imkansız enerji sıçramaları (0 → 50 kWh/saniye) simüle edilir.

## Güvenlik Etkisi
- **Saldırı Türü**: Veri Manipülasyonu / Fatura Sahtekarlığı
- **Risk Seviyesi**: YÜKSEK
- **Etki**: Yanlış faturalama, enerji hırsızlığı, sistem güvenilirliğinin kaybı

## Nasıl Çalışır
1. Normal enerji artışı: 0-5 kWh/saniye
2. Saldırgan ani sıçrama yapar: 0 → 50 kWh (1 saniyede)
3. IDS enerji değişim hızını izler

## Tespit Yöntemi
- Ardışık MeterValues mesajları arasındaki enerji farkı hesaplanır
- Delta/saniye değeri hesaplanır
- Eşik değer: 5 kWh/saniye
- Eşik aşıldığında alarm üretilir

## Testi Çalıştırma

```bash
python anomalies/08_ghost_measurement/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 8: Anormal energy delta - 50.0/s (eşik: 5.0/s)
```

## Konfigürasyon
- `initial_energy`: Başlangıç enerjisi (varsayılan: 1000 Wh)
- `ghost_jump`: Hayalet sıçrama miktarı (varsayılan: 50000 Wh = 50 kWh)
- `threshold_per_second`: Tespit eşiği (varsayılan: 5000 Wh/s = 5 kWh/s)
