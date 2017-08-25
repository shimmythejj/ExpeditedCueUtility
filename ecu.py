"""
Expedited Cue Utility

This module attempts to generate a .cue file from a .csv file and then calls ffmpeg to split the audio file provided
into it's separate tracks

get_seconds(hms) converts a HH:MM:SS string to a seconds int

get_hms(seconds) converts a number of seconds to an HH:MM:SS string

generate() runs the bulk of the program, it expects at least 1 argument of the path to audio file.
tracklist_path and verbose are optional.

external programs ffmpeg and ffprobe are prerequisites for this module to run
"""
import sys
import csv
import os.path
import subprocess
import argparse
import re


class Album(object):
    """Docstring"""
    # TODO this docstring

    def __init__(self, audio_file_path, tracklist_path=None):

        # TODO do I need validation? or will standard errors be good enough?
        self.audio_file_path = audio_file_path
        self.audio_file_directory = os.path.dirname(audio_file_path)
        self.audio_file_name = os.path.basename(audio_file_path)
        self.audio_file_extension = os.path.splitext(self.audio_file_name)[1]
        self.album_title = os.path.splitext(self.audio_file_name)[0]
        self.total_duration_seconds = probe_duration(audio_file_path)
        self.album_performer = ''

        # WAVE, MP3, and AIFF are the only "Supported" formats of cue files
        # setting anything else to WAVE format may work with modern audio players
        if self.audio_file_extension == '.mp3'.lower() or self.audio_file_extension == '.aiff'.lower():
            self.cue_extension = self.audio_file_extension.upper()[1:]
        else:
            self.cue_extension = 'WAVE'

        # if no tracklist_path defined, load tracklist from same directory as audio file (audio_file_path)
        if tracklist_path is None:
            self.tracklist_path = self.audio_file_directory + '/' + 'tracklist.csv'
        else:
            self.tracklist_path = tracklist_path

        self.tracklist_data = parse_tracklist_csv(self.tracklist_path, self.total_duration_seconds)


def get_seconds(hms):
    """
    converts HH:MM:SS, MM:SS, and SS string to total seconds int
    """

    if type(hms) == str:

        # this regex format is a bit more lenient than documentation states, but it shouldn't cause issues
        str_format = re.compile('^([0-9]+:){0,2}([0-9]+)$')
        validity = str_format.match(hms)
        split_string = hms.split(':')

        if len(split_string) == 1 and validity:
            seconds = int(split_string[0])
        elif len(split_string) == 2 and validity:
            seconds = int(split_string[0]) * 60 + int(split_string[1])
        elif len(split_string) == 3 and validity:
            seconds = (int(split_string[0]) * 3600) + (int(split_string[1]) * 60) + int(split_string[2])
        else:
            raise ValueError('expected str in format HH:MM:SS, received: ' + hms)
    else:
        raise TypeError('expected str, received: ' + str(type(hms)))

    return seconds


def get_hms(seconds, hours=True):
    """
    Converts an # of seconds to a HH:MM:SS format string
    truncates the hours if less than 60 minutes, but always has minutes:seconds

    argument seconds can be either an in or float
    returns a string
    """

    if type(seconds) == int or type(seconds) == float:
        seconds = int(round(seconds))
        m, s = divmod(seconds, 60)

        if hours:
            h, m = divmod(m, 60)
            if h < 1 and seconds >= 0:
                print(h, m, s)
                # hms = "%d:%02d" % (m, s)  # old string formatting
                hms = '{}:{:0>2d}'.format(m, s)
            elif h > 0:
                # hms = "%d:%02d:%02d" % (h, m, s)  # old string formatting
                hms = '{}:{:0>2d}:{:0>2d}'.format(h, m, s)
            else:
                raise ValueError('received a negative or invalid value for seconds')

        # cue files don't use hours, only minutes, this format is needed for the cue writer
        else:
            if -1 < seconds:
                # hms = "%d:%02d" % (m, s)  # old string formatting
                hms = '{}:{:0>2d}'.format(m, s)
            else:
                raise ValueError('received a negative or invalid value for seconds')

    else:
        raise TypeError('seconds must be type int or float, received: ' + str(type(seconds)))

    return hms


