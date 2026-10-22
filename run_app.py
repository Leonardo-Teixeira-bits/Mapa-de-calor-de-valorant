"""Convenience launcher script to run the Streamlit dashboard via standard Python command."""

from __future__ import annotations
import sys
import subprocess
import zipfile
from pathlib import Path


def ensure_data_extracted():
    """Extracts data.zip automatically if data/processed is missing."""
    root = Path(__file__).resolve().parent
    processed_summary = root / "data" / "processed" / "maps_summary.json"
    zip_path = root / "data.zip"

    if not processed_summary.exists() and zip_path.exists():
        print(f"📦 Base processada não encontrada. Extraindo '{zip_path.name}'...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(root)
        print("✅ Base de dados extraída com sucesso!\n")


def main():
    ensure_data_extracted()

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
