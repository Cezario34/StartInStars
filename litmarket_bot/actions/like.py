import random
import time
from litmarket_bot.core.human import human_click

def close_like_modal(page, mouse_pos):
    """Закрывает модалку после лайка. Пробует несколько раз."""
    for attempt in range(3):
        try:
            # Основной селектор
            close_btn = page.locator("button[aria-label='Закрыть окно']").first
            if close_btn.is_visible(timeout=3000):
                print(f"Закрываем модалку (попытка {attempt + 1})...")
                human_click(page, close_btn, mouse_pos)
                time.sleep(random.uniform(1, 1.8))

                # Проверяем, закрылась ли
                if not close_btn.is_visible(timeout=2000):
                    print("Модалка закрыта")
                    return True
            else:
                time.sleep(1)
        except:
            time.sleep(1)

    # Запасной вариант — Escape
    try:
        print("Пробуем закрыть через Escape...")
        page.keyboard.press("Escape")
        time.sleep(1)
    except:
        pass

    print("Модалка не закрылась или не появилась")
    return False

def do_like(page, mouse_pos):
    print("--- Лайк ---")
    try:
        page.locator("button.like-button").first.wait_for(state="attached", timeout=12000)
        time.sleep(random.uniform(0.8, 1.5))

        page.evaluate("window.scrollTo(0, 400)")
        time.sleep(1)

        buttons = page.locator("button.like-button.js_like-button")
        count = buttons.count()
        print(f"Кнопок лайка в DOM: {count}")

        clicked = False
        for i in range(count):
            btn = buttons.nth(i)
            box = btn.bounding_box()
            if box and box["width"] > 0 and box["height"] > 0:
                aria = btn.get_attribute("aria-pressed")
                print(f"Видимая кнопка #{i}, aria={aria}")
                if aria == "true":
                    print("Лайк уже стоит")
                    return
                human_click(page, btn, mouse_pos)
                time.sleep(random.uniform(1.8, 2.8))
                clicked = True
                break

        if not clicked and count > 0:
            print("Видимых нет, пробуем принудительно...")
            try:
                buttons.nth(count - 1).click(force=True)
                time.sleep(2)
                clicked = True
            except Exception as e:
                print(f"Принудительный клик не удался: {e}")

        if clicked:
            close_like_modal(page, mouse_pos)
            # Дополнительная пауза после закрытия
            time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"Ошибка лайка: {e}")