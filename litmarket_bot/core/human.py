import time
import random
from config import SHELVES, random_pause, log


def random_sleep(min_ms, max_ms):
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

def human_pause(short=False):
    """Случайная пауза: короткая или обычная"""
    if short or random.random() < 0.3:
        time.sleep(random.uniform(0.4, 1.1))
    else:
        time.sleep(random.uniform(1.2, 2.8))

def move_mouse(page, start_x, start_y, target_x, target_y):
    distance = ((target_x - start_x)**2 + (target_y - start_y)**2)**0.5
    steps = max(12, min(int(distance / 18), 50)) + random.randint(-3, 6)

    # Иногда делаем небольшую «ошибку» в траектории
    wobble = random.uniform(30, 80) if random.random() < 0.4 else random.uniform(10, 40)

    cx1 = start_x + (target_x - start_x) * random.uniform(0.2, 0.4) + random.uniform(-wobble, wobble)
    cy1 = start_y + (target_y - start_y) * random.uniform(0.2, 0.4) + random.uniform(-wobble, wobble)
    cx2 = start_x + (target_x - start_x) * random.uniform(0.6, 0.8) + random.uniform(-wobble, wobble)
    cy2 = start_y + (target_y - start_y) * random.uniform(0.6, 0.8) + random.uniform(-wobble, wobble)

    for i in range(1, steps + 1):
        t = i / steps
        x = ((1-t)**3 * start_x + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * target_x)
        y = ((1-t)**3 * start_y + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * target_y)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.002, 0.012))

    page.mouse.move(target_x, target_y)

def human_click(page, locator, mouse_pos, force=False):
    try:
        locator.scroll_into_view_if_needed()
        human_pause(short=True)

        box = locator.bounding_box()
        if not box:
            if force:
                locator.click(force=True)
            return

        # Иногда кликаем не точно в центр
        spread = 0.35 if random.random() < 0.7 else 0.15
        offset_x = random.uniform(-box["width"] * spread, box["width"] * spread)
        offset_y = random.uniform(-box["height"] * spread, box["height"] * spread)

        target_x = box["x"] + box["width"] / 2 + offset_x
        target_y = box["y"] + box["height"] / 2 + offset_y

        move_mouse(page, mouse_pos[0], mouse_pos[1], target_x, target_y)
        mouse_pos[0], mouse_pos[1] = target_x, target_y

        random_sleep(40, 180)
        page.mouse.down()
        random_sleep(25, 90)
        page.mouse.up()

        # Иногда делаем микро-движение после клика
        if random.random() < 0.25:
            page.mouse.move(target_x + random.randint(-8, 8), target_y + random.randint(-6, 6))

    except Exception as e:
        log.info(f"Ошибка клика: {e}")
        if force:
            try:
                locator.click(force=True)
            except:
                pass

def human_scroll(page, intensity="normal"):
    """Скролл с разной интенсивностью"""
    if intensity == "light":
        times = random.randint(1, 3)
        amount = (200, 500)
    elif intensity == "heavy":
        times = random.randint(4, 7)
        amount = (600, 1100)
    else:
        times = random.randint(2, 5)
        amount = (400, 850)

    for _ in range(times):
        page.mouse.wheel(0, random.randint(*amount))
        time.sleep(random.uniform(0.9, 2.4))

    # Иногда скроллим чуть назад
    if random.random() < 0.2:
        page.mouse.wheel(0, -random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1.2))

def human_type(page, locator, text, mouse_pos):
    human_click(page, locator, mouse_pos)
    random_sleep(130, 300)

    for i, char in enumerate(text):
        page.keyboard.type(char)
        if random.random() < 0.03 and i < len(text) - 1:
            page.keyboard.type(chr(random.randint(97, 122)))
            random_sleep(200, 400)
            page.keyboard.press("Backspace")
            random_sleep(100, 200)
        time.sleep(random.uniform(0.05, 0.12) if random.random() < 0.8 else random.uniform(0.15, 0.3))
