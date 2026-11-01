import random
import logging
# Таймауты
PAGE_TIMEOUT = 60000
ELEMENT_TIMEOUT = 10000
SHORT_TIMEOUT = 3000

# Чтение
MAX_READER_PAGES = 12
SCROLLS_PER_PAGE = (3, 5)
SCROLL_AMOUNT = (500, 900)

# Паузы (секунды)
PAUSE_SHORT = (0.8, 1.8)
PAUSE_MEDIUM = (1.5, 3.0)
PAUSE_LONG = (2.5, 4.5)

# Полки
SHELVES = ["Читаю", "Прочитать", "Прочитано", "Избранное"]

# Браузер
LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars"
]

def random_pause(min_s, max_s):
    import time
    time.sleep(random.uniform(min_s, max_s))

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    return logging.getLogger("litmarket")

log = setup_logging()