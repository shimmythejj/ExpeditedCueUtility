import unittest
import ecu


class TestGetSeconds(unittest.TestCase):
    def test_zero(self):
        result = ecu.get_seconds('0')
        expected = 0
        self.assertEqual(expected, result)

    def test_one(self):
        result = ecu.get_seconds('1')
        expected = 1
        self.assertEqual(expected, result)

    def test_sixty(self):
        result = ecu.get_seconds('60')
        expected = 60
        self.assertEqual(expected, result)

    def test_one_minute(self):
        result = ecu.get_seconds('1:00')
        expected = 60
        self.assertEqual(result,expected)

    def test_one_minute_one(self):
        result = ecu.get_seconds('1:01')
        expected = 61
        self.assertEqual(expected, result)

    def test_one_hour(self):
        result = ecu.get_seconds('1:00:00')
        expected = 3600
        self.assertEqual(expected, result)

    def test_one_hour_and_change(self):
        result = ecu.get_seconds('1:12:34')
        expected = 4354
        self.assertEqual(expected, result)

    def test_a_lotta_seconds(self):
        result = ecu.get_seconds('601')
        expected = 601
        self.assertEqual(expected, result)

    def test_a_lotta_minutes(self):
        result = ecu.get_seconds('61:01')
        expected = 3661
        self.assertEqual(expected, result)

    def test_a_lotta_hours(self):
        result = ecu.get_seconds('25:01:01')
        expected = 90061
        self.assertEqual(expected, result)

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            ecu.get_seconds('12:12:12:12')

    def test_empty(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_seconds('')
        exception_message = str(cm.exception)
        exception_message = exception_message[:42]
        expected_message = 'expected str in format HH:MM:SS, received:'
        self.assertEqual(exception_message, expected_message)

    def test_missing_section(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_seconds('12::12')
        exception_message = str(cm.exception)
        exception_message = exception_message[:42]
        expected_message = 'expected str in format HH:MM:SS, received:'
        self.assertEqual(expected_message, exception_message)

    def test_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            ecu.get_seconds(22)
        exception_message = str(cm.exception)
        exception_message = exception_message[:23]
        expected_message = 'expected str, received:'
        self.assertEqual(expected_message, exception_message)

    def test_with_non_numerical_string(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_seconds('A normal string')
        exception_message = str(cm.exception)
        exception_message = exception_message[:42]
        expected_message = 'expected str in format HH:MM:SS, received:'
        self.assertEqual(expected_message, exception_message)


class TestGetHMS(unittest.TestCase):

    def test_zero(self):
        result = ecu.get_hms(0)
        expected = '0:00'
        self.assertEqual(expected, result)

    def test_one(self):
        result = ecu.get_hms(1)
        expected = '0:01'
        self.assertEqual(expected, result)

    def test_59(self):
        result = ecu.get_hms(59)
        expected = '0:59'
        self.assertEqual(expected, result)

    def test_60(self):
        result = ecu.get_hms(60)
        expected = '1:00'
        self.assertEqual(expected, result)

    def test_61(self):
        result = ecu.get_hms(61)
        expected = '1:01'
        self.assertEqual(expected, result)

    def test_3599(self):
        result = ecu.get_hms(3599)
        expected = '59:59'
        self.assertEqual(expected, result)

    def test_3600(self):
        result = ecu.get_hms(3600)
        expected = '1:00:00'
        self.assertEqual(expected, result)

    def test_3601(self):
        result = ecu.get_hms(3601)
        expected = '1:00:01'
        self.assertEqual(expected, result)

    def test_float(self):
        expected = '12:12'
        result = ecu.get_hms(731.61)
        self.assertEqual(expected, result)

    def test_negative(self):
        with self.assertRaises(ValueError) as cm:
            ecu.get_hms(-12)
        expected_message = 'received a negative or invalid value for seconds'
        exception_message = str(cm.exception)
        self.assertEqual(expected_message, exception_message)

    def test_invalid_type(self):
        with self.assertRaises(TypeError) as cm:
            ecu.get_hms('using a string instead of a number')
        expected_message = 'seconds must be type int or float, received:'
        exception_message = str(cm.exception)[:44]
        self.assertEqual(expected_message, exception_message)


if __name__ == '__main__':
    unittest.main()
