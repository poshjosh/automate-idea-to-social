from .....main.app.aideas.web.browser_cookie_store import BrowserCookieStore


class NoopCookieStore(BrowserCookieStore):
    def save(self):
        print(f"{__name__}#save() -> Noop")

    def load(self):
        print(f"{__name__}#load() -> Noop")
