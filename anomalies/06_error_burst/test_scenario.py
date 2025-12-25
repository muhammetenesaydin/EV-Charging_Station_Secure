"""
Anomali 6: Hata Patlaması Test Senaryosu
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from can.can_utils import CANInterface
from ids.ids_core import IDSCore


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def run_error_burst_attack(config):
    """Hata patlaması saldırısını çalıştır"""
    can_id = int(config['can_id'], 16)
    burst_count = config['burst_count']
    burst_duration = config['burst_duration']
    
    print("="*60)
    print("ANOMALİ 6: HATA PATLAMASI SALDIRISI")
    print("="*60)
    print(f"CAN ID: 0x{can_id:03X} (Hata Mesajı)")
    print(f"Patlama: {burst_count} mesaj {burst_duration} saniyede")
    print(f"Tespit Eşiği: {config['threshold']} mesaj/saniye")
    print("="*60 + "\n")
    
    # CAN'a bağlan
    can_if = CANInterface('vcan0')
    if not can_if.connect():
        print("HATA: vcan0'a bağlanılamadı")
        return
    
    # IDS'i başlat
    ids = IDSCore('vcan0')
    ids.start()
    
    time.sleep(1)
    
    print(f"[SALDIRI] {burst_count} hata mesajı {burst_duration} saniyede gönderiliyor...")
    print(f"[SALDIRI] Başlıyor...\n")
    
    interval = burst_duration / burst_count
    start_time = time.time()
    
    for i in range(burst_count):
        can_if.send_message(
            arbitration_id=can_id,
            data=[0xE1, 0x00, 0x00, 0x00],  # Error code
            log=False
        )
        time.sleep(interval)
    
    elapsed = time.time() - start_time
    actual_rate = burst_count / elapsed
    
    print(f"\n[SALDIRI] Saldırı tamamlandı")
    print(f"[SALDIRI] Gönderilen mesaj: {burst_count}")
    print(f"[SALDIRI] Süre: {elapsed:.2f} saniye")
    print(f"[SALDIRI] Gerçek hız: {actual_rate:.1f} mesaj/saniye")
    print(f"[SALDIRI] Beklenen IDS alarmı: Hata patlaması tespit edildi\n")
    
    time.sleep(1)
    ids.stop()
    can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomali 6: Hata Patlaması Saldırı Simülatörü\n")
    
    config = load_config()
    run_error_burst_attack(config)
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
