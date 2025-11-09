import asyncio
import websockets
import can
import threading
import time
import sys

# --- Global Durum Değişkenleri ---
ocpp_start_bekleniyor = False
lock = threading.Lock()
last_seen_times = {}
bus = None 

# --- GÜVENLİK ÖNLEMİ FONKSİYONU ---
def onlem_al(anomali_tipi_adi, tespit_edilen_id):
    """
    Bir anomali tespit edildiğinde çağrılır ve GÜVENLİ MOD komutu gönderir.
    'anomali_tipi_adi' artık "Anomali 4" yerine "Frekans Dengesizliği" gibi açıklayıcı bir isim alacak.
    """
    global bus
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # GÜNCELLEME BURADA: Artık 'anomali_tipi_adi'nı basıyoruz
    print(f"[{anomali_tipi_adi} TESPİT EDİLDİ] - ID: {tespit_edilen_id:03X}")
    print("GÜVENLİK ÖNLEMİ SİMÜLASYONU BAŞLATILIYOR...")
    print("Tüm sistemlere 'GÜVENLİ MODA GEÇ' komutu (0x001) gönderiliyor.")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    
    try:
        guvenli_mod_mesaji = can.Message(
            arbitration_id=0x001, 
            data=[0xDE, 0xAD, 0x01],
            dlc=3
        )
        if bus:
            bus.send(guvenli_mod_mesaji)
    except Exception as e:
        print(f"[HATA] Güvenli Mod komutu gönderilemedi: {e}")


# --- OCPP Sunucusu (Değişmedi) ---
async def ocpp_server(websocket, path):
    global ocpp_start_bekleniyor
    print(f"[GÜVENLİK-IDS] Yeni bir Şarj İstasyonu bağlandı: {websocket.remote_address}")
    try:
        async for message in websocket:
            if "RemoteStartTransaction" in message:
                with lock:
                    ocpp_start_bekleniyor = True
                print("\n[GÜVENLİK-IDS] NORMAL: OCPP'den 'Start' komutu alındı. (CAN ID 0x200 bekleniyor)")
            await websocket.send(f"'{message}' komutu IDS tarafından alındı.")
    except websockets.exceptions.ConnectionClosed:
        print(f"[GÜVENLİK-IDS] Şarj İstasyonu bağlantısı kapandı.")

# --- CAN Dinleyicisi (IDS Çekirdeği - GÜNCELLENDİ) ---
def can_listener():
    global ocpp_start_bekleniyor, last_seen_times, bus
    
    try:
        bus = can.interface.Bus('vcan0', bustype='socketcan')
    except OSError:
        print("\n[HATA] 'vcan0' arayüzü bulunamadı...")
        sys.exit()
        
    print("[GÜVENLİK-IDS] CAN veriyolu 'vcan0' üzerinde dinlemede...")

    while True:
        msg = bus.recv()
        current_time = time.time()

        # --- ANOMALİ 6 TESPİTİ (DoS) ---
        if msg.arbitration_id == 0x123: 
            last_seen = last_seen_times.get(0x123, 0)
            time_delta = current_time - last_seen
            if time_delta < 0.1 and last_seen != 0:
                # GÜNCELLEME BURADA:
                onlem_al("Ardışık Hata Mesajları (DoS)", msg.arbitration_id)
            last_seen_times[0x123] = current_time

        # --- ANOMALİ 4 TESPİTİ (Frekans) ---
        if msg.arbitration_id == 0x300: 
            last_seen = last_seen_times.get(0x300, 0)
            if last_seen == 0:
                last_seen_times[0x300] = current_time
                continue 
                
            time_delta = current_time - last_seen
            
            if (time_delta < 0.9) or (time_delta > 1.1):
                anomali_tipi = "HIZLI Tekrarlama" if time_delta < 0.9 else "BAYAT/GECİKMİŞ Tekrarlama"
                
                # GÜNCELLEME BURADA:
                onlem_al(f"Frekans Dengesizliği ({anomali_tipi})", msg.arbitration_id)

            last_seen_times[0x300] = current_time

        # --- ANOMALİ 5 TESPİTİ (Bypass) ---
        if msg.arbitration_id == 0x200: 
            print("\n[GÜVENLİK-IDS] CAN ID 0x200 (Start) görüldü. Kontrol ediliyor...")
            with lock:
                if ocpp_start_bekleniyor:
                    print("[GÜVENLİK-IDS] NORMAL: Komut doğrulandı. İzin verildi.")
                    ocpp_start_bekleniyor = False 
                else:
                    # GÜNCELLEME BURADA:
                    onlem_al("OCPP Dışı Kaynaklı Komut (Bypass)", msg.arbitration_id)

# --- Ana Başlatıcı (Değişmedi) ---
async def main():
    can_thread = threading.Thread(target=can_listener, daemon=True)
    can_thread.start()
    
    print("[GÜVENLİK-IDS] OCPP sunucusu 'localhost' (Port 8765) üzerinde başlatılıyor...")
    server = await websockets.serve(ocpp_server, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    print("GÜVENLİKLİ ÖNLEM SİMÜLASYONU v2 (Açıklayıcı İsimli) BAŞLATILIYOR...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[GÜVENLİK-IDS] Simülasyon durduruldu.")
