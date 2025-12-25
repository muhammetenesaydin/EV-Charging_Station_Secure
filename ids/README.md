# Saldırı Tespit Sistemi (IDS)

Bu dizin, CAN ↔ OCPP anomalilerini tespit etmek için IDS bileşenlerini içerir.

## Modüller

### `rules.py`
Tüm 10 anomali senaryosu için tespit kuralları:
1. **FrequencySpikeDetector**: Anormal mesaj frekanslarını tespit eder
2. **OCPPCANDelayDetector**: OCPP komutları ile CAN yanıtları arasındaki gecikmeleri tespit eder
3. **OutOfRangeDetector**: Payload değerlerini bilinen aralıklara göre doğrular
4. **RateChangeDetector**: Periyodik mesajlarda anormal hız değişikliklerini tespit eder
5. **BypassDetector**: Yetkisiz CAN komutlarını tespit eder
6. **BurstDetector**: Mesaj patlamalarını/sellerini tespit eder
7. **ConnectionFloodDetector**: WebSocket bağlantı sellerini tespit eder
8. **ValueDeltaDetector**: Anormal değer değişikliklerini tespit eder (hayalet ölçümler)
9. **FirmwareValidationDetector**: Firmware sürümlerini doğrular
10. **ReplayDetector**: Tekrar saldırılarını tespit eder

### `alerts.py`
Alarm ve loglama sistemi:
- **AlertLogger**: Alarm loglamasını ve istatistikleri yönetir
- **SecurityResponseHandler**: Güvenlik yanıtlarını işler (güvenli mod, engelleme)
- Alarm seviyeleri: INFO, WARNING, CRITICAL

### `ids_core.py`
Temel IDS motoru:
- **IDSCore**: CAN ve OCPP trafiğini izleyen ana IDS motoru
- Tüm dedektörleri entegre eder
- Otomatik güvenlik yanıtları

## Kullanım

### IDS'i Bağımsız Çalıştırma
```bash
python ids/ids_core.py
```

### IDS'i Kod İçinde Kullanma
```python
from ids.ids_core import IDSCore

# IDS'i başlat
ids = IDSCore('vcan0')
ids.start()

# IDS otomatik olarak CAN trafiğini izler

# OCPP mesajlarını işle
ids.process_ocpp_message("BootNotification", {
    "chargePointVendor": "Acme",
    "firmwareVersion": "v1.6-release"
})

# WebSocket bağlantılarını işle
ids.process_websocket_connection()

# IDS'i durdur
ids.stop()
```

### Tekil Dedektörleri Kullanma
```python
from ids.rules import FrequencySpikeDetector

detector = FrequencySpikeDetector(threshold_hz=20.0)

# Frekans sıçraması kontrolü
alert = detector.detect(can_id=0x9FF)
if alert:
    print(alert)
```

## Log Dosyaları

- `logs/ids_alerts.log`: Zaman damgalı tüm alarmlar
- `logs/ids_stats.json`: İstatistikler (toplam alarm, türe göre, seviyeye göre)

## Yapılandırma

Varsayılan eşik değerleri (özelleştirilebilir):
- Frekans sıçraması: 20 mesaj/s
- OCPP → CAN gecikmesi: 2 saniye
- Mesaj patlaması: 10 mesaj/saniye
- WebSocket seli: 10 bağlantı/5 saniye
- Tekrar tespiti: 3 kopya/60 saniye

## Güvenlik Yanıtları

Anomaliler tespit edildiğinde, IDS şunları yapabilir:
1. Alarmları dosyaya ve konsola loglar
2. CAN bus'a güvenli mod komutu gönderir (ID 0x001)
3. Bağlantıları engeller (simüle edilmiş)
4. İstatistikleri takip eder
