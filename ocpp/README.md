# OCPP Mock Bileşenleri

Bu dizin, test için OCPP WebSocket sunucu ve istemci bileşenlerini içerir.

## Modüller

### `ocpp_messages.py`
OCPP mesaj şablonları ve oluşturucular:
- **OCPPMessageBuilder**: OCPP 1.6 JSON mesajları oluşturur
- Mesaj türleri: BootNotification, RemoteStartTransaction, MeterValues, vb.
- Mesajlar için doğrulama fonksiyonları

### `ocpp_server.py`
Mock OCPP Merkez Sistem sunucusu:
- **OCPPServer**: OCPP mesajlarını işleyen WebSocket sunucusu
- Firmware sürüm doğrulaması
- Bağlantı yönetimi
- Özelleştirilebilir mesaj işleyicileri

### `ocpp_client.py`
Mock OCPP Şarj İstasyonu istemcisi:
- **OCPPClient**: OCPP mesajları göndermek için WebSocket istemcisi
- Tüm mesaj türleri için yardımcı metodlar
- Async/await tabanlı

## Kullanım Örnekleri

### OCPP Sunucusunu Başlatma
```python
from ocpp.ocpp_server import OCPPServer

server = OCPPServer(host="localhost", port=9000)
server.run()  # Blocking
```

Veya doğrudan çalıştır:
```bash
python ocpp/ocpp_server.py
```

### OCPP İstemcisi Kullanımı
```python
import asyncio
from ocpp.ocpp_client import OCPPClient

async def main():
    client = OCPPClient("ws://localhost:9000")
    
    if await client.connect():
        # BootNotification gönder
        await client.send_boot_notification(
            charge_point_vendor="Acme",
            charge_point_model="Charger-100",
            firmware_version="v1.6-release"
        )
        
        # MeterValues gönder
        await client.send_meter_values(
            connector_id=1,
            energy_wh=1500,
            power_w=7400,
            current_a=32
        )
        
        await client.disconnect()

asyncio.run(main())
```

### Mesaj Oluşturma
```python
from ocpp.ocpp_messages import OCPPMessageBuilder

builder = OCPPMessageBuilder()

# BootNotification oluştur
boot_msg = builder.boot_notification(
    charge_point_vendor="TestVendor",
    charge_point_model="Model-X",
    firmware_version="v2.0.0"
)

# MeterValues oluştur
meter_msg = builder.meter_values(
    connector_id=1,
    energy_wh=2500,
    power_w=11000,
    current_a=48
)
```

## Varsayılan Yapılandırma

- **Sunucu Portu**: 9000
- **İzin Verilen Firmware Sürümleri**: 
  - v1.5-stable
  - v1.6-release
  - v2.0.1-prod

## Gereksinimler

- Python 3.7+
- `websockets` paketi: `pip install websockets`
