# Anomali 10: Tekrar Saldırısı (Replay Attack)

## Açıklama
Aynı CAN mesajının (ID + payload) kısa sürede tekrar tekrar gönderilmesi ile replay saldırısı simüle edilir.

## Güvenlik Etkisi
- **Saldırı Türü**: Replay Attack / Message Injection
- **Risk Seviyesi**: YÜKSEK
- **Etki**: Geçmiş komutların tekrarlanması, yetkisiz işlemler, sistem manipülasyonu

## Nasıl Çalışır
1. Saldırgan geçerli bir CAN mesajını yakalar
2. Aynı mesajı (ID + payload) tekrar tekrar gönderir
3. IDS mesaj imzalarını (ID + payload hash) takip eder
4. 60 saniye içinde 3'ten fazla aynı mesaj tespit edilirse alarm

## Tespit Yöntemi
- Her CAN mesajı için imza oluşturulur (ID + payload)
- İmzalar zaman damgasıyla kaydedilir
- 60 saniyelik pencere içinde aynı imza sayılır
- Eşik: 3 tekrar/60 saniye

## Testi Çalıştırma

```bash
# Terminal 1: IDS'i başlat
python ids/ids_core.py

# Terminal 2: Replay saldırısını çalıştır
python anomalies/10_replay_attack/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 10: Tekrar saldırısı tespit edildi - CAN ID 0x200 payload [01020304] 5 kez görüldü
```

## Konfigürasyon
- `can_id`: Tekrarlanacak CAN ID (varsayılan: 0x200)
- `payload`: Tekrarlanacak payload (varsayılan: [0x01, 0x02, 0x03, 0x04])
- `replay_count`: Tekrar sayısı (varsayılan: 5)
- `interval_seconds`: Tekrarlar arası süre (varsayılan: 2)
- `threshold`: Tespit eşiği (varsayılan: 3)
