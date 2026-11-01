import random
import time
from human import human_click

def close_payment_modal(page, mouse_pos):
    """Закрывает модалку оплаты, если она появилась"""
    try:
        title = page.locator("h2:has-text('Оплата'), .lmSimpleModal__title:has-text('Оплата')").first
        if not title.is_visible(timeout=1500):
            return False

        print("Появилась модалка оплаты, закрываем...")
        close_btn = page.locator("button[aria-label='Закрыть окно']").first
        if close_btn.is_visible(timeout=2000):
            human_click(page, close_btn, mouse_pos)
            time.sleep(random.uniform(0.8, 1.5))
            print("Модалка оплаты закрыта")
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

        print("В читалке появилась модалка библиотеки, выбираем полку...")
        shelves = ["Прочитать", "Читаю", "Прочитано", "Избранное"]
        shelf = random.choice(shelves)

        shelf_btn = page.locator(f".shelve-button:has-text('{shelf}')").first
        if shelf_btn.count() == 0:
            shelf_btn = page.locator(".shelve-button").first

        if shelf_btn.is_visible(timeout=3000):
            human_click(page, shelf_btn, mouse_pos)
            time.sleep(random.uniform(1, 1.8))
            print(f"Из читалки добавили на полку: {shelf}")
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

        print("Нашли кнопку «Добавить в библиотеку» в читалке, кликаем...")
        human_click(page, btn, mouse_pos)
        time.sleep(random.uniform(1.5, 2.5))

        modal = page.locator(".library-modal, .library-window, .modal-dialog").first
        if modal.is_visible(timeout=4000):
            shelves = ["Прочитать", "Читаю", "Прочитано", "Избранное"]
            shelf = random.choice(shelves)
            shelf_btn = page.locator(f".shelve-button:has-text('{shelf}')").first
            if shelf_btn.count() == 0:
                shelf_btn = page.locator(".shelve-button").first

            if shelf_btn.is_visible(timeout=3000):
                human_click(page, shelf_btn, mouse_pos)
                time.sleep(random.uniform(1, 1.8))
                print(f"Из to-be-continue добавили на полку: {shelf}")
                return True
    except:
        pass
    return False

def go_through_reader(page, mouse_pos, book_url):
    print("Открываем читалку...")
    try:
        opened = False
        try:
            read_link = page.locator("a[href*='/reader/']").filter(has_text="Читать").first
            if read_link.is_visible(timeout=6000):
                human_click(page, read_link, mouse_pos)
                time.sleep(random.uniform(2.5, 4))
                if "/reader/" in page.url:
                    opened = True
                    print("Читалка открылась кликом")
        except:
            pass

        if not opened:
            reader_url = book_url.replace("/books/", "/reader/") + "?page=1"
            print(f"Читалка не открылась, идём принудительно: {reader_url}")
            page.goto(reader_url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 3.5))

        max_pages = 12
        for page_num in range(1, max_pages + 1):
            print(f"Страница {page_num}, скроллим вниз...")

            for _ in range(random.randint(3, 5)):
                page.mouse.wheel(0, random.randint(500, 900))
                time.sleep(random.uniform(1.2, 2.2))

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.8, 2.8))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

            # Закрываем модалку оплаты — если была, выходим из читалки
            if close_payment_modal(page, mouse_pos):
                print("Была оплата — выходим из читалки")
                break

            # Кнопка to-be-continue
            handle_to_be_continue_button(page, mouse_pos)

            # Модалка библиотеки в читалке
            handle_reader_library_modal(page, mouse_pos)

            # Подписка
            sub_btn = page.locator("button.chapter-nav__right").filter(has_text="Подписаться на автора").first
            if sub_btn.is_visible(timeout=2000):
                print("Нашли «Подписаться на автора», кликаем...")
                human_click(page, sub_btn, mouse_pos)
                time.sleep(random.uniform(1.5, 2.5))
                print("Подписались")
                break

            # Далее / следующая глава (универсально — правая кнопка)
            next_found = False
            for attempt in range(3):
                next_btn = page.locator(".chapter-nav__right").last
                if next_btn.count() > 0 and next_btn.is_visible(timeout=3000):
                    btn_text = next_btn.text_content().strip()[:40]
                    print(f"Кликаем правую кнопку: [{btn_text}]")
                    human_click(page, next_btn, mouse_pos)
                    time.sleep(random.uniform(2.2, 3.5))
                    next_found = True
                    break
                else:
                    print(f"Правая кнопка не найдена (попытка {attempt + 1}/3), обновляем...")
                    page.reload(wait_until="domcontentloaded")
                    time.sleep(random.uniform(2, 3))
                    for _ in range(3):
                        page.mouse.wheel(0, 700)
                        time.sleep(0.8)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.5)

            if not next_found:
                print("Правая кнопка так и не появилась — конец или ошибка")
                break

        print("Возвращаемся на страницу книги по URL...")
        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 3.5))

    except Exception as e:
        print(f"Ошибка в читалке: {e}")
        try:
            page.goto(book_url, timeout=30000)
        except:
            pass