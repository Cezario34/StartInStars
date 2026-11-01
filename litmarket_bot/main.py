import argparse
import time
import random
import re
from playwright.sync_api import sync_playwright
from warmup import warmup_before_book

from data.proxies import load_proxies
from data.accounts import load_accounts
from registration.registration import register_one
from actions.login import do_login
from actions.reader import go_through_reader
from actions.like import do_like
from actions.library import add_to_library
from core.browser import create_browser
from config import log, random_pause

def run_actions(playwright, account, proxy, book_url):
    email = account["email"]
    log.info(f"Запуск: {email}")
    result = {"email": email, "login": False, "reader": False, "like": False, "library": False}

    browser, page, mouse_pos = create_browser(playwright, proxy, account)

    try:
        page.goto("https://litmarket.ru/", timeout=60000, wait_until="domcontentloaded")
        page.mouse.move(mouse_pos[0], mouse_pos[1])
        random_pause(1.2, 2.5)

        do_login(page, mouse_pos, email, account["password"])
        result["login"] = True

        # Прогрев
        warmup_before_book(page, mouse_pos)

        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        result["login"] = True

        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        random_pause(2.5, 4.0)

        go_through_reader(page, mouse_pos, book_url)
        result["reader"] = True

        page.wait_for_load_state("domcontentloaded")
        random_pause(2, 3)

        do_like(page, mouse_pos)
        result["like"] = True

        add_to_library(page, mouse_pos)
        result["library"] = True

        log.info(f"Готово: {email}")

    except Exception as e:
        log.error(f"Ошибка на {email}: {e}")
    finally:
        browser.close()

    return result

def interactive_mode(proxies):
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
                log.error("Аккаунты не найдены")
                return

            book_url = input("Ссылка на книгу: ").strip()
            if not book_url:
                log.error("Ссылка не указана")
                return

            log.info(f"Запускаем {len(to_run)} аккаунтов")
            results = []
            for i, acc in enumerate(to_run):
                proxy = proxies[i % len(proxies)]
                res = run_actions(p, acc, proxy, book_url)
                results.append(res)
                random_pause(3, 6)

            if results:
                log.info("=== ОТЧЁТ ===")
                for r in results:
                    status = " | ".join(f"{k}:{'✓' if v else '✗'}" for k, v in r.items() if k != "email")
                    log.info(f"{r['email']} → {status}")

        else:
            log.error("Неверный режим")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["reg", "actions"])
    parser.add_argument("--ids", help="ID аккаунтов через запятую")
    parser.add_argument("--book", help="Ссылка на книгу")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)
    args = parser.parse_args()

    proxies = load_proxies()
    if not proxies:
        log.error("Нет прокси")
        return

    # Если аргументы не переданы — интерактивный режим
    if not args.mode:
        interactive_mode(proxies)
        return

    results = []

    with sync_playwright() as p:
        if args.mode == "reg":
            for num in range(args.start, args.end + 1):
                if num - 1 >= len(proxies):
                    break
                register_one(p, proxies[num - 1], num)
                random_pause(4, 8)

        elif args.mode == "actions":
            if not args.ids or not args.book:
                log.error("Для actions нужны --ids и --book")
                return

            accounts = load_accounts()
            target_ids = [x.strip() for x in args.ids.split(",")]
            to_run = [acc for acc in accounts if acc["id"] in target_ids]

            if not to_run:
                log.error("Аккаунты не найдены")
                return

            log.info(f"Запускаем {len(to_run)} аккаунтов")
            for i, acc in enumerate(to_run):
                proxy = proxies[i % len(proxies)]
                res = run_actions(p, acc, proxy, args.book)
                results.append(res)
                random_pause(3, 6)

    if results:
        log.info("=== ОТЧЁТ ===")
        for r in results:
            status = " | ".join(f"{k}:{'✓' if v else '✗'}" for k, v in r.items() if k != "email")
            log.info(f"{r['email']} → {status}")

if __name__ == "__main__":
    main()