import time
import random
from datetime import datetime

# === PARAMETRELER ===
THRESHOLD = 10         # 1 dakikada izin verilen maksimum yeni bağlantı sayısı
MONITOR_INTERVAL = 60  # İzleme süresi (saniye) - 1 dakika
BLOCK_DURATION = 60    # IP engelleme süresi (saniye) - 1 dakika

# === VERİ YAPILARI ===
connection_log = []     # Her bağlantı denemesini (zaman + IP) saklar
blocked_ips = {}        # Engellenen IP'ler ve engel süresi (IP: engel_bitiş_zamanı)

# === YARDIMCI FONKSİYONLAR ===
def get_new_connections():
    """
    Simülasyon: her döngüde rastgele 0–15 arasında yeni bağlantı oluşturur.
    Gerçek sistemde buraya WebSocket bağlantı sayacını koyarsın.
    """
    new_connections = []
    for _ in range(random.randint(0, 15)):
        ip = f"192.168.1.{random.randint(2, 254)}"
        new_connections.append(ip)
    return new_connections

def log_event(message):
    """Log dosyasına yazar."""
    with open("ddos_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(message)

def block_ip(ip):
    """IP adresini engeller."""
    blocked_ips[ip] = time.time() + BLOCK_DURATION  # Engelleme bitiş zamanını kaydet
    log_event(f"🚫 IP ENGELLENDİ: {ip}")

def unblock_expired_ips():
    """Engel süresi dolan IP'leri kaldırır."""
    now = time.time()
    expired = [ip for ip, until in blocked_ips.items() if now > until]
    for ip in expired:
        del blocked_ips[ip]
        log_event(f"✅ IP ENGELİ KALDIRILDI: {ip}")

# === ANA DÖNGÜ ===
print("🔍 Aşırı Bağlantı Tespiti Sistemi Başlatıldı...")
log_event("=== Sistem başlatıldı ===")

while True:
    # 1. ADIM: Süresi dolan engelleri kaldır
    unblock_expired_ips()

    # 2. ADIM: Yeni bağlantıları simüle et
    new_connections = get_new_connections()
    timestamp = datetime.now().strftime('%H:%M:%S')

    # 3. ADIM: Engelli IP'leri filtrele - sadece engellenmemiş IP'leri al
    allowed_connections = [ip for ip in new_connections if ip not in blocked_ips]

    # 4. ADIM: İzin verilen bağlantıları log'a kaydet
    for ip in allowed_connections:
        connection_log.append((time.time(), ip))  # (zaman_damgası, IP_adresi)

    # 5. ADIM: Son 1 dakikadaki bağlantıları say
    current_time = time.time()
    # MONITOR_INTERVAL (60 saniye) içindeki bağlantıları filtrele
    recent_connections = [ip for t, ip in connection_log if current_time - t <= MONITOR_INTERVAL]
    conn_count = len(recent_connections)

    # 6. ADIM: Durumu ekrana yazdır
    print(f"[{timestamp}] Yeni bağlantı: {len(new_connections)}, Toplam son 1 dakikada: {conn_count}")

    # 7. ADIM: Anomali (saldırı) tespiti
    if conn_count > THRESHOLD:
        log_event(f"⚠️ ANOMALİ TESPİT EDİLDİ! Son 1 dakikada {conn_count} bağlantı.")
        # Tüm yeni bağlantıları engelle
        for ip in allowed_connections:
            block_ip(ip)
        log_event("🛑 Olası DDoS engellendi.\n")

    time.sleep(5)  # 5 saniyede bir denetim yap