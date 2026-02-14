#!/usr/bin/env python3


import subprocess
import sys
import importlib

REQUIRED_MODULES = [
    "requests",
    "colorama"
]

def install(package):
    print(f"[+] Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install():
    print("=== Dependency Checker ===\n")

    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
            print(f"[OK] {module} already installed")
        except ImportError:
            print(f"[MISSING] {module}")
            install(module)

    print("\nAll dependencies ready.")

if __name__ == "__main__":
    check_and_install()
