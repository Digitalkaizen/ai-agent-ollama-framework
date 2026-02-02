from datetime import datetime, timezone


def get_utc_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
