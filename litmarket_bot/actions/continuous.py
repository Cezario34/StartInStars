import random
import time
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

from core.human import human_pause, human_scroll
from actions.reader import go_through_reader
from actions.like import do_like
from actions.library import add_to_library
from config import log

MSK = timezone(timedelta(hours=3))
PRIORITY_FILE = Path("priority_books.txt")
BLACKLIST_FILE = Path("blacklist.txt")
PAID_FILE = Path("paid_books.txt")

priority_lock = threading.Lock()
priority_read_by = {}

EXCLUDE_SLUGS = {
    "ebooks", "audiobooks", "audio", "genres", "tags", "cycles",
    "authors", "free", "new", "popular", "bestsellers"
}

def is_night():
    now = datetime.now(MSK)
    return 1 <= now.hour < 8

def load_priority_books():
    if not PRIORITY_FILE.exists():
        return []
    books = []
    for line in PRIORITY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and line.startswith("http"):
            books.append(line)
    return books

def load_blacklist():
    if not BLACKLIST_FILE.exists():
        return set()
    return set(
        line.strip().lower()
        for line in BLACKLIST_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

def load_paid_books():
    if not PAID_FILE.exists():
        return set()
    return set(
        line.strip().lower()
        for line in PAID_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

def mark_as_paid(book_url: str):
    slug = book_url.rstrip("/").split("/books/")[-1].lower()
    if not slug:
        return
    paid = load_paid_books()
    if slug not in paid:
        with PAID_FILE.open("a", encoding="utf-8") as f:
            f.write(slug + "\n")
        log.info(f"Книга добавлена в платные: {slug}")

def already_read_priority(book_url: str, email: str) -> bool:
    with priority_lock:
        return email in priority_read_by.get(book_url, set())

def mark_priority_read(book_url: str, email: str, all_emails: list):
    with priority_lock:
        if book_url not in priority_read_by:
            priority_read_by[book_url] = set()
        priority_read_by[book_url].add(email)

        read_count = len(priority_read_by[book_url])
        total = len(all_emails)
        slug = book_url.rstrip("/").split("/")[-1]
        log.info(f"Приоритет '{slug}': прочитали {read_count}/{total}")

        if read_count >= total:
            current = load_priority_books()
            remaining = [b for b in current if b != book_url]
            PRIORITY_FILE.write_text("\n".join(remaining), encoding="utf-8")
            del priority_read_by[book_url]
            log.info(f"Все прочитали '{slug}', удалена из приоритета")

def is_real_book(href: str) -> bool:
    if not href or "/books/" not in href:
        return False
    href_lower = href.lower()
    if any(x in href_lower for x in ["/genres/", "/tags/", "/cycles/", "/authors/", "/audiobooks", "/audio/"]):
        return False
    slug = href_lower.rstrip("/").split("/books/")[-1]
    if not slug or "/" in slug or "?" in slug or len(slug) < 4:
        return False
    if slug in EXCLUDE_SLUGS:
        return False
    return True

def is_blacklisted(href: str, blacklist: set, paid: set) -> bool:
    href_lower = href.lower()
    if any(x in href_lower for x in ["/audiobooks", "/audio/", "/genres/", "/tags/", "/ebooks"]):
        return True
    slug = href_lower.rstrip("/").split("/books/")[-1] if "/books/" in href_lower else ""
    if slug in EXCLUDE_SLUGS or slug in blacklist or slug in paid:
        return True
    return False

def get_random_book_from_main(page, mouse_pos):
    blacklist = load_blacklist()
    paid = load_paid_books()
    try:
        page.goto("https://litmarket.ru/", timeout=60000, wait_until="domcontentloaded")
        human_pause()
        human_scroll(page, "light")
        time.sleep(random.uniform(1.5, 2.5))

        links = page.locator("a[href*='/books/']")
        count = links.count()
        log.info(f"Найдено ссылок: {count}")

        if count < 3:
            return None

        valid = []
        for i in range(min(count, 40)):
            link = links.nth(i)
            href = link.get_attribute("href") or ""
            if is_real_book(href) and not is_blacklisted(href, blacklist, paid) and link.is_visible():
                text = (link.text_content() or "").strip()
                if len(text) > 2:
                    valid.append((href, text[:50]))

        if not valid:
            log.info("Подходящих книг не найдено")
            return None

        href, title = random.choice(valid[:12])
        log.info(f"Выбрана книга: {title}")

        if not href.startswith("http"):
            href = "https://litmarket.ru" + href
        return href

    except Exception as e:
        log.error(f"Ошибка выбора книги: {e}")
    return None

def continuous_read(playwright, account, proxy, all_emails: list, books_counter: dict, counter_lock: threading.Lock):
    from core.browser import create_browser
    from actions.login import do_login

    email = account["email"]
    log.info(f"[{email}] Старт непрерывного чтения")

    browser, page, mouse_pos = create_browser(playwright, proxy, account)

    try:
        page.goto("https://litmarket.ru/", timeout=60000, wait_until="domcontentloaded")
        do_login(page, mouse_pos, email, account["password"])
        log.info(f"[{email}] Залогинен")

        while True:
            if is_night():
                log.info(f"[{email}] Ночь (МСК), спим 30 мин...")
                time.sleep(1800)
                continue

            priority = load_priority_books()
            is_target = False
            book_url = None

            for p_url in priority:
                if not already_read_priority(p_url, email):
                    book_url = p_url
                    is_target = True
                    log.info(f"[{email}] Целевая книга: {book_url}")
                    break

            if not book_url:
                book_url = get_random_book_from_main(page, mouse_pos)
                if not book_url:
                    log.info(f"[{email}] Не нашли книгу, пауза 5 мин")
                    time.sleep(300)
                    continue
                log.info(f"[{email}] Случайная книга: {book_url}")

            log.info(f"[{email}] Открываем страницу книги...")
            page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            try:
                hit_paywall = go_through_reader(page, mouse_pos, book_url)

                if hit_paywall:
                    mark_as_paid(book_url)
                    log.info(f"[{email}] Книга платная, больше не читаем")
                else:
                    if is_target or random.random() < 0.7:
                        do_like(page, mouse_pos)
                    if is_target or random.random() < 0.6:
                        add_to_library(page, mouse_pos)
                    log.info(f"[{email}] Книга прочитана")

                if is_target:
                    mark_priority_read(book_url, email, all_emails)

                with counter_lock:
                    books_counter["count"] += 1

            except Exception as e:
                log.error(f"[{email}] Ошибка на книге: {e}")

            pause = random.randint(180, 600)
            log.info(f"[{email}] Пауза {pause // 60} мин")
            time.sleep(pause)

    except Exception as e:
        log.error(f"[{email}] Критическая ошибка: {e}")
    finally:
        browser.close()