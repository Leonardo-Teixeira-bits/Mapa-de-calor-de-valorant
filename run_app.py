"""Convenience launcher script to run the Streamlit dashboard via standard Python command."""

from __future__ import annotations
import sys
import subprocess
from pathlib import Path


def main():
    app_path = Path(__file__).resolve().parent / "app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]
    print("=" * 60)
    print("  VALORANT GeoAnalytics • UNIVAVA")
    print("  Inicializando Dashboard Interativo...")
    print(f"  Arquivo: {app_path}")
    print("=" * 60)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDashboard encerrado pelo usuário.")


if __name__ == "__main__":
    main()
