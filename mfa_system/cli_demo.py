#!/usr/bin/env python3
"""
MFA System - CLI Demo

Komut satırı üzerinden MFA sistemini test edin
"""

import sys
import os
import time

# Core modülleri import et
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.totp import TOTPGenerator
from core.authenticator import MFAAuthenticator

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("⚠️  qrcode paketi yüklü değil. QR kod üretilemeyecek.")
    print("   Yüklemek için: pip install qrcode[pil]\n")


def generate_qr_code(uri: str, filename: str):
    """QR kod üret ve kaydet"""
    if not QR_AVAILABLE:
        return False
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # qr_codes dizinini oluştur
        os.makedirs("qr_codes", exist_ok=True)
        filepath = os.path.join("qr_codes", filename)
        img.save(filepath)
        
        return True
    except Exception as e:
        print(f"QR kod hatası: {e}")
        return False


def print_banner():
    """Banner yazdır"""
    print("\n" + "="*60)
    print("   🔐 MULTI-FACTOR AUTHENTICATION DEMO")
    print("   EV Charging Station Security System")
    print("="*60 + "\n")


def demo_registration():
    """Kullanıcı kaydı demosu"""
    print("📝 KULLANICI KAYDI\n")
    
    mfa = MFAAuthenticator()
    
    # Kullanıcı bilgileri
    username = input("Kullanıcı adı: ").strip() or "admin"
    password = input("Şifre (min 8 karakter): ").strip() or "SecurePass123!"
    email = input("Email (opsiyonel): ").strip() or None
    
    print("\n⏳ Kullanıcı kaydediliyor...")
    success, message, totp_secret = mfa.register_user(username, password, email)
    
    if not success:
        print(f"❌ Hata: {message}\n")
        return None, None
    
    print(f"✅ {message}")
    print(f"\n📱 TOTP Secret: {totp_secret}")
    
    # Provisioning URI
    uri = mfa.get_totp_provisioning_uri(username)
    print(f"\n🔗 Google Authenticator URI:")
    print(f"   {uri}\n")
    
    # QR kod üret
    if QR_AVAILABLE:
        qr_filename = f"{username}_qr.png"
        if generate_qr_code(uri, qr_filename):
            print(f"📷 QR Kod kaydedildi: qr_codes/{qr_filename}")
            print(f"   Google Authenticator ile bu QR kodu tarayın!\n")
    
    return mfa, totp_secret


def demo_login(mfa: MFAAuthenticator, totp_secret: str):
    """Login demosu"""
    print("\n" + "="*60)
    print("🔐 LOGIN\n")
    
    username = input("Kullanıcı adı: ").strip() or "admin"
    password = input("Şifre: ").strip() or "SecurePass123!"
    
    print("\n⏳ Şifre doğrulanıyor...")
    success, message, session_id = mfa.initiate_login(username, password)
    
    if not success:
        print(f"❌ {message}\n")
        return None
    
    print(f"✅ {message}")
    
    # OTP üret (demo için)
    totp = TOTPGenerator(secret=totp_secret)
    current_otp = totp.generate()
    remaining = totp.get_remaining_seconds()
    
    print(f"\n📲 Mevcut OTP Kodu: {current_otp}")
    print(f"   (Kalan süre: {remaining} saniye)")
    
    otp_input = input("\nOTP Kodunu girin: ").strip() or current_otp
    
    print("\n⏳ OTP doğrulanıyor...")
    success, message = mfa.verify_otp(session_id, otp_input)
    
    if not success:
        print(f"❌ {message}\n")
        return None
    
    print(f"✅ {message}")
    print(f"\n🎫 Session ID: {session_id[:32]}...")
    
    return session_id


def demo_session_check(mfa: MFAAuthenticator, session_id: str):
    """Session kontrolü demosu"""
    print("\n" + "="*60)
    print("🔍 SESSION KONTROLÜ\n")
    
    is_valid, username = mfa.verify_session(session_id)
    
    if is_valid:
        print(f"✅ Session geçerli")
        print(f"   Kullanıcı: {username}")
        
        # Session bilgileri
        session_info = mfa.session_manager.get_session_info(session_id)
        if session_info:
            print(f"   Durum: {session_info['status']}")
            print(f"   Kalan süre: {session_info['remaining_seconds']}s")
    else:
        print(f"❌ Session geçersiz veya süresi dolmuş")
    
    print()


def demo_logout(mfa: MFAAuthenticator, session_id: str):
    """Logout demosu"""
    print("\n" + "="*60)
    print("👋 LOGOUT\n")
    
    success = mfa.logout(session_id)
    
    if success:
        print("✅ Logout başarılı")
    else:
        print("❌ Logout hatası")
    
    print()


def interactive_demo():
    """İnteraktif demo"""
    print_banner()
    
    print("Bu demo, MFA sisteminin tüm özelliklerini gösterir:\n")
    print("1. Kullanıcı kaydı")
    print("2. TOTP secret ve QR kod üretimi")
    print("3. Login (şifre + OTP)")
    print("4. Session yönetimi")
    print("5. Logout\n")
    
    input("Devam etmek için Enter'a basın...")
    
    # 1. Kayıt
    mfa, totp_secret = demo_registration()
    if not mfa:
        return
    
    input("\nDevam etmek için Enter'a basın...")
    
    # 2. Login
    session_id = demo_login(mfa, totp_secret)
    if not session_id:
        return
    
    input("\nDevam etmek için Enter'a basın...")
    
    # 3. Session kontrolü
    demo_session_check(mfa, session_id)
    
    input("Devam etmek için Enter'a basın...")
    
    # 4. Logout
    demo_logout(mfa, session_id)
    
    # 5. Son kontrol
    demo_session_check(mfa, session_id)
    
    print("="*60)
    print("✅ Demo tamamlandı!")
    print("="*60 + "\n")


def quick_test():
    """Hızlı test (otomatik)"""
    print_banner()
    print("🚀 HIZLI TEST MODU\n")
    
    mfa = MFAAuthenticator()
    
    # Kayıt
    print("1️⃣  Kullanıcı kaydediliyor...")
    success, msg, secret = mfa.register_user("testuser", "TestPass123!", "test@example.com")
    print(f"   {msg}")
    
    if not success:
        return
    
    # Login
    print("\n2️⃣  Login başlatılıyor...")
    success, msg, session_id = mfa.initiate_login("testuser", "TestPass123!")
    print(f"   {msg}")
    
    if not success:
        return
    
    # OTP
    print("\n3️⃣  OTP doğrulanıyor...")
    totp = TOTPGenerator(secret=secret)
    otp = totp.generate()
    print(f"   OTP: {otp}")
    
    success, msg = mfa.verify_otp(session_id, otp)
    print(f"   {msg}")
    
    if not success:
        return
    
    # Session
    print("\n4️⃣  Session kontrol ediliyor...")
    is_valid, username = mfa.verify_session(session_id)
    print(f"   Geçerli: {is_valid} ({username})")
    
    # Logout
    print("\n5️⃣  Logout yapılıyor...")
    mfa.logout(session_id)
    print(f"   Logout başarılı")
    
    print("\n✅ Tüm testler başarılı!\n")


def main():
    """Ana fonksiyon"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        interactive_demo()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo iptal edildi.\n")
        sys.exit(0)
