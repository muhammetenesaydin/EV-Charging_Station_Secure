"""Streamlit arayüzünü başlatmak için giriş noktası.
PyInstaller ile paketlerken `streamlit run` yerine programatik çağrı yapıyoruz.
Not: Streamlit'in resmi API'si doğrudan run fonksiyonu sağlamadığından burada
subprocess ile çağırıyoruz.
"""
from __future__ import annotations
import subprocess
import sys
import os

APP_FILE = os.path.join(os.path.dirname(__file__), "app.py")


def main():
    # Windows'ta exe içinden çağrı
    cmd = [sys.executable, "-m", "streamlit", "run", APP_FILE, "--server.headless", "false"]
    print("[INFO] Streamlit arayüzü başlatılıyor...")
    print("[CMD]", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
