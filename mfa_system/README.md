# Multi-Factor Authentication (MFA) Demo Sistemi

Elektrikli Araç Şarj İstasyonları için profesyonel MFA uygulaması.

## 🎯 Özellikler

- ✅ **TOTP (Time-based OTP)** - Google Authenticator uyumlu
- ✅ **QR Kod Üretimi** - Kolay kurulum
- ✅ **Session Yönetimi** - Güvenli oturum kontrolü
- ✅ **Cihaz Kaydı** - 3. faktör doğrulama
- ✅ **Web Arayüzü** - Görsel demo
- ✅ **CLI Arayüzü** - Komut satırı kullanımı

## 📦 Kurulum

```bash
# MFA dizinine git
cd mfa_system

# Bağımlılıkları kur
pip install -r requirements.txt
```

## 🚀 Kullanım

### 1. Komut Satırı Demo

```bash
python cli_demo.py
```

**Çıktı:**
```
=== MFA Sistemi Demo ===

✅ Kullanıcı kaydedildi: admin
📱 TOTP Secret: 3JQXG5DJNFZWK4TFMFZXG2LTMVZQ====
   QR Kod: qr_codes/admin_qr.png

🔐 Login başlatılıyor...
   Password verified. Enter OTP code.
📲 OTP Kodu: 123456

🔑 OTP doğrulanıyor...
   Authentication successful
✅ Session ID: abc123...
```

### 2. Web Arayüzü

```bash
python web_demo.py
```

Tarayıcıda açın: `http://localhost:8080`

**Özellikler:**
- Kullanıcı kaydı
- QR kod gösterimi
- Login formu
- OTP doğrulama
- Dashboard

### 3. OCPP Entegrasyonu

```bash
python ocpp_mfa_server.py
```

OCPP sunucusu MFA ile korunur.

## 📁 Dosya Yapısı

```
mfa_system/
├── README.md              # Bu dosya
├── requirements.txt       # Python bağımlılıkları
├── core/                  # Temel MFA modülleri
│   ├── __init__.py
│   ├── totp.py           # TOTP üreteci
│   ├── authenticator.py  # MFA yöneticisi
│   └── session.py        # Session yönetimi
├── cli_demo.py           # Komut satırı demo
├── web_demo.py           # Web arayüzü
├── ocpp_mfa_server.py    # OCPP + MFA sunucusu
├── templates/            # HTML şablonları
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/               # CSS, JS dosyaları
│   └── style.css
└── qr_codes/            # Üretilen QR kodları
```

## 🔐 Güvenlik Özellikleri

### 3 Faktörlü Doğrulama

1. **Bildiğiniz Bir Şey**: Kullanıcı adı + Şifre
2. **Sahip Olduğunuz Bir Şey**: TOTP (Google Authenticator)
3. **Kayıtlı Cihaz**: Device fingerprint

### Ek Güvenlik

- ✅ SHA-256 şifre hashleme
- ✅ HMAC-based OTP
- ✅ Session timeout (1 saat)
- ✅ Brute force koruması
- ✅ Rate limiting

## 📱 Google Authenticator Kurulumu

1. Google Authenticator uygulamasını indirin
2. Kayıt sırasında gösterilen QR kodu tarayın
3. Uygulamada 6 haneli kod görünecek
4. Bu kodu login sırasında girin

## 🧪 Test Senaryoları

### Senaryo 1: Başarılı Login
```bash
python test_scenarios.py --scenario success
```

### Senaryo 2: Yanlış OTP
```bash
python test_scenarios.py --scenario wrong_otp
```

### Senaryo 3: Session Timeout
```bash
python test_scenarios.py --scenario timeout
```

## 📊 API Kullanımı

```python
from core.authenticator import MFAAuthenticator

# MFA sistemi oluştur
mfa = MFAAuthenticator()

# Kullanıcı kaydet
secret = mfa.register_user("admin", "SecurePass123!")

# Login başlat
success, msg, session_id = mfa.initiate_login("admin", "SecurePass123!")

# OTP doğrula
success, msg = mfa.verify_otp(session_id, "123456")

# Session kontrol
is_valid, username = mfa.verify_session(session_id)
```

## 🔗 OCPP Entegrasyonu

MFA sistemi OCPP sunucusu ile entegre edilebilir:

```python
from ocpp_mfa_server import OCPPMFAServer

# MFA korumalı OCPP sunucusu
server = OCPPMFAServer(host="0.0.0.0", port=9000)
server.run()
```

**Özellikler:**
- Her şarj istasyonu için benzersiz credentials
- TLS certificate + TOTP
- Session bazlı yetkilendirme

## 📈 Performans

- **OTP Üretimi**: ~0.001s
- **OTP Doğrulama**: ~0.002s
- **Session Kontrolü**: ~0.0001s
- **QR Kod Üretimi**: ~0.1s

## 🛡️ Güvenlik Tavsiyeleri

1. ✅ TOTP secret'ları güvenli sakla (encrypted database)
2. ✅ HTTPS kullan (production'da)
3. ✅ Rate limiting uygula
4. ✅ Session timeout'ları ayarla
5. ✅ Düzenli güvenlik auditleri yap

## 📝 Lisans

Bu MFA sistemi eğitim amaçlıdır. Production kullanımı için ek güvenlik önlemleri alın.

## 🤝 Katkıda Bulunma

Öneriler ve iyileştirmeler için pull request gönderin!

---

**Not**: Bu sistem, EV-Charging_Station_Secure projesinin bir parçasıdır ancak bağımsız olarak da kullanılabilir.
