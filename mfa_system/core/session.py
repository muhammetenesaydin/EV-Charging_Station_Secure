"""
Session Manager

Güvenli session yönetimi
"""

import time
import secrets
from typing import Dict, Optional, Tuple


class SessionManager:
    """Session yönetim sistemi"""
    
    def __init__(self, default_timeout: int = 3600):
        """
        Args:
            default_timeout: Varsayılan session timeout (saniye)
        """
        self.default_timeout = default_timeout
        self.pending_sessions: Dict[str, Dict] = {}  # Henüz OTP doğrulanmamış
        self.active_sessions: Dict[str, Dict] = {}   # Aktif sessionlar
    
    def create_pending_session(
        self,
        username: str,
        timeout: Optional[int] = None
    ) -> str:
        """
        Pending session oluştur (OTP bekliyor)
        
        Args:
            username: Kullanıcı adı
            timeout: Session timeout (None ise varsayılan)
        
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        
        self.pending_sessions[session_id] = {
            'username': username,
            'created_at': time.time(),
            'expires_at': time.time() + (timeout or self.default_timeout)
        }
        
        return session_id
    
    def get_pending_username(self, session_id: str) -> Optional[str]:
        """
        Pending session'dan kullanıcı adını al
        
        Args:
            session_id: Session ID
        
        Returns:
            Kullanıcı adı veya None
        """
        if session_id not in self.pending_sessions:
            return None
        
        session = self.pending_sessions[session_id]
        
        # Timeout kontrolü
        if time.time() > session['expires_at']:
            del self.pending_sessions[session_id]
            return None
        
        return session['username']
    
    def activate_session(
        self,
        session_id: str,
        username: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Pending session'ı aktif session'a çevir
        
        Args:
            session_id: Session ID
            username: Kullanıcı adı
            timeout: Session timeout (None ise varsayılan)
        
        Returns:
            True ise başarılı
        """
        # Pending session'ı kaldır
        if session_id in self.pending_sessions:
            del self.pending_sessions[session_id]
        
        # Aktif session oluştur
        self.active_sessions[session_id] = {
            'username': username,
            'created_at': time.time(),
            'last_activity': time.time(),
            'expires_at': time.time() + (timeout or self.default_timeout)
        }
        
        return True
    
    def verify_session(
        self,
        session_id: str,
        update_activity: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Session geçerliliğini kontrol et
        
        Args:
            session_id: Session ID
            update_activity: Son aktivite zamanını güncelle
        
        Returns:
            (is_valid, username)
        """
        if session_id not in self.active_sessions:
            return False, None
        
        session = self.active_sessions[session_id]
        
        # Timeout kontrolü
        if time.time() > session['expires_at']:
            del self.active_sessions[session_id]
            return False, None
        
        # Son aktiviteyi güncelle
        if update_activity:
            session['last_activity'] = time.time()
        
        return True, session['username']
    
    def extend_session(
        self,
        session_id: str,
        additional_seconds: int
    ) -> bool:
        """
        Session süresini uzat
        
        Args:
            session_id: Session ID
            additional_seconds: Eklenecek saniye
        
        Returns:
            True ise başarılı
        """
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session['expires_at'] += additional_seconds
        
        return True
    
    def end_session(self, session_id: str) -> bool:
        """
        Session sonlandır
        
        Args:
            session_id: Session ID
        
        Returns:
            True ise başarılı
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        
        if session_id in self.pending_sessions:
            del self.pending_sessions[session_id]
            return True
        
        return False
    
    def cleanup_expired_sessions(self):
        """Süresi dolmuş sessionları temizle"""
        now = time.time()
        
        # Pending sessions
        expired_pending = [
            sid for sid, session in self.pending_sessions.items()
            if now > session['expires_at']
        ]
        for sid in expired_pending:
            del self.pending_sessions[sid]
        
        # Active sessions
        expired_active = [
            sid for sid, session in self.active_sessions.items()
            if now > session['expires_at']
        ]
        for sid in expired_active:
            del self.active_sessions[sid]
        
        return len(expired_pending) + len(expired_active)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Session bilgilerini al
        
        Args:
            session_id: Session ID
        
        Returns:
            Session bilgileri veya None
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id].copy()
            session['status'] = 'active'
            session['remaining_seconds'] = int(session['expires_at'] - time.time())
            return session
        
        if session_id in self.pending_sessions:
            session = self.pending_sessions[session_id].copy()
            session['status'] = 'pending'
            session['remaining_seconds'] = int(session['expires_at'] - time.time())
            return session
        
        return None
    
    def get_active_session_count(self) -> int:
        """Aktif session sayısı"""
        return len(self.active_sessions)
    
    def get_pending_session_count(self) -> int:
        """Pending session sayısı"""
        return len(self.pending_sessions)


# Test kodu
if __name__ == "__main__":
    print("=== Session Manager Test ===\n")
    
    sm = SessionManager(default_timeout=60)
    
    # Pending session oluştur
    session_id = sm.create_pending_session("admin", timeout=300)
    print(f"Pending Session: {session_id[:16]}...")
    
    # Username al
    username = sm.get_pending_username(session_id)
    print(f"Username: {username}")
    
    # Aktif session'a çevir
    sm.activate_session(session_id, username)
    print(f"Session activated")
    
    # Doğrula
    is_valid, user = sm.verify_session(session_id)
    print(f"Valid: {is_valid} ({user})")
    
    # Session bilgisi
    info = sm.get_session_info(session_id)
    print(f"Info: {info}")
