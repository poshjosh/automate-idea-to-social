from .....main.aideas.agent.translation.translator import Translator


class TestTranslator(Translator):
    def __init__(self):
        super().__init__('https://test-service-url')

    """Simply return the original argument list"""
    def call_translation_service(self, params: dict, headers: dict):
        return params['q'].split(self.get_separator())
