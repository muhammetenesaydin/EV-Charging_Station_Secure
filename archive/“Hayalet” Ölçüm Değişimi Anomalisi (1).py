import time
import random
from datetime import datetime
import os

# --- Parametreler ---
NORMAL_MIN = 100.0
NORMAL_MAX = 120.0
ANOMALY_THRESHOLD = 5.0
CHECK_INTERVAL = 2

def simulate_sensor(prev_value):
    """Sensör verisi üretir (test için anomali oranı artırıldı)."""
    # %30 ihtimalle anormal veri üret (test için)
    if random.random() < 0.3:  
        change = random.uniform(10, 30) * random.choice([-1, 1])
    else:
        change = random.uniform(-2, 2)
    
    return round(prev_value + change, 2)

def detect_anomaly(prev_value, current_value):
    """Anomali kontrolü."""
    diff = abs(current_value - prev_value)
    
    if diff > ANOMALY_THRESHOLD:
        return True, f"🚨 Ani Değişim Anomalisi! Önceki: {prev_value} → Şimdi: {current_value} (Δ={diff})"
    elif current_value < NORMAL_MIN or current_value > NORMAL_MAX:
        return True, f"⚠️ Aralık Dışı Anomalisi: {current_value} kWh"
    else:
        return False, f"✅ Normal Ölçüm: {current_value} kWh (Δ={diff})"

def monitor_sensor():
    print("🔍 Anomali Tespit Sistemi Başladı...\n")
    print("📁 Log dosyası: anomaly_log.txt\n")
    
    # Log dosyasını kontrol et
    try:
        with open("anomaly_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== Yeni Oturum Başladı: {datetime.now()} ===\n")
        print("✅ Log dosyası hazır")
    except Exception as e:
        print(f"❌ Log dosyası hatası: {e}")
        return
    
    prev_value = random.uniform(NORMAL_MIN, NORMAL_MAX)
    anomaly_count = 0

    while True:
        current_value = simulate_sensor(prev_value)
        anomaly, message = detect_anomaly(prev_value, current_value)

        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

        if anomaly:
            anomaly_count += 1
            try:
                with open("anomaly_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now()}] {message}\n")
                print(f"   📝 Log'a yazıldı (Toplam anomali: {anomaly_count})")
            except Exception as e:
                print(f"   ❌ Log yazma hatası: {e}")

        prev_value = current_value
        time.sleep(CHECK_INTERVAL)

# --- Başlat ---
if __name__ == "__main__":
    monitor_sensor()