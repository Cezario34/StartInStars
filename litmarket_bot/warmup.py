import random
import time
from litmarket_bot.core.human import human_click

def warmup(page, mouse_pos):
    print("Начинаем прогрев...")

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
        print(f"Прогрев (книга): {e}")

    page.mouse.wheel(0, random.randint(200, 500))
    time.sleep(random.uniform(1.5, 3))
    print("Прогрев завершён")