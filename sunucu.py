import asyncio
import websockets
import time

baglanti_sayaci = {}
ZAMAN_ARALIGI = 60  # Saniye (rapordaki 1 dakika)
ESIK_DEGERI = 10     # İzin verilen max bağlantı

# --- DÜZELTME BURADA ---
# Fonksiyon tanımından 'path' argümanı kaldırıldı
async def handler(websocket):
# ---------------------
    simdiki_zaman = int(time.time())
    # Gelen bağlantının IP adresini al
    istemci_ip = websocket.remote_address[0]
    
    # Bu IP için zaman aşımına uğramış eski bağlantı kayıtlarını temizle
    mevcut_kayitlar = baglanti_sayaci.get(istemci_ip, [])
    gecerli_kayitlar = [t for t in mevcut_kayitlar if simdiki_zaman - t < ZAMAN_ARALIGI]
    
    # Yeni bağlantının zaman damgasını ekle
    gecerli_kayitlar.append(simdiki_zaman)
    baglanti_sayaci[istemci_ip] = gecerli_kayitlar
    
    # ANOMALİ TESPİTİ (Raporunuzdaki kural):
    # Bu IP'den gelen bağlantı sayısı eşik değerini aştı mı?
    if len(gecerli_kayitlar) > ESIK_DEGERI:
        # Raporunuzdaki örnek uyarıya benzer bir çıktı
        print(f"--- ALARM: IP {istemci_ip} EŞİK AŞILDI! --- Son {ZAMAN_ARALIGI}sn içinde {len(gecerli_kayitlar)} bağlantı!")
    else:
        print(f"Yeni bağlantı alındı: {istemci_ip}. (Son {ZAMAN_ARALIGI}sn içinde toplam: {len(gecerli_kayitlar)} bağlantı)")
    
    try:
        await websocket.wait_closed() # Bağlantı kapanana kadar bekle
    except websockets.exceptions.ConnectionClosed:
        pass # Bağlantı kapandı, sorun yok

async def main():
    print(f"WebSocket sunucusu (Gözlemci) 'localhost:8765' üzerinde başlatıldı...")
    print(f"Tespit kuralı: {ZAMAN_ARALIGI} saniye içinde {ESIK_DEGERI}'den fazla bağlantı ALARM tetikler.")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Sunucuyu sonsuza kadar çalıştır

if __name__ == "__main__":
    asyncio.run(main())
