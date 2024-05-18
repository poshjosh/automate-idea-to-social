import os.path
import unittest
import uuid
from datetime import datetime

from ....main.app.aideas.env import get_cached_results_file


class EnvTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_name = "test-agent"

    def test_get_cached_results_file_given_non_existing_file(self):
        input_filename = f"{uuid.uuid4().hex}.jpg"
        filepath = get_cached_results_file(self.agent_name, input_filename)
        self.__check_result(filepath, input_filename)

    def test_get_cached_results_file_given_existing_file(self):
        random = uuid.uuid4().hex
        input_filename = f"{random}.jpg"
        expected_suffix = f"{random}-1.jpg"
        existing = get_cached_results_file(self.agent_name, input_filename)
        self.__create_file(existing)
        try:
            filepath = get_cached_results_file(self.agent_name, input_filename)
            self.__check_result(filepath, expected_suffix)
        finally:
            self.__remove_file(existing)

    def test_get_cached_results_file_given_no_file(self):
        filepath = get_cached_results_file(self.agent_name)
        self.__check_result(filepath)

    def __check_result(self, filepath: str, expected_suffix: str = None):
        output_filename = os.path.basename(filepath)
        self.assertIn(self.agent_name, filepath)
        self.assertTrue(output_filename.startswith(datetime.now().strftime("%Y-%m-%d")))
        if expected_suffix:
            self.assertTrue(output_filename.endswith(expected_suffix))

    @staticmethod
    def __create_file(path):
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        if not os.path.exists(path):
            with open(path, 'a'):
                os.utime(path, None)
                print("Created file: ", path)

    @staticmethod
    def __remove_file(path):
        if os.path.exists(path):
            os.remove(path)
            print("Removed file: ", path)


if __name__ == '__main__':
    unittest.main()
