"""
TOTP (Time-based One-Time Password) Generator

Google Authenticator uyumlu OTP üreteci
"""

import time
import hmac
import hashlib
import base64
import secrets
from typing import Optional


class TOTPGenerator:
    """Time-based One-Time Password üreteci"""
    
    def __init__(self, secret: Optional[str] = None, interval: int = 30, digits: int = 6):
        """
        Args:
            secret: Base32 encoded secret key (None ise otomatik üret)
            interval: OTP geçerlilik süresi (saniye)
            digits: OTP hanesi (6 veya 8)
        """
        self.secret = secret or self._generate_secret()
        self.interval = interval
        self.digits = digits
    
    @staticmethod
    def _generate_secret(length: int = 32) -> str:
        """
        Rastgele Base32 secret üret
        
        Args:
            length: Secret uzunluğu (byte)
        
        Returns:
            Base32 encoded secret
        """
        random_bytes = secrets.token_bytes(length)
        return base64.b32encode(random_bytes).decode('utf-8')
    
    def _get_counter(self, timestamp: Optional[float] = None) -> int:
        """
        Zaman bazlı counter hesapla
        
        Args:
            timestamp: Unix timestamp (None ise şimdiki zaman)
        
        Returns:
            Counter değeri
        """
        if timestamp is None:
            timestamp = time.time()
        return int(timestamp // self.interval)
    
    def _generate_hotp(self, counter: int) -> str:
        """
        HMAC-based OTP üret
        
        Args:
            counter: Counter değeri
        
        Returns:
            OTP kodu
        """
        # Secret'ı decode et
        key = base64.b32decode(self.secret, casefold=True)
        
        # Counter'ı 8 byte'a çevir
        msg = counter.to_bytes(8, byteorder='big')
        
        # HMAC-SHA1 hesapla
        hmac_hash = hmac.new(key, msg, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code = int.from_bytes(hmac_hash[offset:offset+4], byteorder='big') & 0x7FFFFFFF
        
        # Belirtilen hane sayısına göre formatla
        otp = str(code % (10 ** self.digits)).zfill(self.digits)
        return otp
    
    def generate(self, timestamp: Optional[float] = None) -> str:
        """
        OTP kodu üret
        
        Args:
            timestamp: Unix timestamp (None ise şimdiki zaman)
        
        Returns:
            OTP kodu
        """
        counter = self._get_counter(timestamp)
        return self._generate_hotp(counter)
    
    def verify(self, otp: str, timestamp: Optional[float] = None, window: int = 1) -> bool:
        """
        OTP kodunu doğrula
        
        Args:
            otp: Kullanıcıdan gelen OTP
            timestamp: Unix timestamp (None ise şimdiki zaman)
            window: Zaman penceresi (±window interval)
        
        Returns:
            True ise geçerli
        """
        current_counter = self._get_counter(timestamp)
        
        # Zaman penceresi içinde kontrol et
        for i in range(-window, window + 1):
            counter = current_counter + i
            expected_otp = self._generate_hotp(counter)
            
            # Timing attack'a karşı constant-time comparison
            if hmac.compare_digest(otp, expected_otp):
                return True
        
        return False
    
    def get_provisioning_uri(self, account_name: str, issuer_name: str = "EV Charging MFA") -> str:
        """
        Google Authenticator için provisioning URI üret
        
        Args:
            account_name: Hesap adı (username veya email)
            issuer_name: Uygulama adı
        
        Returns:
            otpauth:// URI
        """
        from urllib.parse import quote
        
        uri = f"otpauth://totp/{quote(issuer_name)}:{quote(account_name)}?"
        uri += f"secret={self.secret}&"
        uri += f"issuer={quote(issuer_name)}&"
        uri += f"algorithm=SHA1&"
        uri += f"digits={self.digits}&"
        uri += f"period={self.interval}"
        
        return uri
    
    def get_remaining_seconds(self, timestamp: Optional[float] = None) -> int:
        """
        Mevcut OTP'nin kalan geçerlilik süresi
        
        Args:
            timestamp: Unix timestamp (None ise şimdiki zaman)
        
        Returns:
            Kalan saniye
        """
        if timestamp is None:
            timestamp = time.time()
        return self.interval - int(timestamp % self.interval)


# Test kodu
if __name__ == "__main__":
    print("=== TOTP Generator Test ===\n")
    
    # TOTP üret
    totp = TOTPGenerator()
    print(f"Secret: {totp.secret}")
    print(f"Interval: {totp.interval}s")
    print(f"Digits: {totp.digits}\n")
    
    # OTP üret
    otp = totp.generate()
    print(f"Current OTP: {otp}")
    print(f"Remaining: {totp.get_remaining_seconds()}s\n")
    
    # Doğrula
    is_valid = totp.verify(otp)
    print(f"Verification: {'✅ Valid' if is_valid else '❌ Invalid'}\n")
    
    # Provisioning URI
    uri = totp.get_provisioning_uri("admin@example.com")
    print(f"Provisioning URI:\n{uri}")
