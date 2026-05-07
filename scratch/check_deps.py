try:
    from flask_seasurf import SeaSurf
    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
