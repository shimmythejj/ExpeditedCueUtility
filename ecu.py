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

    def __init__(self, audio_file_path, tracklist_path=None):

        self.audio_file_path = audio_file_path
        self.audio_file_directory = os.path.dirname(audio_file_path)
        self.audio_file_name = os.path.basename(audio_file_path)
        self.audio_file_extension = os.path.splitext(self.audio_file_name)[1]
        self.album_title = os.path.splitext(self.audio_file_name)[0]
        self.total_duration_seconds = probe_duration(audio_file_path)
        self.album_performer = ''

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


def get_hms(seconds):
    """
    Converts an # of seconds to a HH:MM:SS format string
    truncates the hours if less than 60 minutes, but always has minutes:seconds

    argument seconds can be either an in or float
    returns a string
    """

    if type(seconds) == int or type(seconds) == float:
        seconds = int(round(seconds))
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        if -1 < seconds < 3600:
            # hms = "%d:%02d" % (m, s)  # old string formatting
            hms = '{}:{:0>2d}'.format(m, s)
        elif seconds > 3599:
            # hms = "%d:%02d:%02d" % (h, m, s)  # old string formatting
            hms = '{}:{:0>2d}:{:0>2d}'.format(h, m, s)
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

    # since there is no csv and file sanity checking yet, visual inspection is required
    print('')
    print(working_album.audio_file_name)
    print('')
    print(working_album.album_title + ' ' + working_album.audio_file_extension.upper()[1:])
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
    print('')
    user_decision = input('Continue? [y/n]:')
    if user_decision != 'y':
        print('')
        print('Exiting')
        input("Press enter key to finish...")
        print('')
        sys.exit(0)


# TODO TESTS
def write_cue(album, output_file):
    # outputting track section of .cue file
    cue_output_full_path = album.audio_file_directory + '/' + output_file
    with open(cue_output_full_path, 'w') as f:
        f.write('PERFORMER "' + album.album_performer + '"\n')
        f.write('TITLE "' + album.album_title + '"\n')
        f.write('FILE "' + album.audio_file_name +
                '" ' + album.audio_file_extension.upper()[1:] + '\n')
        for item in album.tracklist_data:
            f.write('  TRACK ' + item[0] + ' AUDIO\n')
            f.write('    TITLE "' + item[2] + '"\n')
            f.write('    PERFORMER "' + item[1] + '"\n')
            f.write('    INDEX 01 ' + get_hms(item[3]) + ':00\n')


# TODO TESTS
def split_tracks(working_album):
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

    review_album(working_album)
    # TODO create a user prompt method that works with unittests
    # if verbose mode is off it will create a cue file by default
    if verbose:
        print('')
        user_decision = input('Create .cue file at ' + working_album.audio_file_path + '? [y/n]:')
        print('')
        if user_decision[0].lower() == 'y':
            create_cue = True
            working_album.album_performer = input('Album performer:')
        else:
            create_cue = False
            working_album.album_performer = 'Various Artists'
            # this wont actually do anything since the cue isn't be created
    else:
        create_cue = True
        working_album.album_performer = 'Various Artists'

    if create_cue:
        write_cue(working_album, output_file)

        print('')
        print('CUE File written')
        print('')

    # same thing here, verbose gives option to split, it defaults to split without verbose
    if verbose:
        print('')
        user_decision = input('Split audio into individual tracks at ' + working_album.audio_file_path + '? [y/n]:')
        print('')
        if user_decision[0].lower() == 'y':
            do_split_tracks = True
        else:
            do_split_tracks = False
    else:
        do_split_tracks = True

    if do_split_tracks:
        split_tracks(working_album)

    print('')
    input("Press enter key to finish...")
    print('')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('audio', help='path to audio file to be processed')
    parser.add_argument('-t', '--tracklist', type=str, help='path to tracklist csv file')
    parser.add_argument('-v', '--verbose', action='store_true', help='extra user prompts appear')
    pargs = parser.parse_args()
    generate(pargs.audio, tracklist_path=pargs.tracklist, verbose=pargs.verbose)
