# 🚀 CAN ↔ OCPP Anomali Tespiti ve Simülasyonu Projesi  
**Bir Yazılım Tabanlı Laboratuvar Çerçevesi**

Bu proje, **şarj istasyonu ağ geçitleri** (gateway) üzerinde **CAN ↔ OCPP** iletişimini hedefleyen siber tehditleri araştırmak, simüle etmek ve basit bir **Intrusion Detection System** (IDS) ile tespit etmek amacıyla geliştirilmiştir. Eğitim, kavram kanıtı (Proof of Concept), araştırma ve demo senaryoları için idealdir.

> ⚙️ **Tamamen yazılım tabanlıdır**: Gerçek donanım yerine `vcan0` sanal CAN arayüzü ve OCPP WebSocket bağlantısı kullanılır.

---

## 🎯 Projenin Amacı

Bu simülasyon çerçevesi, aşağıdaki güvenlik ve davranışsal analiz senaryolarını test etmek için tasarlanmıştır:

- **CAN ↔ OCPP mesaj eşleşmeleri** (ör. CAN ID → OCPP StartTransaction)  
- **Zamanlama analizleri** (OCPP komutundan CAN tepkisine kadar geçen süre)  
- **Anormal trafik davranışları**: Replay, delta sıçramaları, frekans patlamaları  
- **Savunma stratejileri**: Whitelist doğrulama, HMAC, mesaj sıralaması, korelasyon tabanlı kurallar  

---
![CAN-OCPP Gateway Mimarisi](assets/occp_can_gantt.png)
---


## 🔥 Simüle Edilen 10 Kritik Anomali Senaryosu

| ID | Senaryo                         | Açıklama |
|----|----------------------------------|---------|
| 1  | **Frequency Spike**             | Trafikte normalde görünmeyen bir CAN IDʼnin (ör. `0x9FF`) ani ve aşırı sıklıkta gönderilmesi |
| 2  | **OCPP → CAN Delay**            | `RemoteStartTransaction` sonrası `0x200` IDʼli CAN mesajının normalden çok daha geç gelmesi |
| 3  | **Out-of-Range Payload**        | `max_current = 255 A` gibi mantıksız/fiziksel olarak imkânsız değerlerin gönderilmesi |
| 4  | **MeterValues Rate Doubling**   | Normalde 1 Hz olan ölçüm mesajlarının aniden 2 Hzʼe çıkarılması |
| 5  | **OCPP Dışı Start**             | CAN hattı üzerinden doğrudan başlatma komutu gönderilmesi (OCPP onayı olmadan) |
| 6  | **Error Burst**                 | `0x301` hata mesajının çok kısa sürede tekrar tekrar gönderilmesi |
| 7  | **WebSocket Flood**             | Çok sayıda yeni OCPP WebSocket bağlantısının kısa sürede açılması |
| 8  | **Hayalet Ölçüm**               | `MeterValues` içinde anormal, ani enerji tüketimi sıçraması (ör. 0 → 50 kWh/saniye) |
| 9  | **Firmware Mismatch**           | Gateway’de tanımlı olmayan `firmwareVersion` ile OCPP mesajı gönderilmesi |
| 10 | **Replay Attack**               | Aynı CAN ID + payload kombinasyonunun tekrar tekrar gönderilmesi |

---

## 🛠️ Kurulum & Gereksinimler

### Sistem
- Linux (Ubuntu 20.04+/22.04 önerilir)
- `vcan` kernel modülü
- `can-utils` paketi

### Python Paketleri
```bash
pip install python-can websockets ocpp
```

### Ekip Üyeleri
230541102 Muhammet Enes AYDIN
230541146 Emre AŞKIN
230541074 Anıl Gökhan YILMAZ
230541120 Ömer Yiğit AVŞAR
230541052 Muhammed Fatih SALTAN




