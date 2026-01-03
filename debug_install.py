import sys
try:
    import pg8000
    with open("debug_status.txt", "w") as f:
        f.write(f"SUCCESS: pg8000 found at {pg8000.__file__}\n")
        f.write(f"Python: {sys.executable}\n")
except ImportError as e:
    with open("debug_status.txt", "w") as f:
        f.write(f"ERROR: {e}\n")
        f.write(f"Python: {sys.executable}\n")
        f.write(f"Path: {sys.path}\n")
except Exception as e:
    with open("debug_status.txt", "w") as f:
        f.write(f"EXCEPTION: {e}\n")
