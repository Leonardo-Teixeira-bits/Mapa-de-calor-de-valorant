"""Convenience launcher script to run the Streamlit dashboard via standard Python command."""

from __future__ import annotations
import sys
import subprocess
from pathlib import Path


def ensure_data_ready():
    project_root = Path(__file__).resolve().parent
    processed_dir = project_root / "data" / "processed"
    events_path = processed_dir / "processed_events.parquet"
    zip_path = project_root / "data.zip"

    if (not processed_dir.exists() or not events_path.exists()) and zip_path.exists():
        print("=" * 60)
        print("  Detectado data.zip! Extraindo base de dados e artefatos...")
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(project_root)
        print("  Dados descompactados com sucesso na pasta data/.")
        print("=" * 60)


def main():
    ensure_data_ready()
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
