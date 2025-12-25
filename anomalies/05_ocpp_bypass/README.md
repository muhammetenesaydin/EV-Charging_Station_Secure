# Anomali 5: OCPP Bypass (Doğrudan CAN Başlatma)

## Açıklama
Bu senaryo, OCPP yetkilendirmesi olmadan doğrudan CAN hattı üzerinden şarj başlatma komutunun gönderilmesini simüle eder. Normal akışta, şarj başlatma komutu önce OCPP üzerinden yetkilendirilmeli, sonra CAN'a gönderilmelidir.

## Güvenlik Etkisi
- **Saldırı Türü**: Yetkilendirme Bypass / Yetkisiz Erişim
- **Risk Seviyesi**: KRİTİK
- **Etki**: Ücretsiz şarj, faturalama bypass, sistem güvenliğinin ihlali

## Nasıl Çalışır
1. Normal akış: OCPP RemoteStartTransaction → CAN 0x200 komutu
2. Saldırı: OCPP olmadan direkt CAN 0x200 komutu gönderilir
3. IDS, OCPP yetkilendirmesi olmayan CAN komutlarını tespit eder

## Tespit Yöntemi
- OCPP RemoteStartTransaction alındığında CAN komutu yetkilendirilir
- Yetkilendirme 5 saniye geçerlidir
- Yetkisiz CAN 0x200 komutu gelirse alarm üretilir

## Testi Çalıştırma

```bash
# Terminal 1: IDS'i başlat
python ids/ids_core.py

# Terminal 2: Bypass saldırısını çalıştır
python anomalies/05_ocpp_bypass/test_scenario.py
```

## Beklenen Çıktı
```
⚠️  ANOMALİ 5: Yetkisiz CAN komutu - 0x200 OCPP yetkilendirmesi olmadan gönderildi
🚨 GÜVENLİK YANITI TETİKLENDİ 🚨
```

## Konfigürasyon
- `can_id`: Başlatma komutu CAN ID (varsayılan: 0x200)
- `authorization_timeout`: Yetkilendirme geçerlilik süresi (varsayılan: 5 saniye)
