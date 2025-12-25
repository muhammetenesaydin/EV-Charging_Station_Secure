"""
Multi-Factor Authentication (MFA) Implementation

OCPP sunucusu için MFA desteği ekler
"""

import time
import hmac
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from datetime import datetime


class TOTPGenerator:
    """Time-based One-Time Password üreteci"""
    
    def __init__(self, secret: str = None, interval: int = 30):
        """
        Args:
            secret: Base32 encoded secret key
            interval: OTP geçerlilik süresi (saniye)
        """
        self.secret = secret or self._generate_secret()
        self.interval = interval
    
    def _generate_secret(self) -> str:
        """Rastgele secret key üret"""
        return secrets.token_hex(20)
    
    def generate_otp(self) -> str:
        """6 haneli OTP kodu üret"""
        counter = int(time.time() // self.interval)
        
        # HMAC-SHA1 hesapla
        key = bytes.fromhex(self.secret)
        msg = counter.to_bytes(8, byteorder='big')
        hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code = int.from_bytes(hmac_hash[offset:offset+4], byteorder='big') & 0x7FFFFFFF
        
        # 6 haneli kod
        otp = str(code % 1000000).zfill(6)
        return otp
    
    def verify_otp(self, otp: str, window: int = 1) -> bool:
        """
        OTP kodunu doğrula
        
        Args:
            otp: Kullanıcıdan gelen OTP
            window: Zaman penceresi (±window interval)
        """
        current_counter = int(time.time() // self.interval)
        
        for i in range(-window, window + 1):
            counter = current_counter + i
            
            # Bu counter için OTP hesapla
            key = bytes.fromhex(self.secret)
            msg = counter.to_bytes(8, byteorder='big')
            hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
            
            offset = hmac_hash[-1] & 0x0F
            code = int.from_bytes(hmac_hash[offset:offset+4], byteorder='big') & 0x7FFFFFFF
            expected_otp = str(code % 1000000).zfill(6)
            
            if hmac.compare_digest(otp, expected_otp):
                return True
        
        return False


class MFAAuthenticator:
    """Multi-Factor Authentication yöneticisi"""
    
    def __init__(self):
        self.users = {}  # username: {password_hash, totp_secret, devices}
        self.pending_auth = {}  # session_id: {username, stage, expiry}
        self.sessions = {}  # session_id: {username, created, last_activity}
    
    def register_user(self, username: str, password: str) -> str:
        """
        Yeni kullanıcı kaydet ve TOTP secret döndür
        
        Returns:
            TOTP secret (QR kod için kullanılabilir)
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        totp = TOTPGenerator()
        
        self.users[username] = {
            'password_hash': password_hash,
            'totp_secret': totp.secret,
            'devices': [],
            'created': time.time()
        }
        
        return totp.secret
    
    def initiate_login(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Login başlat (Faktör 1: Şifre)
        
        Returns:
            (success, message, session_id)
        """
        if username not in self.users:
            return False, "Invalid credentials", None
        
        user = self.users[username]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if not hmac.compare_digest(user['password_hash'], password_hash):
            return False, "Invalid credentials", None
        
        # Session oluştur
        session_id = secrets.token_urlsafe(32)
        self.pending_auth[session_id] = {
            'username': username,
            'stage': 'password_verified',
            'expiry': time.time() + 300  # 5 dakika
        }
        
        return True, "Password verified. Enter OTP code.", session_id
    
    def verify_otp(self, session_id: str, otp_code: str) -> Tuple[bool, str]:
        """
        OTP kodunu doğrula (Faktör 2: TOTP)
        
        Returns:
            (success, message)
        """
        if session_id not in self.pending_auth:
            return False, "Invalid or expired session"
        
        auth = self.pending_auth[session_id]
        
        # Timeout kontrolü
        if time.time() > auth['expiry']:
            del self.pending_auth[session_id]
            return False, "Session expired"
        
        # OTP doğrula
        username = auth['username']
        user = self.users[username]
        totp = TOTPGenerator(secret=user['totp_secret'])
        
        if not totp.verify_otp(otp_code):
            return False, "Invalid OTP code"
        
        # Session oluştur
        self.sessions[session_id] = {
            'username': username,
            'created': time.time(),
            'last_activity': time.time()
        }
        
        # Pending auth temizle
        del self.pending_auth[session_id]
        
        return True, "Authentication successful"
    
    def verify_session(self, session_id: str, max_idle: int = 3600) -> Tuple[bool, Optional[str]]:
        """
        Session geçerliliğini kontrol et
        
        Args:
            session_id: Session ID
            max_idle: Maksimum idle süresi (saniye)
        
        Returns:
            (is_valid, username)
        """
        if session_id not in self.sessions:
            return False, None
        
        session = self.sessions[session_id]
        
        # Idle timeout kontrolü
        if time.time() - session['last_activity'] > max_idle:
            del self.sessions[session_id]
            return False, None
        
        # Activity güncelle
        session['last_activity'] = time.time()
        
        return True, session['username']
    
    def logout(self, session_id: str):
        """Session sonlandır"""
        if session_id in self.sessions:
            del self.sessions[session_id]


class DeviceAuthenticator:
    """Cihaz bazlı kimlik doğrulama (Faktör 3)"""
    
    def __init__(self):
        self.registered_devices = {}  # username: [device_ids]
        self.device_fingerprints = {}  # device_id: fingerprint
    
    def register_device(self, username: str, device_id: str, fingerprint: Dict):
        """Cihaz kaydet"""
        if username not in self.registered_devices:
            self.registered_devices[username] = []
        
        self.registered_devices[username].append(device_id)
        self.device_fingerprints[device_id] = {
            'fingerprint': fingerprint,
            'registered': time.time(),
            'last_seen': time.time()
        }
    
    def verify_device(self, username: str, device_id: str, fingerprint: Dict) -> bool:
        """Cihazı doğrula"""
        if username not in self.registered_devices:
            return False
        
        if device_id not in self.registered_devices[username]:
            return False
        
        if device_id not in self.device_fingerprints:
            return False
        
        stored = self.device_fingerprints[device_id]['fingerprint']
        
        # Fingerprint karşılaştır (basit örnek)
        if stored.get('user_agent') != fingerprint.get('user_agent'):
            return False
        
        # Last seen güncelle
        self.device_fingerprints[device_id]['last_seen'] = time.time()
        
        return True


# Örnek kullanım
if __name__ == "__main__":
    print("=== MFA Authenticator Demo ===\n")
    
    # MFA sistemi oluştur
    mfa = MFAAuthenticator()
    
    # Kullanıcı kaydet
    username = "admin"
    password = "SecurePass123!"
    totp_secret = mfa.register_user(username, password)
    print(f"✅ Kullanıcı kaydedildi: {username}")
    print(f"📱 TOTP Secret: {totp_secret}")
    print(f"   (Bu secret'ı Google Authenticator'a ekleyin)\n")
    
    # Login denemesi
    print("🔐 Login başlatılıyor...")
    success, message, session_id = mfa.initiate_login(username, password)
    print(f"   {message}")
    
    if success:
        # OTP üret ve doğrula
        totp = TOTPGenerator(secret=totp_secret)
        otp_code = totp.generate_otp()
        print(f"📲 OTP Kodu: {otp_code}\n")
        
        print("🔑 OTP doğrulanıyor...")
        success, message = mfa.verify_otp(session_id, otp_code)
        print(f"   {message}")
        
        if success:
            print(f"✅ Session ID: {session_id[:16]}...\n")
            
            # Session doğrula
            is_valid, user = mfa.verify_session(session_id)
            if is_valid:
                print(f"✅ Session geçerli: {user}")
            
            # Logout
            mfa.logout(session_id)
            print("👋 Logout yapıldı")
