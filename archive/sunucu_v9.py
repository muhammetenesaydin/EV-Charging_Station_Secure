import asyncio
import websockets
import json

# Raporunuzdaki "Normal Durum": İzin verilen yazılımların listesi 
ALLOWED_LIST = [
    "v1.5-stable",
    "v1.6-release",
    "v2.0.1-prod"
]

async def handler(websocket):
    print(f"Yeni bir cihaz bağlandı: {websocket.remote_address[0]}")
    try:
        # Cihazdan 'BootNotification' mesajını bekle
        message_str = await websocket.recv()
        print(f"Mesaj alındı: {message_str}")
        
        # Mesajı JSON olarak ayrıştır
        try:
            message_json = json.loads(message_str)
            firmware = message_json.get("firmwareVersion")
        except json.JSONDecodeError:
            print("HATA: Geçersiz JSON formatı.")
            return

        # --- ANOMALİ TESPİTİ (Raporunuzdaki Kural) --- [cite: 43]
        if firmware:
            if firmware not in ALLOWED_LIST:
                # Raporunuzdaki "Anomali" ve "Uyarı" [cite: 45, 149]
                print(f"--- ALARM: YAZILIM UYUŞMAZLIĞI! ---")
                print(f"    Gelen Versiyon: '{firmware}'")
                print(f"    Bu versiyon İZİN LİSTESİNDE DEĞİL! ")
            else:
                # Raporunuzdaki "Normal Durum" 
                print(f"Cihaz doğrulandı. '{firmware}' izin listesinde.")
        else:
            print("HATA: Mesajda 'firmwareVersion' alanı bulunamadı.")
            
    except websockets.exceptions.ConnectionClosed:
        print("Cihazın bağlantısı kapandı.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

async def main():
    print("--- 9. Senaryo: Yazılım Kimliği Sunucusu ---")
    print(f"İzin Verilen Yazılımlar: {ALLOWED_LIST}")
    print(f"Sunucu 'localhost:8766' üzerinde başlatıldı...")
    async with websockets.serve(handler, "localhost", 8766):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
