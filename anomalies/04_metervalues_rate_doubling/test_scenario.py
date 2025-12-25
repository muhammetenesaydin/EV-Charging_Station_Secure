"""
Anomali 4: MeterValues Frekans İkiye Katlama Test Senaryosu
"""

import sys
import os
import json
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ocpp.ocpp_client import OCPPClient
from ocpp.ocpp_server import OCPPServer
from ids.ids_core import IDSCore
import threading


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


async def run_rate_doubling_attack(config):
    """MeterValues frekans saldırısını çalıştır"""
    attack_rate = config['attack_rate_hz']
    duration = config['duration_seconds']
    
    print("="*60)
    print("ANOMALİ 4: METERVALUES FREKANS İKİYE KATLAMA SALDIRISI")
    print("="*60)
    print(f"Normal Frekans: {config['normal_rate_hz']} Hz")
    print(f"Saldırı Frekansı: {attack_rate} Hz")
    print(f"Tolerans: ±{config['tolerance']*100}%")
    print(f"Süre: {duration} saniye")
    print("="*60 + "\n")
    
    # OCPP sunucusunu başlat
    server = OCPPServer(host="localhost", port=9000)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    # IDS'i başlat
    ids = IDSCore('vcan0')
    ids.start()
    
    time.sleep(1)
    
    # OCPP istemcisini bağla
    client = OCPPClient("ws://localhost:9000")
    
    if await client.connect():
        print(f"[SALDIRI] MeterValues mesajları {attack_rate} Hz'de gönderiliyor...")
        print(f"[SALDIRI] {duration} saniye boyunca devam edecek\n")
        
        interval = 1.0 / attack_rate
        start_time = time.time()
        message_count = 0
        energy = 1000.0
        
        while (time.time() - start_time) < duration:
            # MeterValues gönder
            await client.send_meter_values(
                connector_id=1,
                energy_wh=energy,
                power_w=7400,
                current_a=32
            )
            
            # IDS'e bildir
            ids.process_ocpp_message("MeterValues", {
                "connectorId": 1,
                "meterValue": [{
                    "timestamp": time.time(),
                    "sampledValue": [{"value": str(energy), "measurand": "Energy.Active.Import.Register"}]
                }]
            })
            
            message_count += 1
            energy += 10
            await asyncio.sleep(interval)
        
        elapsed = time.time() - start_time
        actual_rate = message_count / elapsed
        
        print(f"\n[SALDIRI] Saldırı tamamlandı")
        print(f"[SALDIRI] Gönderilen mesaj sayısı: {message_count}")
        print(f"[SALDIRI] Gerçek frekans: {actual_rate:.2f} Hz")
        print(f"[SALDIRI] Beklenen IDS alarmı: Frekans anomalisi tespit edildi\n")
        
        await client.disconnect()
    
    time.sleep(1)
    ids.stop()


if __name__ == "__main__":
    print("\n🔴 Anomali 4: MeterValues Frekans İkiye Katlama Saldırı Simülatörü\n")
    
    config = load_config()
    asyncio.run(run_rate_doubling_attack(config))
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
