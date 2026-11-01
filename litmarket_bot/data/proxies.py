from pathlib import Path
from config import SHELVES, random_pause, log

PROXIES_FILE = Path("data/proxies.txt")

def load_proxies():
    proxies = []
    if not PROXIES_FILE.exists():
        log.info("Ошибка: proxies.txt не найден")
        return proxies

    for line in PROXIES_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) == 4:
            proxies.append({
                "server": f"http://{parts[0]}:{parts[1]}",
                "username": parts[2],
                "password": parts[3],
                "ip_port": f"{parts[0]}:{parts[1]}"
            })
        else:
            log.info(f"Пропущена строка: {line}")
    return proxies