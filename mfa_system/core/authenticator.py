"""
Multi-Factor Authenticator

Kullanıcı kaydı, login, OTP doğrulama
"""

import time
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from .totp import TOTPGenerator
from .session import SessionManager


class MFAAuthenticator:
    """Multi-Factor Authentication yöneticisi"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.session_manager = SessionManager()
        self.login_attempts: Dict[str, list] = {}  # Brute force koruması
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 dakika
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi hashle (SHA-256)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _is_locked_out(self, username: str) -> bool:
        """Kullanıcı kilitli mi kontrol et"""
        if username not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[username]
        if len(attempts) < self.max_attempts:
            return False
        
        # Son denemeden bu yana geçen süre
        last_attempt = attempts[-1]
        if time.time() - last_attempt > self.lockout_duration:
            # Kilidi kaldır
            self.login_attempts[username] = []
            return False
        
        return True
    
    def _record_failed_attempt(self, username: str):
        """Başarısız denemeyi kaydet"""
        if username not in self.login_attempts:
            self.login_attempts[username] = []
        
        self.login_attempts[username].append(time.time())
        
        # Eski denemeleri temizle
        cutoff = time.time() - self.lockout_duration
        self.login_attempts[username] = [
            t for t in self.login_attempts[username] if t > cutoff
        ]
    
    def register_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Yeni kullanıcı kaydet
        
        Args:
            username: Kullanıcı adı
            password: Şifre
            email: Email (opsiyonel)
        
        Returns:
            (success, message, totp_secret)
        """
        # Kullanıcı zaten var mı?
        if username in self.users:
            return False, "Username already exists", None
        
        # Şifre kontrolü
        if len(password) < 8:
            return False, "Password must be at least 8 characters", None
        
        # TOTP secret üret
        totp = TOTPGenerator()
        
        # Kullanıcıyı kaydet
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'totp_secret': totp.secret,
            'email': email,
            'created_at': time.time(),
            'last_login': None,
            'login_count': 0
        }
        
        return True, "User registered successfully", totp.secret
    
    def initiate_login(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Login başlat (Faktör 1: Şifre)
        
        Args:
            username: Kullanıcı adı
            password: Şifre
        
        Returns:
            (success, message, session_id)
        """
        # Kullanıcı kilitli mi?
        if self._is_locked_out(username):
            remaining = self.lockout_duration - (time.time() - self.login_attempts[username][-1])
            return False, f"Account locked. Try again in {int(remaining)}s", None
        
        # Kullanıcı var mı?
        if username not in self.users:
            self._record_failed_attempt(username)
            return False, "Invalid credentials", None
        
        user = self.users[username]
        password_hash = self._hash_password(password)
        
        # Şifre doğru mu?
        if not secrets.compare_digest(user['password_hash'], password_hash):
            self._record_failed_attempt(username)
            return False, "Invalid credentials", None
        
        # Session oluştur (pending)
        session_id = self.session_manager.create_pending_session(
            username=username,
            timeout=300  # 5 dakika
        )
        
        return True, "Password verified. Enter OTP code.", session_id
    
    def verify_otp(
        self,
        session_id: str,
        otp_code: str
    ) -> Tuple[bool, str]:
        """
        OTP kodunu doğrula (Faktör 2: TOTP)
        
        Args:
            session_id: Session ID
            otp_code: OTP kodu
        
        Returns:
            (success, message)
        """
        # Pending session var mı?
        username = self.session_manager.get_pending_username(session_id)
        if not username:
            return False, "Invalid or expired session"
        
        # Kullanıcı bilgilerini al
        user = self.users[username]
        
        # TOTP doğrula
        totp = TOTPGenerator(secret=user['totp_secret'])
        if not totp.verify(otp_code, window=1):
            return False, "Invalid OTP code"
        
        # Pending session'ı aktif session'a çevir
        if not self.session_manager.activate_session(session_id, username):
            return False, "Failed to create session"
        
        # Kullanıcı istatistiklerini güncelle
        user['last_login'] = time.time()
        user['login_count'] += 1
        
        # Başarısız denemeleri temizle
        if username in self.login_attempts:
            self.login_attempts[username] = []
        
        return True, "Authentication successful"
    
    def verify_session(
        self,
        session_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Session geçerliliğini kontrol et
        
        Args:
            session_id: Session ID
        
        Returns:
            (is_valid, username)
        """
        return self.session_manager.verify_session(session_id)
    
    def logout(self, session_id: str) -> bool:
        """
        Session sonlandır
        
        Args:
            session_id: Session ID
        
        Returns:
            True ise başarılı
        """
        return self.session_manager.end_session(session_id)
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Kullanıcı bilgilerini al (şifre hariç)
        
        Args:
            username: Kullanıcı adı
        
        Returns:
            Kullanıcı bilgileri veya None
        """
        if username not in self.users:
            return None
        
        user = self.users[username].copy()
        user.pop('password_hash', None)
        user.pop('totp_secret', None)
        
        return user
    
    def get_totp_provisioning_uri(
        self,
        username: str,
        issuer: str = "EV Charging MFA"
    ) -> Optional[str]:
        """
        Google Authenticator için QR kod URI'si
        
        Args:
            username: Kullanıcı adı
            issuer: Uygulama adı
        
        Returns:
            Provisioning URI veya None
        """
        if username not in self.users:
            return None
        
        user = self.users[username]
        totp = TOTPGenerator(secret=user['totp_secret'])
        
        return totp.get_provisioning_uri(username, issuer)


# Test kodu
if __name__ == "__main__":
    print("=== MFA Authenticator Test ===\n")
    
    mfa = MFAAuthenticator()
    
    # Kullanıcı kaydet
    success, msg, secret = mfa.register_user("admin", "SecurePass123!")
    print(f"Register: {msg}")
    print(f"TOTP Secret: {secret}\n")
    
    # Login başlat
    success, msg, session_id = mfa.initiate_login("admin", "SecurePass123!")
    print(f"Login: {msg}")
    print(f"Session ID: {session_id}\n")
    
    if success:
        # OTP üret ve doğrula
        totp = TOTPGenerator(secret=secret)
        otp = totp.generate()
        print(f"OTP Code: {otp}")
        
        success, msg = mfa.verify_otp(session_id, otp)
        print(f"OTP Verify: {msg}\n")
        
        if success:
            # Session kontrol
            is_valid, username = mfa.verify_session(session_id)
            print(f"Session Valid: {is_valid} ({username})")
