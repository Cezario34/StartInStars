import random
import time
from core.human import human_click,human_type, random_sleep, human_pause, human_scroll
from config import SHELVES, random_pause, log


def do_login(page, mouse_pos, email, password):
    log.info("Логинимся...")
    human_click(page, page.locator(".login-btn").first, mouse_pos)
    human_pause(short=True)

    human_type(page, page.locator("input[name='email']").first, email, mouse_pos)
    human_pause(short=True)
    human_type(page, page.locator("input[name='password']").first, password, mouse_pos)

    random_sleep(200, 500)
    human_click(page, page.locator(".authLoginButton").first, mouse_pos)

    page.locator("a[href='#userPages'] .user-avatar").first.wait_for(timeout=15000)
    log.info(f"Успешный вход: {email}")

    human_pause()
    if random.random() < 0.35:
        human_scroll(page, "light")