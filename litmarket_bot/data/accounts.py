from pathlib import Path
from config import SHELVES, random_pause, log


ACCOUNTS_FILE = Path("data/accounts.txt")

def load_accounts():
    accounts = []
    if not ACCOUNTS_FILE.exists():
        log.info("Ошибка: accounts.txt не найден")
        return accounts

    for line in ACCOUNTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 6:
            accounts.append({
                "id": parts[0],
                "email": parts[1],
                "password": parts[2],
                "ua": parts[3],
                "width": int(parts[4]),
                "height": int(parts[5])
            })
        else:
            log.info(f"Пропущена строка: {line}")
    return accounts