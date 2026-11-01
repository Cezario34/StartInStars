import time
import random

def random_sleep(min_ms, max_ms):
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

def move_mouse(page, start_x, start_y, target_x, target_y):
    distance = ((target_x - start_x)**2 + (target_y - start_y)**2)**0.5
    steps = max(15, min(int(distance / 15), 45)) + random.randint(0, 5)

    cx1 = start_x + (target_x - start_x) * 0.3 + random.uniform(-50, 50)
    cy1 = start_y + (target_y - start_y) * 0.3 + random.uniform(-50, 50)
    cx2 = start_x + (target_x - start_x) * 0.7 + random.uniform(-50, 50)
    cy2 = start_y + (target_y - start_y) * 0.7 + random.uniform(-50, 50)

    for i in range(1, steps + 1):
        t = i / steps
        x = ((1-t)**3 * start_x + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * target_x)
        y = ((1-t)**3 * start_y + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * target_y)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.003, 0.008))

    page.mouse.move(target_x, target_y)

def human_click(page, locator, mouse_pos):
    try:
        locator.scroll_into_view_if_needed()
        random_sleep(150, 300)
        box = locator.bounding_box()
        if not box:
            print("Не найден bounding box")
            return

        offset_x = random.randint(-int(box["width"]/4), int(box["width"]/4)) if box["width"] > 20 else 0
        offset_y = random.randint(-int(box["height"]/4), int(box["height"]/4)) if box["height"] > 20 else 0

        target_x = box["x"] + box["width"]/2 + offset_x
        target_y = box["y"] + box["height"]/2 + offset_y

        move_mouse(page, mouse_pos[0], mouse_pos[1], target_x, target_y)
        mouse_pos[0], mouse_pos[1] = target_x, target_y

        random_sleep(50, 160)
        page.mouse.down()
        random_sleep(30, 110)
        page.mouse.up()
    except Exception as e:
        print(f"Ошибка клика: {e}")

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