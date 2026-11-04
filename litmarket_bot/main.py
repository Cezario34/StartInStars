import argparse
import time
import random
import re
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright

from data.proxies import load_proxies
from data.accounts import load_accounts
from registration.registration import register_one
from actions.login import do_login
from actions.reader import go_through_reader
from actions.like import do_like
from actions.library import add_to_library
from actions.continuous import continuous_read, load_priority_books, priority_read_by, priority_lock
from core.browser import create_browser
from core.human import human_pause
from config import log, random_pause

books_read_counter = {"count": 0}
batch_lock = threading.Lock()

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

        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        random_pause(2.5, 4.0)

        go_through_reader(page, mouse_pos, book_url)
        result["reader"] = True

        page.wait_for_load_state("domcontentloaded")
        random_pause(2, 3)

        if random.random() < 0.4:
            log.info("Порядок: библиотека → лайк")
            add_to_library(page, mouse_pos)
            result["library"] = True
            human_pause()
            do_like(page, mouse_pos)
            result["like"] = True
        else:
            log.info("Порядок: лайк → библиотека")
            do_like(page, mouse_pos)
            result["like"] = True
            human_pause()
            add_to_library(page, mouse_pos)
            result["library"] = True

        log.info(f"Готово: {email}")

    except Exception as e:
        log.error(f"Ошибка на {email}: {e}")
    finally:
        browser.close()

    return result

def save_report(results):
    if not results:
        return
    report_file = Path("results.txt")
    with report_file.open("a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
        for r in results:
            status = " | ".join(f"{k}:{'OK' if v else 'FAIL'}" for k, v in r.items() if k != "email")
            f.write(f"{r['email']} → {status}\n")
    log.info(f"Отчёт сохранён в {report_file}")

def print_report(results):
    if not results:
        return
    log.info("=== ОТЧЁТ ===")
    for r in results:
        status = " | ".join(f"{k}:{'✓' if v else '✗'}" for k, v in r.items() if k != "email")
        log.info(f"{r['email']} → {status}")
    save_report(results)

def run_one(acc, proxy, book_url):
    with sync_playwright() as p:
        return run_actions(p, acc, proxy, book_url)

def continuous_wrapper(account, proxy, all_emails):
    with sync_playwright() as p:
        continuous_read(p, account, proxy, all_emails, books_read_counter, batch_lock)

def start_continuous_batched(accounts, proxies):
    all_emails = [acc["email"] for acc in accounts]
    batch_size = 5
    total = len(accounts)

    log.info(f"Всего аккаунтов: {total}, запуск партиями по {batch_size}")

    with ThreadPoolExecutor(max_workers=total) as executor:
        futures = []
        started = 0
        started_emails = []

        for i in range(min(batch_size, total)):
            acc = accounts[i]
            proxy = proxies[i % len(proxies)]
            futures.append(executor.submit(continuous_wrapper, acc, proxy, all_emails))
            started_emails.append(acc["email"])
            log.info(f"Запущен аккаунт {i+1}/{total}: {acc['email']}")
            time.sleep(random.uniform(2, 4))
        started = min(batch_size, total)

        while started < total:
            log.info("Ждём: 3 книги + все приоритетные...")

            while True:
                time.sleep(15)

                with batch_lock:
                    books_ok = books_read_counter["count"] >= 3

                priority = load_priority_books()
                priority_ok = True
                if priority:
                    with priority_lock:
                        for p_url in priority:
                            readers = priority_read_by.get(p_url, set())
                            if not readers.intersection(started_emails):
                                priority_ok = False
                                break

                if books_ok and priority_ok:
                    break

            with batch_lock:
                books_read_counter["count"] = 0

            next_end = min(started + batch_size, total)
            for i in range(started, next_end):
                acc = accounts[i]
                proxy = proxies[i % len(proxies)]
                futures.append(executor.submit(continuous_wrapper, acc, proxy, all_emails))
                started_emails.append(acc["email"])
                log.info(f"Запущен аккаунт {i+1}/{total}: {acc['email']}")
                time.sleep(random.uniform(2, 4))
            started = next_end

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log.error(f"Поток упал: {e}")

def interactive_mode(proxies):
    print("1 — Регистрация")
    print("2 — Логин + действия")
    print("3 — Непрерывное чтение")
    mode = input("Выбери режим: ").strip()

    if mode == "1":
        start = int(input("С какого: ") or "1")
        end = int(input("По какой: ") or "5")
        with sync_playwright() as p:
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

        log.info(f"Запускаем {len(to_run)} аккаунтов (параллельно)")
        results = []

        with ThreadPoolExecutor(max_workers=len(to_run)) as executor:
            futures = []
            for i, acc in enumerate(to_run):
                proxy = proxies[i % len(proxies)]
                futures.append(executor.submit(run_one, acc, proxy, book_url))
                time.sleep(random.uniform(1, 2))

            for future in as_completed(futures):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    log.error(f"Поток упал: {e}")

        print_report(results)

    elif mode == "3":
        accounts = load_accounts()
        if not accounts:
            log.error("Нет аккаунтов")
            return
        start_continuous_batched(accounts, proxies)

    else:
        log.error("Неверный режим")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["reg", "actions", "continuous"])
    parser.add_argument("--ids", help="ID аккаунтов через запятую")
    parser.add_argument("--book", help="Ссылка на книгу")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)
    args = parser.parse_args()

    proxies = load_proxies()
    if not proxies:
        log.error("Нет прокси")
        return

    if not args.mode:
        interactive_mode(proxies)
        return

    results = []

    if args.mode == "reg":
        with sync_playwright() as p:
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

        log.info(f"Запускаем {len(to_run)} аккаунтов (параллельно)")

        with ThreadPoolExecutor(max_workers=len(to_run)) as executor:
            futures = []
            for i, acc in enumerate(to_run):
                proxy = proxies[i % len(proxies)]
                futures.append(executor.submit(run_one, acc, proxy, args.book))
                time.sleep(random.uniform(1, 2))

            for future in as_completed(futures):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    log.error(f"Поток упал: {e}")

        print_report(results)

    elif args.mode == "continuous":
        accounts = load_accounts()
        if not accounts:
            log.error("Нет аккаунтов")
            return
        start_continuous_batched(accounts, proxies)

if __name__ == "__main__":
    main()