def probe_duration(audio_file_path):
    """This uses ffprobe to find an audio file's length and returns seconds as a float"""

    # ffprobe utility can provide total duration of media file in seconds.
    ffprobe_cmd = 'ffprobe -i "' + audio_file_path + '" -show_entries format=duration -v quiet -of csv="p=0"'
    ffprobe_result = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    total_duration_seconds = ffprobe_result.communicate()[0].decode(encoding='utf-8')

    # Stripping line and carriage returns from total_duration_seconds result and converting to float for later use
    total_duration_seconds = total_duration_seconds.replace('\r', '')
    total_duration_seconds = total_duration_seconds.replace('\n', '')
    total_duration_seconds = float(total_duration_seconds)
    return total_duration_seconds


# TODO TESTS
def parse_tracklist_csv(tracklist_path, total_duration_seconds):
    """
    This parses the tracklist csv

    tracklist.csv should be 4 rows per column in the format Track#,Artist,Track Title,Track Index in HH:MM:SS
    if no tracklist csv file is provided, then tracklist.csv is loaded from the same directory as the audio file
    """

    tracklist_data = []

    # loading initial csv into tracklist_data
    with open(tracklist_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # csv file expects a HH:MM:SS style index for each track, converting it to raw seconds for easier processing
            row[3] = get_seconds(row[3])
            tracklist_data.append(row)

    # appending individual track length to the end of each row
    for i, row in enumerate(tracklist_data):
        if i == len(tracklist_data) - 1:
            duration_seconds = total_duration_seconds - row[3]
        else:
            duration_seconds = tracklist_data[i + 1][3] - row[3]
        row.append(duration_seconds)

    return tracklist_data


# TODO TESTS
def review_album(working_album):
    """Prints a readable chart of data of working_album Album, accepts a populated Album object"""

    # since there is no csv and file sanity checking yet, visual inspection is required
    print('')
    print(working_album.audio_file_name)
    print('')
    print(working_album.album_title + ' ' + working_album.cue_extension)
    print('')
    print('Tracklist')
    print('')
    # column headers
    print('{:>4}'.format('#') + '  ' +
          '{:<30}'.format('Track Artist')[:24] + '  ' +
          '{:<30}'.format('Track Title')[:24] + '  ' +
          '{:>10}'.format('Index')[-10:] + '  ' +
          '{:>10}'.format('Length')[-10:])
    print('-' * 80)
    # data
    for item in working_album.tracklist_data:
        print('{:>4}'.format(item[0]) + '  ' +
              '{:<30}'.format(item[1])[:24] + '  ' +
              '{:<30}'.format(item[2])[:24] + '  ' +
              '{:>10}'.format(get_hms(item[3]))[-10:] + '  ' +
              '{:>10}'.format(get_hms(item[4]))[-10:])

    # adding total length sanity check remove eventually
    calculated_length_seconds = 0
    for row in working_album.tracklist_data:
        calculated_length_seconds += row[4]
    print('{:>80}'.format(get_hms(calculated_length_seconds)))
    print('{:>80}'.format(get_hms(working_album.total_duration_seconds)))
    # print('')
    # user_decision = input('Continue? [y/n]:')
    if not yes_no_decision('Continue?'):
        print('')
        print('Exiting')
        print('')
        enter_to_continue()
        sys.exit(0)


# TODO TESTS
def write_cue(album, output_file):
    """Docstring"""
    # TODO this docstring

    # outputting track section of .cue file
    cue_output_full_path = album.audio_file_directory + '/' + output_file
    with open(cue_output_full_path, 'w') as f:
        f.write('PERFORMER "' + album.album_performer + '"\n')
        f.write('TITLE "' + album.album_title + '"\n')
        f.write('FILE "' + album.audio_file_name +
                '" ' + album.cue_extension + '\n')
        for item in album.tracklist_data:
            f.write('  TRACK ' + item[0] + ' AUDIO\n')
            f.write('    TITLE "' + item[2] + '"\n')
            f.write('    PERFORMER "' + item[1] + '"\n')
            f.write('    INDEX 01 ' + get_hms(item[3], hours=False) + ':00\n')

    print('')
    print('CUE file written.')
    print('')


# TODO TESTS
def split_tracks(working_album):
    """Docstring"""
    # TODO this docstring

    # create split output directory
    split_output_directory = working_album.audio_file_directory + '/split'
    if not os.path.exists(split_output_directory):
        os.makedirs(split_output_directory)

    # splitting tracks and outputting to audio_file_directory/split directory
    for row in working_album.tracklist_data:

        # preparing arguments
        # track filenames are '# - Artist - Track.extension'
        track_filename = row[0] + ' - ' + row[1] + ' - ' + row[2] + working_album.audio_file_extension
        track_output_full_path = split_output_directory + '/' + track_filename

        # preparing track index and length respectively
        track_index = str(row[3])
        track_length = str(row[4])

        # ffmpeg command for splitting audio files into the same format
        cmd = ['ffmpeg', '-i', working_album.audio_file_path, '-ss', track_index,
               '-t', track_length, '-c:a', 'copy', '-y', track_output_full_path]

        # TODO figure a way to error out the program if any of these ffmpeg instances error
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='')


