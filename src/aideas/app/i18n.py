DEFAULT_LANGUAGE_CODE="en"
supported_language_code_to_display_name = {
    "ar":"العربية",
    "bn":"বাংলা",
    "de":"Deutsch",
    "en":"English",
    "es":"Español",
    "fr":"Français",
    "hi":"हिन्दी",
    "it":"Italiano",
    "ja":"日本語",
    "ko":"한국어",
    "ru":"Русский",
    "tr":"Türkçe",
    "uk":"українська",
    "zh":"中文"
}

class Language:
    def __init__(self, code: str, display_name: str):
        self.__code = code
        self.__display_name = display_name

    @property
    def is_default(self):
        return self.code == DEFAULT_LANGUAGE_CODE

    @property
    def is_supported(self):
        return self.code in supported_language_code_to_display_name

    @property
    def code(self):
        return self.__code

    @property
    def display_name(self):
        return self.__display_name

    def __str__(self):
        return f"{self.code}={self.display_name}"

    def __repr__(self):
        return self.__str__()

class I18n:
    @staticmethod
    def get_supported_languages() -> list[Language]:
        supported_languages = []
        codes: list[str] = [str(k) for k,v in supported_language_code_to_display_name.items()]
        for code in codes:
            if not code:
                continue
            supported_languages.append(Language(code, supported_language_code_to_display_name.get(code, code)))
        return supported_languages

    @staticmethod
    def get_supported_language_codes():
        return [e.code for e in I18n.get_supported_languages()]
