import random
import time
from core.human import human_click
from config import SHELVES, random_pause, log


def add_to_library(page, mouse_pos):
    log.info("--- Библиотека ---")
    try:
        # Ждём появления блока библиотеки
        page.locator(".library-button, .btn-library").first.wait_for(timeout=12000)
        random_pause(0.6, 1.2)

        # Читаем текст кнопки
        btn = page.locator(".btn-library").first
        btn_text = ""
        if btn.count() > 0:
            btn_text = (btn.text_content() or "").strip()
        log.info(f"Текст кнопки: [{btn_text}]")

        # Уже в библиотеке?
        already = any(word in btn_text.lower() for word in ["библиотеке", "читаю", "прочитано", "избранн"])
        if already:
            log.info("Книга уже в библиотеке — пропускаем")
            return

        # Ищем кнопку добавления
        add_btn = page.locator(".btn-library").filter(has_text="В библиотеку").first
        if add_btn.count() == 0 or not add_btn.is_visible(timeout=4000):
            log.info("Кнопка «В библиотеку» не найдена")
            return

        log.info("Кликаем «В библиотеку»...")
        # Человеческий клик
        human_click(page, add_btn, mouse_pos)
        random_pause(1.5, 2.3)

        # Проверяем модалку
        modal = page.locator(".library-window, .library-modal, .modal-dialog").first
        modal_opened = False

        try:
            modal.wait_for(state="visible", timeout=4000)
            modal_opened = True
            log.info("Модалка полок открылась")
        except:
            log.info("Человеческий клик не открыл модалку, пробуем прямой...")
            try:
                add_btn.click(force=True)
                random_pause(1.5, 2.3)
                modal.wait_for(state="visible", timeout=5000)
                modal_opened = True
                log.info("Модалка открылась прямым кликом")
            except:
                log.info("Модалка так и не появилась")
                return

        if not modal_opened:
            return

        # Выбираем полку
        shelf = random.choice(SHELVES)
        log.info(f"Выбираем полку: {shelf}")

        shelf_btn = None
        selectors = [
            f"button[data-shelf-name='{shelf}']",
            f".shelve-button:has-text('{shelf}')",
            f".library-window button:has-text('{shelf}')",
            f"button:has-text('{shelf}')"
        ]

        for sel in selectors:
            candidate = page.locator(sel).first
            if candidate.count() > 0 and candidate.is_visible(timeout=2000):
                shelf_btn = candidate
                break

        if not shelf_btn:
            log.info("Кнопка полки не найдена")
            texts = page.locator(".library-window button, .shelve-button").all_text_contents()
            log.info(f"Доступные кнопки: {texts}")
            return

        human_click(page, shelf_btn, mouse_pos)
        random_pause(1.2, 2.0)
        log.info(f"Книга добавлена на полку: {shelf}")

    except Exception as e:
        log.info(f"Ошибка библиотеки: {e}")