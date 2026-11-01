import random
from faker import Faker

faker = Faker("ru_RU")

def transliterate(text: str) -> str:
    cyrillic = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    latin = [
        "A","B","V","G","D","E","E","Zh","Z","I","I","K","L","M","N","O","P","R","S","T",
        "U","F","Kh","Ts","Ch","Sh","Sh","","Y","","E","Yu","Ya",
        "a","b","v","g","d","e","e","zh","z","i","i","k","l","m","n","o","p","r","s","t",
        "u","f","kh","ts","ch","sh","sh","","y","","e","yu","ya"
    ]
    return "".join(latin[cyrillic.find(ch)] if cyrillic.find(ch) >= 0 else ch for ch in text)

def get_realistic_browser_profile():
    chrome_version = random.randint(122, 125)
    os_chance = random.randint(0, 99)

    if os_chance < 70:
        os_string, platform, js_platform = "Windows NT 10.0; Win64; x64", '"Windows"', "Win32"
    elif os_chance < 90:
        os_string, platform, js_platform = "Macintosh; Intel Mac OS X 10_15_7", '"macOS"', "MacIntel"
    else:
        os_string, platform, js_platform = "X11; Linux x86_64", '"Linux"', "Linux x86_64"

    ua = f"Mozilla/5.0 ({os_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
    sec_ch_ua = f'"Google Chrome";v="{chrome_version}", "Chromium";v="{chrome_version}", "Not.A/Brand";v="24"'

    return {
        "userAgent": ua,
        "secChUa": sec_ch_ua,
        "secChUaPlatform": platform,
        "jsPlatform": js_platform,
        "version": str(chrome_version)
    }

def get_realistic_viewport():
    chance = random.randint(0, 99)
    if chance < 50:
        return 1920, 1080
    elif chance < 80:
        return 1366, 768
    return random.choice([(1536, 864), (1440, 900), (2560, 1440)])

def generate_account_data():
    first = faker.first_name()
    last = faker.last_name()
    num = random.randint(100, 9999)
    domain = random.choice(["@mail.ru", "@yandex.ru", "@gmail.com", "@bk.ru", "@inbox.ru"])
    email = transliterate(first).lower() + transliterate(last).lower() + str(num) + domain
    password = faker.password(length=random.randint(10, 14), special_chars=True, digits=True, upper_case=True)
    return email, password