def yes_no_decision(prompt_text, inputter=input):
    """Asks user a question, returns answer as boolean, by default it uses input(), can be defined for unit testing"""

    print('')
    user_input = inputter('{} [y/n]:'.format(prompt_text))
    print('')
    if user_input:
        if user_input[0].lower() == 'y':
            return True
        else:
            return False
    else:
        return False


def get_user_input(prompt_text, inputter=input):
    return inputter(prompt_text)


def enter_to_continue(inputter=input):
    """Simple press enter to continue"""

    print('')
    inputter('Press enter to continue...')
    print('')


# TODO TESTS
def generate(audio_file_path, tracklist_path=None, verbose=False):
    """
    The generate function, generates a .cue file from a .csv and audio file.

    audio_file_path should be a path to an audio file

    tracklist_path should be a path to a valid .csv file

    create_cue determines whether a .cue file is generated

    do_split_tracks determines whether the original audio file is split into separate tracks

    the cue file is generated in the same directory as the audio file
    the split tracks are generated in a 'split/' subdirectory of the audio file
    """
    # TODO change the CSV format to start with Track# THEN Track Index followed by Artist,Track Title
    # TODO make some nicer error messages if referenced files don't exist
    # TODO choose custom outputs for cue and split tracks...

    working_album = Album(audio_file_path, tracklist_path)

    output_file = working_album.album_title + '.cue'

    if verbose:
        working_album.album_performer = get_user_input('Album performer:')
        if yes_no_decision('Review album data?'):
            review_album(working_album)
        if yes_no_decision('Create .cue file?'):
            write_cue(working_album, output_file)
        if yes_no_decision('Split tracks?'):
            split_tracks(working_album)
    else:
        working_album.album_performer = "Various Artists"
        review_album(working_album)
        write_cue(working_album, output_file)
        split_tracks(working_album)

    enter_to_continue()


def parse_them_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('audio', help='path to audio file to be processed')
    parser.add_argument('-t', '--tracklist', type=str, help='path to tracklist csv file')
    parser.add_argument('-v', '--verbose', action='store_true', help='extra user prompts appear')
    pargs = parser.parse_args(args)
    return pargs


if __name__ == '__main__':
    print(sys.argv)
    pargs = parse_them_args(sys.argv[1:])
    generate(pargs.audio, tracklist_path=pargs.tracklist, verbose=pargs.verbose)
