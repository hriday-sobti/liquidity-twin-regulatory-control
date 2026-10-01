import subprocess
import sys


def main():
    print("Launching Liquidity Twin FastAPI Server on http://localhost:8000...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    subprocess.call(cmd)


if __name__ == "__main__":
    main()
