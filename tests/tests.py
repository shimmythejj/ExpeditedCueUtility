import unittest
import ecu


class TestGetSeconds(unittest.TestCase):
    def test_zero(self):
        result = ecu.get_seconds('0')
        expected = 0
        self.assertEqual(result, expected)

    def test_one(self):
        result = ecu.get_seconds('1')
        expected = 1
        self.assertEqual(result, expected)

    def test_sixty(self):
        result = ecu.get_seconds('60')
        expected = 60
        self.assertEqual(result, expected)

    def test_one_minute(self):
        result = ecu.get_seconds('1:00')
        expected = 60
        self.assertEqual(result,expected)

    def test_one_minute_one(self):
        result = ecu.get_seconds('1:01')
        expected = 61
        self.assertEqual(result, expected)

    def test_one_hour(self):
        result = ecu.get_seconds('1:00:00')
        expected = 3600
        self.assertEqual(result, expected)

    def test_one_hour_and_change(self):
        result = ecu.get_seconds('1:12:34')
        expected = 4354
        self.assertEqual(result, expected)

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            ecu.get_seconds('12:12:12:12')

    def test_empty(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_seconds('')
        exception_message = str(cm.exception)
        exception_message = exception_message[:42]
        print(exception_message)
        expected_message = 'expected str in format HH:MM:SS, received:'
        self.assertEqual(exception_message, expected_message)

    def test_missing_section(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_seconds('12::12')
        exception_message = str(cm.exception)
        exception_message = exception_message[:42]
        print(exception_message)
        expected_message = 'expected str in format HH:MM:SS, received:'
        self.assertEqual(exception_message, expected_message)

    def test_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            ecu.get_seconds(22)
        exception_message = str(cm.exception)
        exception_message = exception_message[:23]
        expected_message = 'expected str, received:'
        self.assertEqual(exception_message, expected_message)

if __name__ == '__main__':
    unittest.main()
