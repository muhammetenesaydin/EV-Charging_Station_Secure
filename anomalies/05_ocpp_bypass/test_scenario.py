"""
Anomali 5: OCPP Bypass Test Senaryosu
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


def run_bypass_attack(config):
    """OCPP bypass saldırısını çalıştır"""
    can_id = int(config['can_id'], 16)
    
    print("="*60)
    print("ANOMALİ 5: OCPP BYPASS SALDIRISI")
    print("="*60)
    print(f"CAN ID: 0x{can_id:03X}")
    print(f"Saldırı: OCPP yetkilendirmesi OLMADAN CAN komutu gönderme")
    print(f"Normal Akış: OCPP RemoteStart → CAN 0x{can_id:03X}")
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
    
    print("[SALDIRI] OCPP yetkilendirmesi OLMADAN CAN başlatma komutu gönderiliyor...")
    print(f"[SALDIRI] Doğrudan CAN ID 0x{can_id:03X} mesajı gönderiliyor...\n")
    
    # OCPP olmadan direkt CAN komutu gönder
    can_if.send_message(
        arbitration_id=can_id,
        data=[0x01, 0x00, 0x00, 0x00],  # Start command
        log=True
    )
    
    time.sleep(2)
    
    print(f"\n[SALDIRI] Saldırı tamamlandı")
    print(f"[SALDIRI] Beklenen IDS alarmı: Yetkisiz CAN komutu tespit edildi\n")
    
    ids.stop()
    can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomali 5: OCPP Bypass Saldırı Simülatörü\n")
    
    config = load_config()
    run_bypass_attack(config)
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
