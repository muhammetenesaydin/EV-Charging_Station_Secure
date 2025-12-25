"""
Anomali 7: WebSocket Bağlantı Seli Test Senaryosu
"""

import sys
import os
import json
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ocpp.ocpp_server import OCPPServer
from ids.ids_core import IDSCore
import threading
import websockets


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


async def run_websocket_flood_attack(config):
    """WebSocket sel saldırısını çalıştır"""
    connection_count = config['connection_count']
    duration = config['duration_seconds']
    server_url = config['server_url']
    
    print("="*60)
    print("ANOMALİ 7: WEBSOCKET BAĞLANTI SELİ SALDIRISI")
    print("="*60)
    print(f"Hedef: {server_url}")
    print(f"Bağlantı Sayısı: {connection_count}")
    print(f"Süre: {duration} saniye")
    print(f"Tespit Eşiği: {config['threshold']} bağlantı/{duration}s")
    print("="*60 + "\n")
    
    # OCPP sunucusunu başlat
    server = OCPPServer(host="localhost", port=9000)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    # IDS'i başlat
    ids = IDSCore('vcan0')
    ids.start()
    
    time.sleep(1)
    
    print(f"[SALDIRI] {connection_count} WebSocket bağlantısı {duration} saniyede açılıyor...")
    print(f"[SALDIRI] Başlıyor...\n")
    
    connections = []
    start_time = time.time()
    interval = duration / connection_count
    
    try:
        for i in range(connection_count):
            try:
                # Bağlantı aç
                ws = await asyncio.wait_for(
                    websockets.connect(server_url),
                    timeout=1.0
                )
                connections.append(ws)
                
                # IDS'e bildir
                ids.process_websocket_connection()
                
                await asyncio.sleep(interval)
            except Exception as e:
                pass  # Bağlantı hatalarını yoksay
        
        elapsed = time.time() - start_time
        success_count = len(connections)
        
        print(f"\n[SALDIRI] Saldırı tamamlandı")
        print(f"[SALDIRI] Açılan bağlantı: {success_count}/{connection_count}")
        print(f"[SALDIRI] Süre: {elapsed:.2f} saniye")
        print(f"[SALDIRI] Hız: {success_count/elapsed:.1f} bağlantı/saniye")
        print(f"[SALDIRI] Beklenen IDS alarmı: WebSocket seli tespit edildi\n")
        
        # Bağlantıları kapat
        for ws in connections:
            try:
                await ws.close()
            except:
                pass
    
    except KeyboardInterrupt:
        print("\n[SALDIRI] Kullanıcı tarafından durduruldu")
    
    time.sleep(1)
    ids.stop()


if __name__ == "__main__":
    print("\n🔴 Anomali 7: WebSocket Bağlantı Seli Saldırı Simülatörü\n")
    
    config = load_config()
    asyncio.run(run_websocket_flood_attack(config))
    
    print("="*60)
    print("Saldırı senaryosu tamamlandı")
    print("="*60 + "\n")
