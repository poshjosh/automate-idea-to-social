import unittest
import sys

sys.path.append("../../../../main/aideas/agent/translation")

import translator

class TranslationAgentTest(unittest.TestCase):
    def test_translate_text(self):
        q = (
            "1. Мене звати Тіна, я інженер-програміст у Google. А також щось тут з двох речень.",
            "2. Як інженер-програміст, я працюю над внутрішнім інструментом, ",
            "3. який обслуговує інженерів безпеки та мережевих інженерів Google.",
        )

        result = translator.translate_text("en", q, source="uk")

        # print(result)

        result = translator.translate_text("en", q, source="uk", chunk_size=120, verbose=1)

        # print(result)

        print("\n".join(result))


if __name__ == '__main__':
    unittest.main()
