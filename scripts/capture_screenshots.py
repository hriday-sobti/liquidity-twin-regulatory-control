"""
Capture high-resolution screenshots of Liquidity Twin dashboard views.
"""

import os
import subprocess
import time
from PIL import Image

CHROME_BIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://127.0.0.1:5173"
OUT_DIR = os.path.abspath("docs/assets/screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

VIEWS = [
    ("overview", "01_overview.png"),
    ("movement", "02_movement_explorer.png"),
    ("lineage", "03_lineage_audit.png"),
    ("scenarios", "04_scenario_lab.png"),
    ("controls", "05_controls_catalog.png"),
    ("close", "06_close_workspace.png"),
    ("reporting", "07_reporting_packs.png"),
    ("queries", "08_query_workbench.png"),
    ("copilot", "09_analyst_copilot.png"),
    ("benchmark", "10_public_benchmark.png"),
]

for section, filename in VIEWS:
    out_file = os.path.join(OUT_DIR, filename)
    url = f"{BASE_URL}/#{section}"
    print(f"Capturing {section} -> {filename}...")
    
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1440,920",
        "--virtual-time-budget=4000",
        f"--screenshot={out_file}",
        url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(out_file):
        sz = os.path.getsize(out_file)
        img = Image.open(out_file)
        print(f"  Done: {sz:,} bytes | {img.size}")
    else:
        print(f"  Failed: {res.stderr}")

print("All screenshots captured.")
