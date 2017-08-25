import unittest
import unittest.mock
import ecu
import os
import shutil


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
        self.assertEqual(result, expected)

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


class TestProbeDuration(unittest.TestCase):
    def test_sample_data(self):
        sample_audio = 'sample audio/Theophany - Time\'s End 1 (Sample).mp3'
        expected_duration = 93
        calculated_duration = ecu.probe_duration(sample_audio)
        rounded_duration = round(calculated_duration)
        self.assertEqual(expected_duration, rounded_duration)


class TestParseTracklistCsv(unittest.TestCase):
    def test_sample_data(self):
        sample_audio = 'sample audio/tracklist.csv'
        duration = 93
        returned_data = ecu.parse_tracklist_csv(sample_audio, duration)
        expected_data = [['1', 'Theophany', 'Majora\'s Mask (Sample)', 0, 31],
                         ['2', 'Theophany', 'The Clockworks (Sample)', 31, 31],
                         ['3', 'Theophany ft. Laura Intravia', 'Terrible Fate (Sample)', 62, 31]]

        self.assertEqual(expected_data, returned_data)


# @unittest.skip('I do not know how to do this one yet')
class TestReviewAlbum(unittest.TestCase):

    @unittest.mock.patch('ecu.yes_no_decision', return_value='Y')
    def test_review_album_continue(self, input):
        test_album = ecu.Album('sample audio/Theophany - Time\'s End 1 (Sample).mp3', 'sample audio/tracklist.csv')
        ecu.review_album(test_album)

    @unittest.mock.patch('ecu.yes_no_decision', return_value='n')
    def test_review_album_exit(self, input):
        test_album = ecu.Album('sample audio/Theophany - Time\'s End 1 (Sample).mp3', 'sample audio/tracklist.csv')
        ecu.review_album(test_album)


class TestWriteCue(unittest.TestCase):
    def test_sample_data(self):
        self.fail()


class TestSplitTracks(unittest.TestCase):
    def test_split_tracks(self):
        self.fail()


class TestYesNoDecision(unittest.TestCase):

    def test_yes_no_decision(self):

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter('y'))
        self.assertEqual(True, result)

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter('Y'))
        self.assertEqual(True, result)

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter('Yes'))
        self.assertEqual(True, result)

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter('n'))
        self.assertEqual(False, result)

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter(''))
        self.assertEqual(False, result)

        result = ecu.yes_no_decision('test prompt', inputter=nifty_inputter(False))
        self.assertEqual(False, result)


class TestGetUserInput(unittest.TestCase):

    # @unittest.mock.patch('ecu.get_user_input', return_value='test')
    def test_get_user_input(self):
        self.assertEqual('test', ecu.get_user_input('test prompt', inputter=nifty_inputter('test')))


class TestEnterToContinue(unittest.TestCase):

    def test_enter_to_continue(self):
        ecu.enter_to_continue(inputter=nifty_inputter(''))
        pass


# @unittest.skip('I do not know how to do this one yet')
class TestGenerate(unittest.TestCase):

    @unittest.mock.patch('ecu.yes_no_decision', return_value='y')
    @unittest.mock.patch('ecu.get_user_input', return_value='y')
    @unittest.mock.patch('ecu.enter_to_continue', return_value='y')
    def test_generate_verbose(self, input1, input2, input3):
        if os.path.exists('sample/audio/'):
            shutil.rmtree('sample audio/split/')
        if os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue'):
            os.remove('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        ecu.generate('sample audio/Theophany - Time\'s End 1 (Sample).mp3', verbose=True)
        track1_exists = os.path.exists('sample audio/split/1 - Theophany - Majora\'s Mask (Sample).mp3')
        track2_exists = os.path.exists('sample audio/split/2 - Theophany - The Clockworks (Sample).mp3')
        track3_exists = os.path.exists('sample audio/split/3 - Theophany ft. Laura Intravia - Terrible Fate (Sample).mp3')
        cuefile_exists = os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        self.assertEqual(True, track1_exists)
        self.assertEqual(True, track2_exists)
        self.assertEqual(True, track3_exists)
        self.assertEqual(True, cuefile_exists)

    @unittest.mock.patch('ecu.yes_no_decision', return_value='y')
    @unittest.mock.patch('ecu.get_user_input', return_value='y')
    @unittest.mock.patch('ecu.enter_to_continue', return_value='y')
    def test_generate_nonverbose(self, input1, input2, input3):
        if os.path.exists('sample/audio/'):
           shutil.rmtree('sample audio/split/')
        if os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue'):
            os.remove('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        ecu.generate('sample audio/Theophany - Time\'s End 1 (Sample).mp3')
        track1_exists = os.path.exists('sample audio/split/1 - Theophany - Majora\'s Mask (Sample).mp3')
        track2_exists = os.path.exists('sample audio/split/2 - Theophany - The Clockworks (Sample).mp3')
        track3_exists = os.path.exists('sample audio/split/3 - Theophany ft. Laura Intravia - Terrible Fate (Sample).mp3')
        cuefile_exists = os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        self.assertEqual(True, track1_exists)
        self.assertEqual(True, track2_exists)
        self.assertEqual(True, track3_exists)
        self.assertEqual(True, cuefile_exists)

    @unittest.mock.patch('ecu.yes_no_decision', return_value='y')
    @unittest.mock.patch('ecu.get_user_input', return_value='y')
    @unittest.mock.patch('ecu.enter_to_continue', return_value='y')
    def test_generate_custom_tracklist(self, input1, input2, input3):
        if os.path.exists('sample/audio/'):
            shutil.rmtree('sample audio/split/')
        if os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue'):
            os.remove('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        ecu.generate('sample audio/Theophany - Time\'s End 1 (Sample).mp3', tracklist_path='sample audio/reference files/custom tracklist.csv')
        track1_exists = os.path.exists('sample audio/split/1 - Theophany - Majora\'s Mask (Sample).mp3')
        track2_exists = os.path.exists('sample audio/split/2 - Theophany - The Clockworks (Sample).mp3')
        track3_exists = os.path.exists('sample audio/split/3 - Theophany ft. Laura Intravia - Terrible Fate (Sample).mp3')
        cuefile_exists = os.path.exists('sample audio/Theophany - Time\'s End 1 (Sample).cue')
        self.assertEqual(True, track1_exists)
        self.assertEqual(True, track2_exists)
        self.assertEqual(True, track3_exists)
        self.assertEqual(True, cuefile_exists)


class TestParseThemArgs(unittest.TestCase):

    def test_parse_them_args(self):
        received_pargs = str(ecu.parse_them_args(['sample audio/Theophany - Time\'s End 1 (Sample).mp3',
                                                  '-t',
                                                  'sample audio/reference files/custom tracklist.csv',
                                                  '-v']))
        expected_pargs = str('Namespace(audio="sample audio/Theophany - Time\'s End 1 (Sample).mp3", '
                             'tracklist=\'sample audio/reference files/custom tracklist.csv\', '
                             'verbose=True)')
        print(expected_pargs)
        print(received_pargs)
        self.assertEqual(expected_pargs, received_pargs)


def nifty_inputter(return_value):
    """
    This function returns a function intending to replace the input() function for testing
    The function returned will do nothing but return the return_value
    """

    def tester_inputter(prompt_text):
        return return_value

    return tester_inputter


if __name__ == '__main__':
    unittest.main()

