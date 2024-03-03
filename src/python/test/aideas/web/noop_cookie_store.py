from ....main.aideas.web.browser_cookie_store import BrowserCookieStore


class NoopCookieStore(BrowserCookieStore):
    def __init__(self, webdriver, domain):
        super().__init__(webdriver, domain)

    def save(self):
        print(f"{__name__}#save() -> Noop")

    def load(self):
        print(f"{__name__}#load() -> Noop")
