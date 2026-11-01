import random
import time
from core.human import human_click, human_pause, human_scroll
from config import SHELVES, random_pause, log

def close_payment_modal(page, mouse_pos):
    """Закрывает модалку оплаты, если она появилась"""
    try:
        title = page.locator("h2:has-text('Оплата'), .lmSimpleModal__title:has-text('Оплата')").first
        if not title.is_visible(timeout=1500):
            return False

        log.info("Появилась модалка оплаты, закрываем...")
        close_btn = page.locator("button[aria-label='Закрыть окно']").first
        if close_btn.is_visible(timeout=2000):
            human_click(page, close_btn, mouse_pos)
            human_pause(short=True)
            log.info("Модалка оплаты закрыта")
            return True
    except:
        pass
    return False

def handle_reader_library_modal(page, mouse_pos):
    """Если в читалке появилась модалка «Добавьте на полку» — кликаем по полке"""
    try:
        modal = page.locator(".library-modal, .reader-modal.library-modal").first
        if not modal.is_visible(timeout=2000):
            return False

        log.info("В читалке появилась модалка библиотеки, выбираем полку...")
        shelves = ["Прочитать", "Читаю", "Прочитано", "Избранное"]
        shelf = random.choice(shelves)

        shelf_btn = page.locator(f".shelve-button:has-text('{shelf}')").first
        if shelf_btn.count() == 0:
            shelf_btn = page.locator(".shelve-button").first

        if shelf_btn.is_visible(timeout=3000):
            human_click(page, shelf_btn, mouse_pos)
            human_pause(short=True)
            log.info(f"Из читалки добавили на полку: {shelf}")
            return True
    except:
        pass
    return False

def handle_to_be_continue_button(page, mouse_pos):
    """Кнопка «Добавить в библиотеку» в блоке to-be-continue"""
    try:
        btn = page.locator(".to-be-continue_btn, button.to-be-continue_btn").first
        if not btn.is_visible(timeout=2000):
            return False

        log.info("Нашли кнопку «Добавить в библиотеку» в читалке, кликаем...")
        human_click(page, btn, mouse_pos)
        human_pause()

        modal = page.locator(".library-modal, .library-window, .modal-dialog").first
        if modal.is_visible(timeout=4000):
            shelves = ["Прочитать", "Читаю", "Прочитано", "Избранное"]
            shelf = random.choice(shelves)
            shelf_btn = page.locator(f".shelve-button:has-text('{shelf}')").first
            if shelf_btn.count() == 0:
                shelf_btn = page.locator(".shelve-button").first

            if shelf_btn.is_visible(timeout=3000):
                human_click(page, shelf_btn, mouse_pos)
                human_pause(short=True)
                log.info(f"Из to-be-continue добавили на полку: {shelf}")
                return True
    except:
        pass
    return False

def go_through_reader(page, mouse_pos, book_url):
    log.info("Открываем читалку...")
    try:
        opened = False
        try:
            read_link = page.locator("a[href*='/reader/']").filter(has_text="Читать").first
            if read_link.is_visible(timeout=6000):
                human_click(page, read_link, mouse_pos)
                human_pause()
                if "/reader/" in page.url:
                    opened = True
                    log.info("Читалка открылась кликом")
        except:
            pass

        if not opened:
            reader_url = book_url.replace("/books/", "/reader/") + "?page=1"
            log.info(f"Читалка не открылась, идём принудительно: {reader_url}")
            page.goto(reader_url, timeout=60000, wait_until="domcontentloaded")
            human_pause()

        max_pages = 12
        for page_num in range(1, max_pages + 1):
            log.info(f"Страница {page_num}, читаем...")

            # Человеческий скролл
            human_scroll(page, intensity=random.choice(["normal", "heavy", "light"]))
            time.sleep(random.uniform(0.8, 1.8))

            # Иногда пауза «на подумать»
            if random.random() < 0.18:
                log.info("...думаем...")
                time.sleep(random.uniform(2.0, 4.5))

            # Доскролл в низ
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.0, 2.0))

            # Закрываем модалку оплаты — если была, выходим
            if close_payment_modal(page, mouse_pos):
                log.info("Была оплата — выходим из читалки")
                break

            # Кнопка to-be-continue
            handle_to_be_continue_button(page, mouse_pos)

            # Модалка библиотеки
            handle_reader_library_modal(page, mouse_pos)

            # Подписка
            sub_btn = page.locator("button.chapter-nav__right").filter(has_text="Подписаться на автора").first
            if sub_btn.is_visible(timeout=2000):
                log.info("Нашли «Подписаться на автора», кликаем...")
                human_click(page, sub_btn, mouse_pos)
                human_pause()
                log.info("Подписались")
                break

            # Правая кнопка (далее / следующая глава)
            next_found = False
            for attempt in range(3):
                next_btn = page.locator(".chapter-nav__right").last
                if next_btn.count() > 0 and next_btn.is_visible(timeout=3000):
                    btn_text = (next_btn.text_content() or "").strip()[:40]
                    log.info(f"Кликаем правую кнопку: [{btn_text}]")
                    human_click(page, next_btn, mouse_pos)
                    human_pause()
                    next_found = True
                    break
                else:
                    log.info(f"Правая кнопка не найдена (попытка {attempt + 1}/3), обновляем...")
                    page.reload(wait_until="domcontentloaded")
                    human_pause()
                    human_scroll(page, "normal")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.2)

            if not next_found:
                log.info("Правая кнопка так и не появилась — конец или ошибка")
                break

        log.info("Возвращаемся на страницу книги по URL...")
        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        human_pause()

    except Exception as e:
        log.info(f"Ошибка в читалке: {e}")
        try:
            page.goto(book_url, timeout=30000)
        except:
            pass