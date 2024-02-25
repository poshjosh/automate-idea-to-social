import glob
import unittest

testSuite = unittest.TestSuite()
test_file_strings = glob.glob('python/test/aideas/*_test.py')
print(f'test_file_strings: {test_file_strings}')
module_strings = [str[0:len(str)-3] for str in test_file_strings]
print(f'module_strings: {module_strings}')
[__import__(str) for str in module_strings]
suites = [unittest.TestLoader().loadTestsFromName(str) for str in module_strings]
[testSuite.addTest(suite) for suite in suites]
print(testSuite)

result = unittest.TestResult()
testSuite.run(result)
print(result)


if __name__ == "__main__":
    unittest.main()