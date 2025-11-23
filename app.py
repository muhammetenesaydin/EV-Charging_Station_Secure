"""Streamlit tabanlı CAN Bus payload anomali görselleştirme arayüzü.

Kullanım:
  streamlit run app.py

Özellikler:
- Simülasyonu adım adım ilerlet (Next Step / Otomatik Çalıştır)
- Anomali tespit edilen paketleri kırmızı X ile göster
- Canlı tablo (index, timestamp, değer, anomaly)
- Özet metrikler (toplam paket, anomali sayısı, anomali oranı)
- Log dosyası ve CSV indirme butonları
"""

import time
import random
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

NORMAL_MIN = 0
NORMAL_MAX = 100
ATTACK_COLOR = 'red'
NORMAL_COLOR = 'royalblue'

# Saldırı senaryosu veri seti (önceden tanımlı)
TRAFFIC_LEN1 = 15
ATTACK_VALUES = [255, 100, 120, 255, 400, 85]
RECOVERY_LEN = 10

LOG_FILE = "ids_alert_log.csv"
STREAM_CSV = "full_stream.csv"

class StepSimulation:
    def __init__(self):
        self.stream = self._generate_stream()
        self.index = 0
        self.records = []  # list of dicts

    def _generate_stream(self):
        traffic_normal1 = [random.randint(20, 80) for _ in range(TRAFFIC_LEN1)]
        attack = ATTACK_VALUES[:]  # copy
        recovery = [random.randint(20, 80) for _ in range(RECOVERY_LEN)]
        return traffic_normal1 + attack + recovery

    def has_next(self):
        return self.index < len(self.stream)

    def step(self):
        if not self.has_next():
            return None
        value = self.stream[self.index]
        self.index += 1
        is_anomaly = value < NORMAL_MIN or value > NORMAL_MAX
        rec = {
            "index": self.index,
            "timestamp": datetime.now(),
            "value": value,
            "is_anomaly": is_anomaly
        }
        self.records.append(rec)
        if is_anomaly:
            with open(LOG_FILE, "a", encoding="utf-8") as lf:
                lf.write(f"{rec['timestamp'].isoformat()},CRITICAL,ANOMALY_DETECTED,PAYLOAD:{value}\n")
        return rec

    def to_dataframe(self):
        if not self.records:
            return pd.DataFrame(columns=["index", "timestamp", "value", "is_anomaly"])
        df = pd.DataFrame(self.records)
        return df

# Yardımcı fonksiyonlar

def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as lf:
            lf.write("timestamp,level,event,payload\n")

@st.cache_data
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

# --- UI ---
st.set_page_config(page_title="CAN Payload Anomali IDS", layout="wide")
st.title("CAN Bus Payload Anomali Tespiti - Adım Adım Simülasyon")

if "sim" not in st.session_state:
    st.session_state.sim = StepSimulation()
    init_log_file()

sim: StepSimulation = st.session_state.sim

col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("Kontroller")
    if st.button("Sonraki Paket"):
        sim.step()
    auto = st.checkbox("Otomatik Çalıştır (Hızlı)")
    speed = st.slider("Otomatik hız (saniye)", 0.1, 1.5, 0.4)
    if auto and sim.has_next():
        # Her render döngüsünde bir adım daha
        sim.step()
        time.sleep(speed)  # UI nefes alması için kısa bekleme
        # Streamlit yeni sürümlerde st.rerun, eski sürümde experimental_rerun
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()
    if not sim.has_next():
        st.success("Simülasyon tamamlandı.")
    if st.button("Sıfırla"):
        st.session_state.sim = StepSimulation()
        init_log_file()
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

    st.markdown("---")
    df = sim.to_dataframe()
    total = len(df)
    anomalies = df[df["is_anomaly"]].shape[0]
    ratio = (anomalies / total * 100) if total else 0
    st.metric("Toplam Paket", total)
    st.metric("Anomali Sayısı", anomalies)
    st.metric("Anomali Oranı %", f"{ratio:.1f}")

    if not df.empty:
        csv_bytes = convert_df(df)
        st.download_button("Akış CSV indir", csv_bytes, STREAM_CSV, mime="text/csv")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_content = f.read()
        st.download_button("Log dosyası indir", log_content, LOG_FILE, mime="text/plain")

with col_left:
    st.subheader("Canlı Grafik")
    df = sim.to_dataframe()
    fig, ax = plt.subplots(figsize=(10, 5))
    if not df.empty:
        ax.plot(df["index"], df["value"], color='gray', linestyle='--', alpha=0.5, label='Veri Akışı')
        normal_df = df[~df["is_anomaly"]]
        anomaly_df = df[df["is_anomaly"]]
        ax.scatter(normal_df["index"], normal_df["value"], color=NORMAL_COLOR, s=50, label='Normal')
        if not anomaly_df.empty:
            ax.scatter(anomaly_df["index"], anomaly_df["value"], color=ATTACK_COLOR, marker='x', s=120, linewidths=2.5, label='Anomali')
    ax.axhspan(NORMAL_MIN, NORMAL_MAX, color='green', alpha=0.08, label='Güvenli Aralık')
    ax.set_xlabel("Paket Index")
    ax.set_ylabel("Payload (A)")
    ax.set_title("Adım Adım Payload İzleme")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
    st.pyplot(fig, clear_figure=True)

st.markdown("---")
st.subheader("Paket Tablosu")
st.dataframe(df, width='stretch')

st.caption("Bu arayüz eğitim amaçlıdır. Anomali tespiti basit eşik kontrolüne dayanır.")
