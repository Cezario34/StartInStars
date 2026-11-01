import random
from playwright.sync_api import sync_playwright
from config import LAUNCH_ARGS

def create_browser(playwright, proxy, account):
    browser = playwright.chromium.launch(
        headless=False,
        proxy={
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"]
        },
        args=LAUNCH_ARGS
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
    mouse_pos = [
        random.randint(100, account["width"] - 100),
        random.randint(100, account["height"] - 100)
    ]
    return browser, page, mouse_pos