import random
from playwright.sync_api import sync_playwright
from config import LAUNCH_ARGS
from config import SHELVES, random_pause, log


def get_sec_ch_ua(user_agent: str) -> str:
    """Генерирует Sec-CH-UA на основе User-Agent"""
    if "Chrome/" in user_agent:
        try:
            version = user_agent.split("Chrome/")[1].split(".")[0]
            return f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not.A/Brand";v="24"'
        except:
            pass
    return '"Google Chrome";v="124", "Chromium";v="124", "Not.A/Brand";v="24"'

def create_browser(playwright, proxy, account):
    ua = account["ua"]
    sec_ch_ua = get_sec_ch_ua(ua)

    browser = playwright.chromium.launch(
        headless=False,
        proxy={
            "server": proxy["server"],
            "username": proxy["username"],
            "password": proxy["password"]
        },
        args=LAUNCH_ARGS + [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
        ]
    )

    context = browser.new_context(
        user_agent=ua,
        viewport={"width": account["width"], "height": account["height"]},
        device_scale_factor=random.choice([1, 1.25, 1.5]),
        locale="ru-RU",
        timezone_id="Europe/Moscow",
        extra_http_headers={
            "Sec-CH-UA": sec_ch_ua,
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": "\"Windows\"",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    )
    context.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ru-RU', 'ru', 'en-US', 'en']
        });
        window.chrome = { runtime: {} };

        // Canvas noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            const ctx = this.getContext('2d');
            if (ctx) {
                const imageData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                }
                ctx.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.apply(this, arguments);
        };
    """
        )

    page = context.new_page()
    mouse_pos = [
        random.randint(100, account["width"] - 100),
        random.randint(100, account["height"] - 100)
    ]
    return browser, page, mouse_pos