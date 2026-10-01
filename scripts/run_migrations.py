import subprocess
import sys


def main():
    print("Executing alembic database migrations...")
    subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])
    print("Database migrations successfully applied.")


if __name__ == "__main__":
    main()
