import asyncio
import websockets
import time

# Rapordaki "Anomali" tanımına uygun olarak 10'dan fazla bağlantı açacağız
BAGLANTI_ADEDI = 20
SUNUCU_ADRESI = "ws://localhost:8765"

async def connect():
    try:
        # Sunucuya bağlanmayı dene
        async with websockets.connect(SUNUCU_ADRESI) as websocket:
            # Bağlantıyı 5 saniye açık tut, sonra kapat
            await asyncio.sleep(5)
            return True
    except Exception as e:
        # Sunucuya bağlanamazsak hatayı yazdır
        print(f"Bağlantı hatası: {e}")
        return False

async def main():
    print(f"Saldırı Başlatılıyor: {SUNUCU_ADRESI} adresine {BAGLANTI_ADEDI} adet eş zamanlı bağlantı denemesi...")

    # Eş zamanlı olarak BAGLANTI_ADEDI kadar connect() fonksiyonunu çalıştır
    tasks = [connect() for _ in range(BAGLANTI_ADEDI)]
    results = await asyncio.gather(*tasks)

    basarili_baglanti = sum(results)
    print(f"Saldırı Tamamlandı. {basarili_baglanti} adet bağlantı başarılı oldu.")

if __name__ == "__main__":
    asyncio.run(main())
