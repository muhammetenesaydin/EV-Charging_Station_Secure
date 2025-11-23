"""CAN Bus payload anomali simülasyonu ve görselleştirmesi.

Özellikler:
 - Normal ve anomali payload üretimi
 - Matplotlib grafiği (PNG kaydı)
 - Anomali loglama (ids_alert_log.csv)
 - Tüm akışın CSV export'u (full_stream.csv)
 - Matplotlib/Pandas yoksa metinsel özet fallback'i
"""

import os
import random
from datetime import datetime

try:  # Matplotlib isteğe bağlı
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    plt = None
    HAS_MATPLOTLIB = False
    print("[UYARI] matplotlib kurulu değil. Grafik metin olarak özetlenecek. Kurmak için: pip install matplotlib")

try:  # Pandas isteğe bağlı
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    pd = None
    HAS_PANDAS = False
    print("[UYARI] pandas kurulu değil. full_stream.csv basit formatta yazılacak. Kurmak için: pip install pandas")

# --- AYARLAR ---
NORMAL_MAX = 100
NORMAL_MIN = 0
ATTACK_COLOR = 'red'
NORMAL_COLOR = 'blue'

LOG_FILE = "ids_alert_log.csv"
STREAM_CSV = "full_stream.csv"
PLOT_FILE = "simulation_result.png"


class SimulationVisualizer:
    def __init__(self):
        self.payloads: list[int] = []
        self.timestamps: list[datetime] = []
        self.anomalies: list[tuple[int, int]] = []  # (index, value)
        self.indices: list[int] = []
        self.flags: list[bool] = []  # is_anomaly bayrakları
        self.counter: int = 0

    def add_data(self, value: int, is_anomaly: bool):
        """Veri noktasını ekle ve anomaly ise kaydet."""
        self.counter += 1
        self.indices.append(self.counter)
        self.payloads.append(value)
        self.timestamps.append(datetime.now())
        self.flags.append(is_anomaly)
        if is_anomaly:
            self.anomalies.append((self.counter, value))

    def _export_stream_csv(self):
        """Tüm akışı CSV dosyasına yazar."""
        if HAS_PANDAS and pd:
            df = pd.DataFrame({
                "index": self.indices,
                "timestamp": self.timestamps,
                "value": self.payloads,
                "is_anomaly": self.flags,
            })
            df.to_csv(STREAM_CSV, index=False, encoding="utf-8")
        else:  # Basit manuel yazım
            with open(STREAM_CSV, "w", encoding="utf-8") as f:
                f.write("index,timestamp,value,is_anomaly\n")
                for i, ts, val, flag in zip(self.indices, self.timestamps, self.payloads, self.flags):
                    f.write(f"{i},{ts.isoformat()},{val},{flag}\n")

    def plot_results(self):
        if HAS_MATPLOTLIB and plt:
            plt.figure(figsize=(12, 6))

            # Veri akış çizgisi
            plt.plot(self.indices, self.payloads, color='gray', alpha=0.5, linestyle='--', label='Veri Akışı')

            # Normal noktalar
            normal_indices = [i for i, flag in zip(self.indices, self.flags) if not flag]
            normal_values = [self.payloads[i - 1] for i in normal_indices]
            plt.scatter(normal_indices, normal_values, color=NORMAL_COLOR, s=40, label='Normal Trafik (0-100A)')

            # Anomali noktaları
            if self.anomalies:
                anomaly_x = [x[0] for x in self.anomalies]
                anomaly_y = [x[1] for x in self.anomalies]
                plt.scatter(anomaly_x, anomaly_y, color=ATTACK_COLOR, marker='x', s=100, linewidths=3,
                            label='TESPİT EDİLEN ANOMALİ')

            # Güvenli aralık
            plt.axhspan(NORMAL_MIN, NORMAL_MAX, color='green', alpha=0.1, label='Güvenli Protokol Aralığı')

            # Süslemeler
            plt.title('Senaryo 3: CAN Bus Payload Anomali Tespiti (Man-in-the-Middle)', fontsize=14)
            plt.xlabel('Paket Sıra No', fontsize=12)
            plt.ylabel('Payload Değeri (Amper)', fontsize=12)
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.legend(loc='upper right')

            print("Grafik oluşturuluyor ve kaydediliyor...")
            plt.savefig(PLOT_FILE, dpi=150, bbox_inches='tight')
            plt.show()
            print(f"[OK] Grafik '{PLOT_FILE}' dosyasına kaydedildi.")
        else:
            print("[METİNSEL ÖZET] Toplam nokta:", len(self.payloads))
            if self.anomalies:
                print("Anomaliler:")
                for idx, val in self.anomalies:
                    print(f" - {idx}: {val}")
            else:
                print("Anomali yok.")

        # Her durumda akışı dışa aktar
        self._export_stream_csv()
        print(f"[OK] Akış CSV kaydedildi: {STREAM_CSV}")


def _ensure_log_header():
    """Log dosyasında header yoksa ekler (opsiyonel)."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("timestamp,level,event,payload\n")


def run_visual_simulation():
    visualizer = SimulationVisualizer()
    _ensure_log_header()

    # Veri üretimi (Normal -> Saldırı -> Normal)
    traffic_data = [random.randint(20, 80) for _ in range(15)]
    attack_data = [255, 100, 120, 255, 400, 85]  # Saldırı manipülasyonu
    recovery_data = [random.randint(20, 80) for _ in range(10)]
    full_stream = traffic_data + attack_data + recovery_data

    print("Simülasyon çalışıyor ve veriler analiz ediliyor...")

    for value in full_stream:
        is_anomaly = value < NORMAL_MIN or value > NORMAL_MAX
        visualizer.add_data(value, is_anomaly)
        if is_anomaly:
            # Log dosyasına yaz (append)
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().isoformat()},CRITICAL,ANOMALY_DETECTED,PAYLOAD:{value}\n")

    visualizer.plot_results()
    print(f"[OK] Anomali logları '{LOG_FILE}' dosyasına yazıldı.")
    return visualizer


if __name__ == "__main__":
    run_visual_simulation()

# --- SİMÜLASYON AKIŞI (Önceki Kodun Entegre Hali) ---

def run_visual_simulation():
    visualizer = SimulationVisualizer()
    
    # Veri Üretimi (Normal -> Saldırı -> Normal)
    # Normal: 0-80 arası rastgele
    traffic_data = [random.randint(20, 80) for _ in range(15)]
    
    # Saldırı: 255, 300, -50, 150 gibi değerler
    attack_data = [255, 100, 120, 255, 400, 85] 
    
    # Normal: Tekrar normale dönüş
    recovery_data = [random.randint(20, 80) for _ in range(10)]
    
    full_stream = traffic_data + attack_data + recovery_data
    
    print("Simülasyon çalışıyor ve veriler analiz ediliyor...")
    
    # Analiz Döngüsü
    for value in full_stream:
        # IDS Kuralı
        is_anomaly = False
        if value < NORMAL_MIN or value > NORMAL_MAX:
            is_anomaly = True
            
        # Görselleştiriciye ekle
        visualizer.add_data(value, is_anomaly)
        
    # Sonucu Çiz
    visualizer.plot_results()

if __name__ == "__main__":
    run_visual_simulation()