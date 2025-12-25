# Anomali 2: OCPP → CAN Gecikmesi

## Açıklama
Bu senaryo, bir OCPP `RemoteStartTransaction` komutu ile karşılık gelen CAN bus yanıtı arasındaki anormal gecikmeyi simüle eder. Normalde, OCPP sunucusu bir başlatma komutu gönderdiğinde, CAN bus 1-2 saniye içinde yanıt vermelidir. Bu saldırı önemli bir gecikme ekler.

## Güvenlik Etkisi
- **Saldırı Türü**: Ortadaki Adam (MitM) / Zamanlama Saldırısı
- **Risk Seviyesi**: ORTA
- **Etki**: Ele geçirilmiş ağ geçidi, ağ sorunları veya kötü niyetli gecikme enjeksiyonunu gösterebilir

## Nasıl Çalışır
1. OCPP sunucusu `RemoteStartTransaction` komutu gönderir
2. Ağ geçidi 2 saniye içinde CAN mesajı (ID `0x200`) göndermelidir
3. Saldırgan CAN yanıtını 10+ saniye geciktirir
4. IDS, gecikme eşiği aştığında tespit eder

## Tespit Yöntemi
- OCPP komutu alındığında zaman damgasını takip et
- Beklenen CAN yanıtını (ID 0x200) izle
- Zaman farkını hesapla ve eşik değerle karşılaştır
- Gecikme > 2 saniye ise alarm ver

## Testi Çalıştırma

### IDS'i OCPP Entegrasyonu ile Başlat (Terminal 1)
```bash
python anomalies/02_ocpp_can_delay/test_scenario.py --mode ids
```

### Saldırı Senaryosunu Çalıştır (Terminal 2)
```bash
python anomalies/02_ocpp_can_delay/test_scenario.py --mode attack
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 2: Anormal gecikme tespit edildi - OCPP → CAN 0x200: 10.5s (eşik: 2.0s)
🚨 GÜVENLİK YANITI TETİKLENDİ 🚨
```

## Konfigürasyon
- `expected_can_id`: Başlatma komutu için CAN ID (varsayılan: 0x200)
- `normal_delay_seconds`: Normal gecikme (varsayılan: 0.5)
- `attack_delay_seconds`: Saldırı gecikmesi (varsayılan: 10.0)
- `threshold_seconds`: Tespit eşiği (varsayılan: 2.0)
