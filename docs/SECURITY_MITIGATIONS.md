# Güvenlik Önlemleri ve Anomali Engelleme Stratejileri

## İçindekiler
- [Genel Güvenlik Prensipleri](#genel-güvenlik-prensipleri)
- [Anomali Bazlı Önlemler](#anomali-bazlı-önlemler)
- [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
- [Uygulama Önerileri](#uygulama-önerileri)

---

## Genel Güvenlik Prensipleri

### 1. Savunma Katmanları (Defense in Depth)

```
┌─────────────────────────────────────┐
│  Katman 1: Fiziksel Güvenlik        │
├─────────────────────────────────────┤
│  Katman 2: Ağ Segmentasyonu         │
├─────────────────────────────────────┤
│  Katman 3: Kimlik Doğrulama (MFA)   │
├─────────────────────────────────────┤
│  Katman 4: Şifreleme (TLS/Crypto)   │
├─────────────────────────────────────┤
│  Katman 5: Saldırı Tespit (IDS)     │
├─────────────────────────────────────┤
│  Katman 6: Loglama ve İzleme        │
└─────────────────────────────────────┘
```

### 2. Zero-Trust Yaklaşımı

- **Hiçbir cihaza varsayılan olarak güvenme**
- Her mesajı doğrula
- En az yetki prensibi (Least Privilege)
- Sürekli izleme ve doğrulama

---

## Anomali Bazlı Önlemler

### Anomali 1: Frekans Sıçraması

**Saldırı**: CAN ID 0x9FF'de 100 msg/s

**Önleme Stratejileri**:

1. **Hız Sınırlama (Rate Limiting)**
   ```python
   # Her CAN ID için maksimum mesaj hızı tanımla
   RATE_LIMITS = {
       0x9FF: 10,  # maksimum 10 msg/s
       0x200: 5,   # maksimum 5 msg/s
   }
   ```

2. **Token Bucket Algoritması**
   - Her CAN ID için token bucket
   - Eşik aşıldığında mesajları reddet
   - Dinamik hız ayarlama

3. **CAN Gateway Filtreleme**
   - Kritik olmayan ID'leri filtrele
   - Whitelist tabanlı iletim
   - Öncelik tabanlı kuyruk yönetimi

**Uygulama**:
```python
class RateLimiter:
    def __init__(self, max_rate_hz):
        self.max_rate = max_rate_hz
        self.tokens = max_rate_hz
        self.last_update = time.time()
    
    def allow_message(self):
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.max_rate, self.tokens + elapsed * self.max_rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

---

### Anomali 2: OCPP → CAN Gecikmesi

**Saldırı**: RemoteStart sonrası 10s gecikme

**Önleme Stratejileri**:

1. **Timeout Mekanizması**
   ```python
   COMMAND_TIMEOUT = 2.0  # saniye
   
   # OCPP komutu geldiğinde zamanlayıcı başlat
   # CAN yanıtı gelmezse komutu iptal et
   ```

2. **Heartbeat Kontrolü**
   - Düzenli heartbeat mesajları
   - Yanıt süresini izle
   - Gecikme tespit edilirse alarm

3. **Watchdog Timer**
   - Kritik işlemler için watchdog
   - Zaman aşımında güvenli mod

**Uygulama**:
```python
class CommandTimeoutMonitor:
    def __init__(self, timeout=2.0):
        self.timeout = timeout
        self.pending_commands = {}
    
    def register_command(self, cmd_id, expected_can_id):
        self.pending_commands[cmd_id] = {
            'timestamp': time.time(),
            'expected_can_id': expected_can_id
        }
    
    def check_timeout(self):
        now = time.time()
        for cmd_id, info in list(self.pending_commands.items()):
            if now - info['timestamp'] > self.timeout:
                self.trigger_alarm(f"Timeout: {cmd_id}")
                del self.pending_commands[cmd_id]
```

---

### Anomali 3: Aralık Dışı Değer

**Saldırı**: 255A akım (max 80A)

**Önleme Stratejileri**:

1. **Payload Doğrulama**
   ```python
   VALID_RANGES = {
       'current': (0, 80),      # Ampere
       'voltage': (200, 250),   # Volt
       'power': (0, 22000),     # Watt
       'temperature': (-20, 80) # Celsius
   }
   ```

2. **Sınır Kontrolü (Bounds Checking)**
   - Her mesajda değer kontrolü
   - Aralık dışı değerleri reddet
   - Güvenli varsayılan değerler

3. **Fiziksel Limitler**
   - Donanım seviyesinde koruma
   - Akım kesiciler
   - Termal koruma

**Uygulama**:
```python
def validate_payload(parameter, value):
    if parameter not in VALID_RANGES:
        return False, "Unknown parameter"
    
    min_val, max_val = VALID_RANGES[parameter]
    if not (min_val <= value <= max_val):
        return False, f"Out of range: {value} (valid: {min_val}-{max_val})"
    
    return True, None
```

---

### Anomali 4: MeterValues Frekans İkiye Katlama

**Saldırı**: 1 Hz → 2 Hz

**Önleme Stratejileri**:

1. **Frekans İzleme**
   - Beklenen frekansı tanımla
   - Sapmaları tespit et
   - Adaptif eşik değerleri

2. **Mesaj Damgalama (Timestamping)**
   - Her mesaja zaman damgası
   - Ardışık mesajlar arası süre kontrolü
   - Anomali tespitinde kullan

3. **Veri Agregasyonu**
   - Fazla mesajları birleştir
   - Sunucuya tek mesaj gönder
   - Bant genişliği optimizasyonu

---

### Anomali 5: OCPP Bypass

**Saldırı**: OCPP olmadan direkt CAN komutu

**Önleme Stratejileri**:

1. **Yetkilendirme Kontrolü** ⭐
   ```python
   class AuthorizationManager:
       def __init__(self):
           self.authorized_commands = {}
       
       def authorize(self, can_id, ocpp_session_id):
           self.authorized_commands[can_id] = {
               'session': ocpp_session_id,
               'expiry': time.time() + 5.0
           }
       
       def is_authorized(self, can_id):
           if can_id not in self.authorized_commands:
               return False
           
           auth = self.authorized_commands[can_id]
           if time.time() > auth['expiry']:
               del self.authorized_commands[can_id]
               return False
           
           return True
   ```

2. **Session Management**
   - Her OCPP komutu için session ID
   - CAN mesajında session ID kontrolü
   - Session timeout mekanizması

3. **Command Sequencing**
   - Komutları sıralı numaralandır
   - Sıra dışı komutları reddet
   - Replay saldırılarını önle

---

### Anomali 6: Hata Patlaması

**Saldırı**: 50 hata mesajı/saniye

**Önleme Stratejileri**:

1. **Hata Mesajı Filtreleme**
   - Tekrarlayan hataları grupla
   - Belirli sürede maksimum hata sayısı
   - Fazla hataları bastır

2. **Backpressure Mekanizması**
   - Hata yükü fazlaysa yavaşlat
   - Kaynak tüketimini sınırla
   - Öncelikli mesaj işleme

3. **Circuit Breaker Pattern**
   ```python
   class CircuitBreaker:
       def __init__(self, threshold=10, timeout=60):
           self.threshold = threshold
           self.timeout = timeout
           self.failure_count = 0
           self.last_failure_time = 0
           self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
       
       def record_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()
           
           if self.failure_count >= self.threshold:
               self.state = 'OPEN'
               print("Circuit breaker OPEN - blocking traffic")
   ```

---

### Anomali 7: WebSocket Seli

**Saldırı**: 100 bağlantı/5 saniye

**Önleme Stratejileri**:

1. **Connection Rate Limiting**
   - IP bazlı bağlantı sınırı
   - Zaman penceresi içinde maksimum bağlantı
   - Geçici IP engelleme

2. **Connection Pooling**
   - Maksimum eşzamanlı bağlantı sayısı
   - Bağlantı kuyruğu
   - Timeout mekanizması

3. **IP Whitelist/Blacklist**
   ```python
   class ConnectionLimiter:
       def __init__(self, max_connections=10, window=5.0):
           self.max_connections = max_connections
           self.window = window
           self.connections = defaultdict(deque)
           self.blacklist = set()
       
       def allow_connection(self, ip):
           if ip in self.blacklist:
               return False
           
           now = time.time()
           # Eski bağlantıları temizle
           while self.connections[ip] and self.connections[ip][0] < now - self.window:
               self.connections[ip].popleft()
           
           if len(self.connections[ip]) >= self.max_connections:
               self.blacklist.add(ip)
               return False
           
           self.connections[ip].append(now)
           return True
   ```

---

### Anomali 8: Hayalet Ölçüm

**Saldırı**: 0 → 50 kWh ani sıçrama

**Önleme Stratejileri**:

1. **Delta Kontrolü**
   ```python
   MAX_ENERGY_DELTA = 5.0  # kWh/s
   
   def validate_energy_reading(current, previous, time_delta):
       delta_per_second = abs(current - previous) / time_delta
       return delta_per_second <= MAX_ENERGY_DELTA
   ```

2. **Kalman Filtresi**
   - Ölçüm değerlerini filtrele
   - Ani sıçramaları yumuşat
   - Gerçekçi değer tahmini

3. **Trend Analizi**
   - Geçmiş değerleri sakla
   - Trend çizgisi oluştur
   - Trend dışı değerleri reddet

---

### Anomali 9: Firmware Uyuşmazlığı

**Saldırı**: Yetkisiz "evil-v9" firmware

**Önleme Stratejileri**:

1. **Firmware Whitelist** ⭐
   ```python
   ALLOWED_FIRMWARE = [
       "v1.5-stable",
       "v1.6-release",
       "v2.0.1-prod"
   ]
   
   def validate_firmware(version):
       return version in ALLOWED_FIRMWARE
   ```

2. **Digital Signature Verification**
   - Firmware imzalama
   - Public key ile doğrulama
   - Güvenilir kaynak kontrolü

3. **Secure Boot**
   - Boot sırasında firmware doğrulama
   - İmzasız firmware çalıştırma
   - TPM/HSM entegrasyonu

---

### Anomali 10: Tekrar Saldırısı (Replay Attack)

**Saldırı**: Aynı mesajın 5 kez tekrarı

**Önleme Stratejileri**:

1. **Nonce/Sequence Number** ⭐
   ```python
   class ReplayProtection:
       def __init__(self, window_size=100):
           self.seen_nonces = deque(maxlen=window_size)
       
       def is_replay(self, nonce):
           if nonce in self.seen_nonces:
               return True
           self.seen_nonces.append(nonce)
           return False
   ```

2. **Timestamp Validation**
   - Her mesaja timestamp ekle
   - Eski mesajları reddet
   - Saat senkronizasyonu

3. **Message Authentication Code (MAC)**
   ```python
   import hmac
   import hashlib
   
   def create_mac(message, secret_key):
       return hmac.new(secret_key, message, hashlib.sha256).digest()
   
   def verify_mac(message, mac, secret_key):
       expected_mac = create_mac(message, secret_key)
       return hmac.compare_digest(mac, expected_mac)
   ```

---

## Multi-Factor Authentication (MFA)

### MFA Nedir?

Multi-Factor Authentication (Çok Faktörlü Kimlik Doğrulama), kullanıcının kimliğini doğrulamak için **iki veya daha fazla bağımsız faktör** kullanır:

1. **Bildiğiniz Bir Şey** (Knowledge): Şifre, PIN
2. **Sahip Olduğunuz Bir Şey** (Possession): Token, telefon, RFID kart
3. **Olduğunuz Bir Şey** (Inherence): Biyometrik (parmak izi, yüz tanıma)

### OCPP için MFA Uygulaması

#### 1. Admin/Yönetici Erişimi için MFA

**Senaryo**: CSMS (Central System) yönetim paneline erişim

```python
class MFAManager:
    def __init__(self):
        self.pending_auth = {}
        self.totp_secret = {}  # Time-based OTP secrets
    
    def initiate_login(self, username, password):
        # Adım 1: Kullanıcı adı ve şifre kontrolü
        if not self.verify_credentials(username, password):
            return False, "Invalid credentials"
        
        # Adım 2: OTP kodu gönder
        otp_code = self.generate_otp(username)
        self.send_otp_sms(username, otp_code)
        
        # Pending auth kaydet
        self.pending_auth[username] = {
            'otp': otp_code,
            'expiry': time.time() + 300  # 5 dakika
        }
        
        return True, "OTP sent"
    
    def verify_otp(self, username, otp_code):
        # Adım 3: OTP doğrulama
        if username not in self.pending_auth:
            return False
        
        auth = self.pending_auth[username]
        if time.time() > auth['expiry']:
            del self.pending_auth[username]
            return False
        
        if auth['otp'] == otp_code:
            del self.pending_auth[username]
            return True
        
        return False
    
    def generate_otp(self, username):
        # TOTP (Time-based OTP) üret
        import pyotp
        if username not in self.totp_secret:
            self.totp_secret[username] = pyotp.random_base32()
        
        totp = pyotp.TOTP(self.totp_secret[username])
        return totp.now()
```

#### 2. Şarj İstasyonu Kimlik Doğrulama

**Senaryo**: Kullanıcı şarj başlatmak istiyor

**Yöntem 1: RFID + PIN**
```python
class ChargingAuthenticator:
    def authenticate_user(self, rfid_tag, pin_code):
        # Faktör 1: RFID kartı (sahip olduğunuz)
        if not self.validate_rfid(rfid_tag):
            return False, "Invalid RFID"
        
        # Faktör 2: PIN kodu (bildiğiniz)
        if not self.validate_pin(rfid_tag, pin_code):
            return False, "Invalid PIN"
        
        return True, "Authenticated"
```

**Yöntem 2: Mobil App + Biometric**
```python
class MobileAuthenticator:
    def authenticate_user(self, user_id, biometric_token, device_id):
        # Faktör 1: Kayıtlı cihaz (sahip olduğunuz)
        if not self.validate_device(user_id, device_id):
            return False, "Unknown device"
        
        # Faktör 2: Biyometrik (olduğunuz)
        if not self.validate_biometric(user_id, biometric_token):
            return False, "Biometric failed"
        
        # Faktör 3: Session token (opsiyonel)
        session_token = self.create_session(user_id)
        return True, session_token
```

#### 3. OCPP 2.0.1 ile MFA Entegrasyonu

```python
class OCPP20MFAServer:
    def handle_boot_notification(self, charge_point_id, certificate):
        # Faktör 1: TLS Client Certificate
        if not self.verify_certificate(certificate):
            return {"status": "Rejected"}
        
        # Faktör 2: Charge Point ID doğrulama
        if not self.validate_charge_point_id(charge_point_id):
            return {"status": "Rejected"}
        
        # Faktör 3: Challenge-Response
        challenge = self.generate_challenge()
        self.pending_challenges[charge_point_id] = challenge
        
        return {
            "status": "Pending",
            "challenge": challenge
        }
    
    def handle_challenge_response(self, charge_point_id, response):
        expected = self.pending_challenges.get(charge_point_id)
        if not expected:
            return {"status": "Rejected"}
        
        if self.verify_challenge_response(expected, response):
            return {"status": "Accepted"}
        
        return {"status": "Rejected"}
```

### MFA Uygulama Önerileri

#### Seviye 1: Temel MFA (Minimum)
- ✅ Kullanıcı adı + Şifre
- ✅ SMS/Email OTP
- ✅ Session timeout

#### Seviye 2: Orta MFA (Önerilen)
- ✅ Kullanıcı adı + Güçlü şifre
- ✅ TOTP (Google Authenticator)
- ✅ Cihaz kaydı
- ✅ IP whitelist

#### Seviye 3: Gelişmiş MFA (Maksimum Güvenlik)
- ✅ TLS Client Certificate
- ✅ Hardware token (YubiKey)
- ✅ Biyometrik doğrulama
- ✅ Risk bazlı kimlik doğrulama
- ✅ Blockchain tabanlı doğrulama

### MFA Akış Diyagramı

```
┌─────────────┐
│   Kullanıcı │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ 1. Kullanıcı Adı +  │
│    Şifre Gir        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 2. Şifre Doğrula    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 3. OTP Kodu Gönder  │
│    (SMS/App)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 4. OTP Kodu Gir     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 5. OTP Doğrula      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 6. Erişim İzni Ver  │
└─────────────────────┘
```

---

## Uygulama Önerileri

### 1. Öncelik Sırası

**Kritik (Hemen Uygula)**:
1. ✅ Firmware whitelist (Anomali 9)
2. ✅ OCPP yetkilendirme kontrolü (Anomali 5)
3. ✅ Admin paneli için MFA
4. ✅ TLS/WSS şifreleme

**Yüksek (Kısa Vadede)**:
1. ✅ Hız sınırlama (Anomali 1, 6, 7)
2. ✅ Payload doğrulama (Anomali 3, 8)
3. ✅ Replay koruması (Anomali 10)

**Orta (Orta Vadede)**:
1. ✅ Timeout mekanizmaları (Anomali 2)
2. ✅ Frekans izleme (Anomali 4)
3. ✅ Gelişmiş loglama

### 2. Katmanlı Güvenlik Mimarisi

```
Internet
    │
    ▼
┌─────────────────┐
│   Firewall      │  ← IP filtering, DDoS protection
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load Balancer  │  ← Rate limiting, SSL termination
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCPP Server    │  ← MFA, TLS, Authentication
│  (with MFA)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gateway/IDS    │  ← Anomaly detection, Filtering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CAN Bus       │  ← Message validation, Encryption
└─────────────────┘
```

### 3. Güvenlik Kontrol Listesi

#### CAN Bus Güvenliği
- [ ] CAN mesaj frekans limitleri tanımlandı
- [ ] Payload doğrulama kuralları uygulandı
- [ ] CAN gateway filtreleme aktif
- [ ] Mesaj imzalama (MAC) kullanılıyor
- [ ] Replay koruması aktif

#### OCPP Güvenliği
- [ ] TLS 1.2+ kullanılıyor
- [ ] Client certificate doğrulama aktif
- [ ] Firmware whitelist tanımlı
- [ ] Session management uygulandı
- [ ] MFA admin erişimi için aktif

#### IDS Güvenliği
- [ ] Tüm 10 anomali dedektörü aktif
- [ ] Alarm eşikleri optimize edildi
- [ ] Otomatik güvenlik yanıtları tanımlı
- [ ] Log rotasyonu yapılandırıldı
- [ ] İstatistik takibi aktif

### 4. Düzenli Güvenlik Testleri

```bash
# Haftalık testler
python scripts/run_all_anomaly_tests.py

# Aylık penetrasyon testleri
python scripts/security_audit.py

# Çeyrek yıllık güvenlik değerlendirmesi
python scripts/comprehensive_security_check.py
```

---

## Sonuç

Güvenlik, **tek seferlik bir uygulama değil, sürekli bir süreçtir**. Bu dokümanda belirtilen önlemler:

✅ **Çok katmanlı savunma** sağlar  
✅ **Bilinen saldırıları** önler  
✅ **Sıfır güven** prensibini uygular  
✅ **MFA ile** kimlik doğrulama güçlendirir  
✅ **Sürekli izleme** ile proaktif koruma sağlar  

**Önemli**: Tüm güvenlik önlemlerini birlikte uygulamak en iyi sonucu verir!
