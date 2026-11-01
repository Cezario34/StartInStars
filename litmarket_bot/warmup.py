import random
import time
from litmarket_bot.core.human import human_click
from config import SHELVES, random_pause, log

def warmup(page, mouse_pos):
    log.info("Начинаем прогрев...")

    for _ in range(random.randint(2, 4)):
        page.mouse.wheel(0, random.randint(400, 900))
        time.sleep(random.uniform(1.2, 2.8))

    time.sleep(random.uniform(2, 4))

    try:
        book = page.locator("a[href*='/books/']").nth(random.randint(0, 5))
        if book.is_visible(timeout=4000):
            human_click(page, book, mouse_pos)
            time.sleep(random.uniform(3, 6))

            for _ in range(random.randint(1, 3)):
                page.mouse.wheel(0, random.randint(300, 700))
                time.sleep(random.uniform(1, 2.5))

            page.go_back()
            time.sleep(random.uniform(2, 4))
    except Exception as e:
        log.info(f"Прогрев (книга): {e}")

    page.mouse.wheel(0, random.randint(200, 500))
    time.sleep(random.uniform(1.5, 3))
    log.info("Прогрев завершён")

import random
import time
from core.human import human_click, human_scroll, human_pause
from config import log

def warmup_before_book(page, mouse_pos):
    """Случайный прогрев перед целевой книгой"""
    log.info("Прогрев перед книгой...")

    # Скроллим главную
    human_scroll(page, "normal")
    human_pause()

    # Иногда открываем случайную книгу
    if random.random() < 0.6:
        try:
            books = page.locator("a[href*='/books/']")
            count = books.count()
            if count > 3:
                idx = random.randint(0, min(count - 1, 8))
                book = books.nth(idx)
                if book.is_visible(timeout=3000):
                    log.info("Открываем случайную книгу для прогрева")
                    human_click(page, book, mouse_pos)
                    human_pause()
                    human_scroll(page, "light")
                    time.sleep(random.uniform(2, 4))
                    page.go_back()
                    human_pause()
        except Exception as e:
            log.info(f"Прогрев (книга): {e}")

    # Ещё немного скролла
    if random.random() < 0.4:
        human_scroll(page, "light")

    log.info("Прогрев завершён")