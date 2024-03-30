from ......main.app.aideas.agent.translation.translator import Translator


class TestTranslator(Translator):
    @staticmethod
    def of_config(agent_config: dict[str, any]) -> 'Translator':
        return Translator.of_dynamic(agent_config, TestTranslator)

    @staticmethod
    def get_input():
        return [
            "1. Мене звати Тіна, я інженер-програміст у Google. А також щось тут з двох речень.",
            "2. Як інженер-програміст, я працюю над внутрішнім інструментом, ",
            "3. який обслуговує інженерів безпеки та мережевих інженерів Google.",
        ]

    @staticmethod
    def get_expected_response_json() -> list[str]:
        return [[['1. My name is Tina and I am a software engineer at Google. ', '1. Мене звати Тіна, я інженер-програміст у Google.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]], ['And also something here from two sentences. ', 'А також щось тут з двох речень.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]], ["u~~~u 2. As a software engineer, I work on an internal tool, u~~~u 3. that serves Google's security engineers and network engineers.", 'u~~~u 2. Як інженер-програміст, я працюю над внутрішнім інструментом, u~~~u 3. який обслуговує інженерів безпеки та мережевих інженерів Google.', None, None, 3, None, None, [[]], [[['1eb561d2d816b8957a38cd5018eb164c', 'tea_AllEn_2022q2.md']]]]], None, 'uk', None, None, None, None, []]

    @staticmethod
    def get_expected_result() -> list[str]:
        return ['1. My name is Tina and I am a software engineer at Google. And also something here from two sentences.', '2. As a software engineer, I work on an internal tool,', "3. that serves Google's security engineers and network engineers."]

    def call_translation_service(self, params: dict, headers: dict) -> list[str]:
        return self.get_expected_response_json()
