import random
import time
from core.human import human_click, human_type, random_sleep
from config import random_pause, PAUSE_MEDIUM

def do_login(page, mouse_pos, email, password):
    print("Логинимся...")
    human_click(page, page.locator(".login-btn").first, mouse_pos)
    human_type(page, page.locator("input[name='email']").first, email, mouse_pos)
    human_type(page, page.locator("input[name='password']").first, password, mouse_pos)
    random_sleep(250, 500)
    human_click(page, page.locator(".authLoginButton").first, mouse_pos)

    page.locator("a[href='#userPages'] .user-avatar").first.wait_for(timeout=15000)
    print(f"Успешный вход: {email}")
    random_pause(*PAUSE_MEDIUM)