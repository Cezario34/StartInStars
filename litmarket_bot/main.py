import re
import time
import random
from playwright.sync_api import sync_playwright

from proxies import load_proxies
from accounts import load_accounts
from registration import register_one
from login_actions import run_login_actions

def main():
    proxies = load_proxies()
    if not proxies:
        print("Нет прокси")
        return

    print("1 — Регистрация")
    print("2 — Логин + действия (лайк/библиотека)")
    mode = input("Выбери режим: ").strip()

    with sync_playwright() as p:
        if mode == "1":
            start = int(input("С какого: ") or "1")
            end = int(input("По какой: ") or "5")
            for num in range(start, end + 1):
                if num - 1 >= len(proxies):
                    break
                register_one(p, proxies[num - 1], num)
                time.sleep(random.uniform(4, 8))

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
                run_login_actions(p, acc, proxy, book_url)
                time.sleep(random.uniform(3, 6))

        else:
            print("Неверный режим")

if __name__ == "__main__":
    main()