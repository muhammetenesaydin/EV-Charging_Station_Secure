"""
Anomali 10: Tekrar Saldırısı Test Senaryosu
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


def run_replay_attack(config):
    """Tekrar saldırısını çalıştır"""
    can_id = int(config['can_id'], 16)
    payload = config['payload']
    replay_count = config['replay_count']
    interval = config['interval_seconds']
    
    print("="*60)
    print("ANOMALİ 10: TEKRAR SALDIRISI (REPLAY ATTACK)")
    print("="*60)
    print(f"CAN ID: 0x{can_id:03X}")
    print(f"Payload: {payload}")
    print(f"Tekrar Sayısı: {replay_count}")
    print(f"Aralık: {interval} saniye")
    print(f"Tespit Eşiği: {config['threshold']} tekrar")
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
    
    print(f"[SALDIRI] Aynı CAN mesajı {replay_count} kez tekrarlanıyor...")
    print(f"[SALDIRI] Her {interval} saniyede bir gönderilecek\n")
    
    for i in range(replay_count):
        print(f"[SALDIRI] Tekrar #{i+1}: CAN ID 0x{can_id:03X}, Payload: {payload}")
        
        can_if.send_message(
            arbitration_id=can_id,
            data=payload,
            log=True
        )
        
        if i < replay_count - 1:
            time.sleep(interval)
    
    time.sleep(2)
    
    print(f"\n[SALDIRI] Saldırı tamamlandı")
    print(f"[SALDIRI] Toplam {replay_count} aynı mesaj gönderildi")
    print(f"[SALDIRI] Beklenen IDS alarmı: Tekrar saldırısı tespit edildi\n")
    
    ids.stop()
    can_if.disconnect()


if __name__ == "__main__":
    print("\n🔴 Anomali 10: Tekrar Saldırısı (Replay Attack) Simülatörü\n")
    
    config = load_config()
    run_replay_attack(config)
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
