import random
import time
from pathlib import Path
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils import get_realistic_browser_profile, get_realistic_viewport, generate_account_data
from litmarket_bot.core.human import human_click, human_type, random_sleep
from warmup import warmup

ACCOUNTS_FILE = Path("../data/accounts.txt")

def register_one(playwright, proxy, account_num):
    profile = get_realistic_browser_profile()
    width, height = get_realistic_viewport()

    print(f"\n{'='*50}")
    print(f"Аккаунт {account_num} | Прокси: {proxy['ip_port']}")

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
        user_agent=profile["userAgent"],
        viewport={"width": width, "height": height},
        extra_http_headers={
            "Sec-CH-UA": profile["secChUa"],
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": profile["secChUaPlatform"]
        }
    )

    context.add_init_script(f"""
        Object.defineProperty(navigator, 'platform', {{ get: () => '{profile["jsPlatform"]}' }});
    """)

    page = context.new_page()
    mouse_pos = [random.randint(100, width-100), random.randint(100, height-100)]

    try:
        email, password = generate_account_data()
        print(f"Email: {email}")
        print(f"Пароль: {password}")

        page.goto("https://litmarket.ru/")
        page.mouse.move(mouse_pos[0], mouse_pos[1])
        time.sleep(random.uniform(1.5, 3))

        # Прогрев
        warmup(page, mouse_pos)
        time.sleep(random.uniform(2, 4))

        # Регистрация
        human_click(page, page.locator(".login-btn").first, mouse_pos)
        human_type(page, page.locator("input[name='email']").first, email, mouse_pos)
        human_type(page, page.locator("input[name='password']").first, password, mouse_pos)
        random_sleep(200, 400)

        human_click(page, page.locator("input[value='Регистрация']").first, mouse_pos)

        page.locator("input[name='eula_agree']").evaluate("node => node.click()")
        random_sleep(90, 180)
        page.locator("input[name='eula_18_years']").evaluate("node => node.click()")
        random_sleep(90, 180)

        human_click(page, page.locator("button[type='submit']").last, mouse_pos)

        try:
            page.get_by_text("уже существует").wait_for(timeout=5000)
            print("Почта уже существует")
        except PlaywrightTimeoutError:
            print("Почта успешно создана")
            current_id = 1
            if ACCOUNTS_FILE.exists():
                lines = [l for l in ACCOUNTS_FILE.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
                current_id = len(lines) + 1

            line = f"{current_id} | {email} | {password} | {profile['userAgent']} | {width} | {height}\n"
            with ACCOUNTS_FILE.open("a", encoding="utf-8") as f:
                f.write(line)
            print(f"Записано в accounts.txt (ID: {current_id})")

        print(f"Готово для {email}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        browser.close()