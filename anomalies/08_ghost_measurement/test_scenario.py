"""
Anomali 8: Hayalet Ölçüm Değişimi Test Senaryosu
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


async def run_ghost_measurement_attack(config):
    """Hayalet ölçüm saldırısını çalıştır"""
    initial_energy = config['initial_energy']
    ghost_jump = config['ghost_jump']
    threshold = config['threshold_per_second']
    
    print("="*60)
    print("ANOMALİ 8: HAYALET ÖLÇÜM DEĞİŞİMİ SALDIRISI")
    print("="*60)
    print(f"Başlangıç Enerjisi: {initial_energy} Wh")
    print(f"Hayalet Sıçrama: {ghost_jump} Wh ({ghost_jump/1000} kWh)")
    print(f"Tespit Eşiği: {threshold} Wh/s ({threshold/1000} kWh/s)")
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
        print("[SALDIRI] Normal ölçüm gönderiliyor...")
        
        # Normal ölçüm
        await client.send_meter_values(
            connector_id=1,
            energy_wh=initial_energy,
            power_w=7400,
            current_a=32
        )
        
        ids.process_ocpp_message("MeterValues", {
            "connectorId": 1,
            "meterValue": [{
                "timestamp": time.time(),
                "sampledValue": [{
                    "value": str(initial_energy),
                    "measurand": "Energy.Active.Import.Register",
                    "unit": "Wh"
                }]
            }]
        })
        
        await asyncio.sleep(1)
        
        print(f"[SALDIRI] HAYALETÖlçüm gönderiliyor: {initial_energy} → {initial_energy + ghost_jump} Wh")
        print(f"[SALDIRI] Ani sıçrama: {ghost_jump/1000} kWh!\n")
        
        # Hayalet ölçüm - ani sıçrama
        await client.send_meter_values(
            connector_id=1,
            energy_wh=initial_energy + ghost_jump,
            power_w=7400,
            current_a=32
        )
        
        ids.process_ocpp_message("MeterValues", {
            "connectorId": 1,
            "meterValue": [{
                "timestamp": time.time(),
                "sampledValue": [{
                    "value": str(initial_energy + ghost_jump),
                    "measurand": "Energy.Active.Import.Register",
                    "unit": "Wh"
                }]
            }]
        })
        
        await asyncio.sleep(2)
        
        print(f"\n[SALDIRI] Saldırı tamamlandı")
        print(f"[SALDIRI] Beklenen IDS alarmı: Anormal enerji delta tespit edildi\n")
        
        await client.disconnect()
    
    time.sleep(1)
    ids.stop()


if __name__ == "__main__":
    print("\n🔴 Anomali 8: Hayalet Ölçüm Değişimi Saldırı Simülatörü\n")
    
    config = load_config()
    asyncio.run(run_ghost_measurement_attack(config))
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
