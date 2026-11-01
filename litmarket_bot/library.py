import random
import time
from human import human_click

def add_to_library(page, mouse_pos):
    print("--- Библиотека ---")
    try:
        lib_area = page.locator(".library-button, .btn-library").first
        lib_area.wait_for(timeout=10000)
        time.sleep(random.uniform(0.5, 1))

        btn = page.locator(".btn-library").first
        btn_text = btn.text_content().strip() if btn.count() > 0 else ""
        print(f"Текст кнопки библиотеки: [{btn_text}]")

        if "библиотеке" in btn_text.lower() or "читаю" in btn_text.lower() or "прочитано" in btn_text.lower():
            print("Книга уже в библиотеке, пропускаем")
            return

        add_btn = page.locator(".btn-library").filter(has_text="В библиотеку").first
        if add_btn.count() == 0 or not add_btn.is_visible(timeout=3000):
            print("Кнопка «В библиотеку» не найдена")
            return

        print("Кликаем «В библиотеку»...")
        # Сначала человеческий клик
        human_click(page, add_btn, mouse_pos)
        time.sleep(random.uniform(1.5, 2.2))

        # Проверяем, открылась ли модалка
        modal = page.locator(".library-window, .modal-dialog").first
        modal_opened = False
        try:
            modal.wait_for(state="visible", timeout=3000)
            modal_opened = True
            print("Меню полок открылось")
        except:
            print("Человеческий клик не сработал, пробуем прямой...")
            # Запасной прямой клик
            try:
                add_btn.click(force=True)
                time.sleep(random.uniform(1.5, 2.2))
                modal.wait_for(state="visible", timeout=4000)
                modal_opened = True
                print("Меню полок открылось (прямой клик)")
            except:
                print("Модалка полок так и не появилась")
                return

        if not modal_opened:
            return

        # Выбираем полку
        shelves = ["Читаю", "Прочитать", "Прочитано", "Избранное"]
        shelf = random.choice(shelves)

        shelf_btn = page.locator(f"button[data-shelf-name='{shelf}']").first
        if shelf_btn.count() == 0:
            shelf_btn = page.locator(f".library-window button:has-text('{shelf}')").first
        if shelf_btn.count() == 0:
            shelf_btn = page.locator(f"button:has-text('{shelf}')").first

        try:
            shelf_btn.wait_for(state="visible", timeout=4000)
            print(f"Выбираем полку: {shelf}")
            human_click(page, shelf_btn, mouse_pos)
            time.sleep(1.5)
            print(f"Добавлено на полку: {shelf}")
        except Exception as e:
            print(f"Не удалось выбрать полку: {e}")
            texts = page.locator(".library-window button").all_text_contents()
            print(f"Кнопки в модалке: {texts}")

    except Exception as e:
        print(f"Ошибка библиотеки: {e}")