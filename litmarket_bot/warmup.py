import random
import time
from core.human import human_click, human_scroll, human_pause
from config import log


def is_real_book(href: str) -> bool:
    if not href or "/books/" not in href:
        return False
    if any(x in href for x in ["/genres/", "/tags/", "/cycles/", "/authors/"]):
        return False
    slug = href.rstrip("/").split("/books/")[-1]
    return bool(slug and "/" not in slug and "?" not in slug and len(slug) > 3)


def warmup_before_book(page, mouse_pos):
    log.info("Прогрев перед книгой...")

    human_scroll(page, "normal")
    human_pause()

    if random.random() < 0.5:
        try:
            books = page.locator("a[href*='/books/']")
            count = books.count()

            valid = []
            for i in range(min(count, 25)):
                b = books.nth(i)
                href = b.get_attribute("href") or ""
                if is_real_book(href) and b.is_visible():
                    valid.append(b)

            if valid:
                book = random.choice(valid[:8])
                log.info("Открываем случайную книгу для прогрева")
                human_click(page, book, mouse_pos)
                human_pause()
                human_scroll(page, "light")
                time.sleep(random.uniform(2, 4))
                page.go_back()
                human_pause()
        except Exception as e:
            log.info(f"Прогрев: {e}")

    if random.random() < 0.3:
        human_scroll(page, "light")

    log.info("Прогрев завершён")