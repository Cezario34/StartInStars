import random
import time
from core.human import human_click, human_pause, human_scroll
from config import log
from pathlib import Path

TEXTS_DIR = Path("book_texts")
TEXTS_DIR.mkdir(exist_ok=True)

def save_page_text(page, book_slug: str, page_num: int):
    """Сохраняет текст текущей страницы"""
    try:
        paragraphs = page.locator("p[data-index]")
        count = paragraphs.count()
        if count == 0:
            return

        lines = []
        for i in range(count):
            text = paragraphs.nth(i).text_content()
            if text:
                text = text.strip()
                if text:
                    lines.append(text)

        if not lines:
            return

        book_dir = TEXTS_DIR / book_slug
        book_dir.mkdir(exist_ok=True)
        file_path = book_dir / f"page_{page_num}.txt"
        file_path.write_text("\n\n".join(lines), encoding="utf-8")
        log.info(f"Сохранён текст страницы {page_num} ({len(lines)} абзацев)")

    except Exception as e:
        log.info(f"Не удалось сохранить текст: {e}")


def close_payment_modal(page, mouse_pos):
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
    """Возвращает True, если книга платная (встретили модалку оплаты)"""
    log.info("Открываем читалку...")
    hit_paywall = False
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
            page_start = time.time()
            log.info(f"Страница {page_num}, читаем...")
            # Сохраняем текст страницы
            slug = book_url.rstrip("/").split("/books/")[-1]
            save_page_text(page, slug, page_num)
            human_scroll(page, intensity=random.choice(["normal", "heavy", "light"]))
            time.sleep(random.uniform(0.8, 1.8))

            if random.random() < 0.18:
                log.info("...думаем...")
                time.sleep(random.uniform(2.0, 4.5))

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.0, 2.0))

            elapsed = time.time() - page_start
            if elapsed < 60:
                wait = 60 - elapsed + random.uniform(0, 15)
                log.info(f"Дочитываем страницу ещё {wait:.0f} сек")
                time.sleep(wait)

            if close_payment_modal(page, mouse_pos):
                log.info("Была оплата — выходим из читалки")
                hit_paywall = True
                break

            handle_to_be_continue_button(page, mouse_pos)
            handle_reader_library_modal(page, mouse_pos)

            sub_btn = page.locator("button.chapter-nav__right").filter(has_text="Подписаться на автора").first
            if sub_btn.is_visible(timeout=2000):
                log.info("Нашли «Подписаться на автора», кликаем...")
                human_click(page, sub_btn, mouse_pos)
                human_pause()
                log.info("Подписались")
                break

            next_found = False
            for attempt in range(3):
                next_btn = page.locator(".chapter-nav__right").last
                if next_btn.count() > 0 and next_btn.is_visible(timeout=2000):
                    btn_text = (next_btn.text_content() or "").strip()[:40]
                    log.info(f"Кликаем правую кнопку (низ): [{btn_text}]")
                    human_click(page, next_btn, mouse_pos)
                    human_pause()
                    next_found = True
                    break

                log.info("Внизу нет, проверяем верх...")
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(random.uniform(0.8, 1.5))

                next_btn_top = page.locator(".chapter-nav__right").first
                if next_btn_top.count() > 0 and next_btn_top.is_visible(timeout=2000):
                    btn_text = (next_btn_top.text_content() or "").strip()[:40]
                    log.info(f"Кликаем правую кнопку (верх): [{btn_text}]")
                    human_click(page, next_btn_top, mouse_pos)
                    human_pause()
                    next_found = True
                    break

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
        log.error(f"Ошибка в читалке: {e}")
        try:
            page.goto(book_url, timeout=30000)
        except:
            pass

    return hit_paywall