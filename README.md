🚀 CAN ↔ OCPP Anomali Tespit & Simülasyon Projesi
Eğitim, PoC, araştırma ve demo amaçlı olarak hazırlanmış; yalnızca yazılım tabanlı (vcan0 + OCPP/WebSocket) çalışan anomaly simulation & detection framework’ü.
Bu proje ile CAN trafiği, OCPP mesajları ve gateway davranışı üzerinde 10 kritik saldırı/anomali senaryosunu gerçek zamanlı olarak simüle edebilirve basit bir 
IDS (Intrusion Detection System) ile tespit edebilirsin.


📦 İçerik10 farklı CAN ↔ OCPP anomali senaryosuFrekans, içerik, korelasyon, replay ve delay tabanlı tespit kuralları.
Tamamen yazılım tabanlı laboratuvarIDS pseudo-codeSWOT analizi ve yapılabilir öneriler


🧩 Projenin AmacıBu proje, öğrenme ve PoC süreçlerinde aşağıdaki davranışları test etmek için hazırlanmıştır:
CAN → OCPP mesaj eşleşmeleriOCPP → CAN zamanlama analizleriReplay, delta jump, rate spike gibi anormalliklerWhitelist, HMAC, sequence, correlation gibi savunma yöntemleri


🔥 Simüle Edilen 10 Anomali
IDSenaryoAçıklama
0x9FF Frequency Spike Trafikte olmayan ID’nin aniden artması
2OCPP → CAN DelayRemoteStart → 0x200 arasındaki gecikme
Out-of-Range Payloadmax_current = 255 gibi uç değer
MeterValues Rate Doubling1 Hz olan trafiğin 2 Hz’e çıkması
OCPP Dışı StartCAN üzerinden izinsiz Start komutu
0x301 Error BurstÇok hızlı hata mesajı yağmuru
WebSocket FloodÇok sayıda yeni WS bağlantısı
Hayalet ÖlçümBir anda anormal ölçüm değişimi
Firmware MismatchWhitelist dışı firmwareVersion
Replay AttackAynı ID+payload tekrar tekrar geliyor


🛠️ Test Ortamı Gereksinimleri
Linux (Ubuntu önerilir)
vcan kernel modülü
can-utils (cansend, candump)
Python:
  python-can
  websockets
  ocpp
  
⚙️ vcan0 Kurulum
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
