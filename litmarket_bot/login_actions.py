import random
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from human import human_click, human_type, random_sleep
from reader import go_through_reader
from like import do_like
from library import add_to_library

def run_login_actions(playwright, account, proxy, book_url):
    email = account["email"]
    print(f"\nЗапуск: {email}")

    browser = playwright.chromium.launch(
        headless=False,
        proxy={
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"]
        },
        args=["--disable-blink-features=AutomationControlled", "--disable-infobars"]
    )

    context = browser.new_context(
        user_agent=account["ua"],
        viewport={"width": account["width"], "height": account["height"]},
        extra_http_headers={
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": "\"Windows\""
        }
    )

    page = context.new_page()
    mouse_pos = [random.randint(100, account["width"] - 100),
                 random.randint(100, account["height"] - 100)]

    try:
        print("Открываем главную...")
        page.goto("https://litmarket.ru/", timeout=60000, wait_until="domcontentloaded")
        page.mouse.move(mouse_pos[0], mouse_pos[1])
        time.sleep(random.uniform(1.2, 2.5))

        print("Логинимся...")
        human_click(page, page.locator(".login-btn").first, mouse_pos)
        human_type(page, page.locator("input[name='email']").first, email, mouse_pos)
        human_type(page, page.locator("input[name='password']").first, account["password"], mouse_pos)
        random_sleep(250, 500)
        human_click(page, page.locator(".authLoginButton").first, mouse_pos)

        page.locator("a[href='#userPages'] .user-avatar").first.wait_for(timeout=15000)
        print(f"Успешный вход: {email}")
        time.sleep(random.uniform(1.5, 3))

        print(f"Переходим на книгу: {book_url}")
        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        time.sleep(random.uniform(2.5, 4.5))
        print("Страница книги открыта")

        # Небольшой прогрев на странице книги
        page.mouse.wheel(0, random.randint(200, 500))
        time.sleep(random.uniform(1, 2))

        go_through_reader(page, mouse_pos, book_url)

        # Ждём, пока страница книги полностью восстановится после возврата
        print("Возвращаемся на страницу книги...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(random.uniform(2, 3.5))

        do_like(page, mouse_pos)
        add_to_library(page, mouse_pos)

        print(f"Готово: {email}")

    except Exception as e:
        print(f"Ошибка на {email}: {e}")
    finally:
        browser.close()