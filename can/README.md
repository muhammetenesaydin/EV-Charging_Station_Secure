# CAN Bus Araçları

Bu dizin, CAN bus iletişimi ve simülasyonu için araçlar içerir.

## Modüller

### `can_utils.py`
Temel CAN bus araçları:
- **CANInterface**: CAN bus bağlantılarını ve mesaj işlemlerini yönetir
- **CANMessageLogger**: CAN mesajlarını dosyaya ve konsola kaydeder
- **Yardımcı fonksiyonlar**: Hızlı mesaj gönderme ve formatlama

### `can_simulator.py`
CAN trafik simülatörü:
- **CANTrafficSimulator**: Gerçekçi arka plan CAN trafiği üretir
- Yapılandırılabilir trafik kalıpları
- Çok iş parçacıklı mesaj üretimi

## Kullanım Örnekleri

### CAN Mesajı Gönderme
```python
from can.can_utils import send_can_message

# Basit bir mesaj gönder
send_can_message(0x123, [0x01, 0x02, 0x03, 0x04])
```

### CANInterface Kullanımı
```python
from can.can_utils import CANInterface

can_if = CANInterface('vcan0')
if can_if.connect():
    # Mesaj gönder
    can_if.send_message(0x200, [0x01, 0x00, 0x00, 0x00])
    
    # Mesajları dinle
    can_if.listen(
        callback=lambda msg: print(f"Alındı: {msg}"),
        duration=10.0
    )
    
    can_if.disconnect()
```

### Arka Plan Trafiği Üretme
```python
from can.can_simulator import CANTrafficSimulator

simulator = CANTrafficSimulator('vcan0')
simulator.start()

# Trafik arka planda çalışıyor...
time.sleep(60)

simulator.stop()
```

## Gereksinimler

- CAN desteği olan Linux sistemi
- Yapılandırılmış `vcan0` arayüzü
- Kurulu `python-can` paketi

## vcan0 Kurulumu

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

Doğrulama:
```bash
ip link show vcan0
```
