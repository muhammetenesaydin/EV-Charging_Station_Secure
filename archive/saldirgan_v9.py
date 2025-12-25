import asyncio
import websockets
import json

SUNUCU_ADRESI = "ws://localhost:8766"

# Raporunuzdaki "Anomali" senaryosuna uygun sahte 'BootNotification' mesajı
SAHTE_MESAJ = {
    "chargePointVendor": "Hacker",
    "chargePointModel": "Injector-X",
    "firmwareVersion": "evil-v9"  # Bu, 'ALLOWED_LIST' içinde olmayan değer
}

# --- Ekstra: Normal Durum Senaryosu ---
# Bunu test etmek için SAHTE_MESAJ yerine bunu kullanabilirsiniz
NORMAL_MESAJ = {
    "chargePointVendor": "Acme",
    "chargePointModel": "Charger-100",
    "firmwareVersion": "v1.6-release" # Bu, 'ALLOWED_LIST' içinde olan değer
}

async def main():
    print(f"--- 9. Senaryo: Sahte Cihaz Simülatörü ---")
    print(f"Sunucuya bağlanılıyor: {SUNUCU_ADRESI}")
    
    try:
        async with websockets.connect(SUNUCU_ADRESI) as websocket:
            print("Bağlantı başarılı.")
            
            # Sunucuya sahte mesajı JSON formatında gönder
            mesaj_str = json.dumps(SAHTE_MESAJ)
            print(f"Gönderilen 'BootNotification' mesajı: {mesaj_str}")
            await websocket.send(mesaj_str)
            
            # Sunucunun bağlantıyı kapatmasını bekle (veya 5sn bekle)
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"Sunucuya bağlanırken hata oluştu: {e}")

if __name__ == "__main__":
    asyncio.run(main())
