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

class I18n:
    @staticmethod
    def get_supported_languages():
        supported_languages = []
        codes: [str] = [str(k) for k,v in supported_language_code_to_display_name.items()]
        for code in codes:
            if not code:
                continue
            lang = {"code":code, "display_name":supported_language_code_to_display_name.get(code, code)}
            supported_languages.append(lang)
        return supported_languages

    @staticmethod
    def get_supported_language_codes():
        return [e["code"] for e in I18n.get_supported_languages()]
