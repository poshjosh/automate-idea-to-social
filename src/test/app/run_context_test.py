from unittest import mock

import unittest

from aideas.app.run_context import RunContext
from test.app.test_functions import get_run_context


class RunContextTest(unittest.TestCase):
    def test_get_language_codes_str_prefers_run_arg(self):
        with mock.patch.object(RunContext, 'get_arg') as get_arg:
            with mock.patch.object(RunContext, 'get_env') as get_env:
                get_arg.return_value = "ar,bn"
                get_env.return_value = "de,en"
                run_context: RunContext = get_run_context(["test-agent"])
                expect = "ar,bn"
                result = run_context.get_language_codes_str()
                self.assertEqual(result, expect)

    def test_get_language_codes_str_falls_back_to_env(self):
        with mock.patch.object(RunContext, 'get_arg') as get_arg:
            with mock.patch.object(RunContext, 'get_env') as get_env:
                get_arg.return_value = None
                get_env.return_value = "de,en"
                run_context: RunContext = get_run_context(["test-agent"])
                expect = "de,en"
                result = run_context.get_language_codes_str()
                self.assertEqual(result, expect)

    def test_get_language_codes_str_when_run_arg_is_array(self):
        with mock.patch.object(RunContext, 'get_arg') as get_arg:
            with mock.patch.object(RunContext, 'get_env') as get_env:
                get_arg.return_value = ["ar", "bn"]
                get_env.return_value = "de,en"
                run_context: RunContext = get_run_context(["test-agent"])
                expect = "ar,bn"
                result = run_context.get_language_codes_str()
                self.assertEqual(result, expect)

if __name__ == '__main__':
    unittest.main()
