# Anomali 7: WebSocket Bağlantı Seli

## Açıklama
Kısa sürede (5 saniyede) çok sayıda (100+) OCPP WebSocket bağlantısı açılarak DDoS saldırısı simüle edilir.

## Güvenlik Etkisi
- **Saldırı Türü**: Distributed Denial of Service (DDoS)
- **Risk Seviyesi**: KRİTİK
- **Etki**: Sunucu kaynaklarının tükenmesi, meşru kullanıcıların bağlanamaması

## Nasıl Çalışır
1. Saldırgan 5 saniyede 100+ WebSocket bağlantısı açar
2. Normal durumda 5 saniyede 0-5 bağlantı beklenir
3. IDS bağlantı sayısını izler ve eşik aşıldığında alarm üretir

## Tespit Yöntemi
- 5 saniyelik zaman penceresi içinde bağlantı sayısı izlenir
- Eşik değer: 10 bağlantı/5 saniye
- Eşik aşıldığında alarm ve bağlantı engelleme

## Testi Çalıştırma

```bash
python anomalies/07_websocket_flood/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 7: WebSocket seli tespit edildi - 127 bağlantı 5s içinde (eşik: 10)
```

## Konfigürasyon
- `connection_count`: Açılacak bağlantı sayısı (varsayılan: 100)
- `duration_seconds`: Süre (varsayılan: 5)
- `threshold`: Tespit eşiği (varsayılan: 10)
