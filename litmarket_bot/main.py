import re
import time
import random
from playwright.sync_api import sync_playwright

from data.proxies import load_proxies
from data.accounts import load_accounts
from registration.registration import register_one
from actions.login import do_login
from actions.reader import go_through_reader
from actions.like import do_like
from actions.library import add_to_library
from core.browser import create_browser
from config import random_pause, PAUSE_LONG

def run_actions(playwright, account, proxy, book_url):
    email = account["email"]
    print(f"\nЗапуск: {email}")

    browser, page, mouse_pos = create_browser(playwright, proxy, account)

    try:
        print("Открываем главную...")
        page.goto("https://litmarket.ru/", timeout=60000, wait_until="domcontentloaded")
        page.mouse.move(mouse_pos[0], mouse_pos[1])
        random_pause(1.2, 2.5)

        do_login(page, mouse_pos, email, account["password"])

        print(f"Переходим на книгу: {book_url}")
        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        random_pause(2.5, 4.5)
        print("Страница книги открыта")

        page.mouse.wheel(0, random.randint(200, 500))
        random_pause(1, 2)

        go_through_reader(page, mouse_pos, book_url)

        print("Возвращаемся на страницу книги...")
        page.wait_for_load_state("domcontentloaded")
        random_pause(2, 3.5)

        do_like(page, mouse_pos)
        add_to_library(page, mouse_pos)

        print(f"Готово: {email}")

    except Exception as e:
        print(f"Ошибка на {email}: {e}")
    finally:
        browser.close()

def main():
    proxies = load_proxies()
    if not proxies:
        print("Нет прокси")
        return

    print("1 — Регистрация")
    print("2 — Логин + действия")
    mode = input("Выбери режим: ").strip()

    with sync_playwright() as p:
        if mode == "1":
            start = int(input("С какого: ") or "1")
            end = int(input("По какой: ") or "5")
            for num in range(start, end + 1):
                if num - 1 >= len(proxies):
                    break
                register_one(p, proxies[num - 1], num)
                random_pause(4, 8)

        elif mode == "2":
            accounts = load_accounts()
            ids_input = input("ID аккаунтов через пробел/запятую: ")
            target_ids = [x.strip() for x in re.split(r"[,\s]+", ids_input) if x.strip()]

            to_run = [acc for acc in accounts if acc["id"] in target_ids]
            if not to_run:
                print("Аккаунты не найдены")
                return

            book_url = input("Ссылка на книгу: ").strip()
            if not book_url:
                print("Ссылка не указана")
                return

            print(f"Запускаем {len(to_run)} аккаунтов на книгу: {book_url}")
            for i, acc in enumerate(to_run):
                proxy = proxies[i % len(proxies)]
                run_actions(p, acc, proxy, book_url)
                random_pause(3, 6)

        else:
            print("Неверный режим")

if __name__ == "__main__":
    main()