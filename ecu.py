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

# TODO write test code for this I guess???


def get_seconds(hms):
    """
    converts HH:MM:SS, MM:SS, and SS string to total seconds int
    """

    if type(hms) == str:
        split_string = hms.split(':')
        if len(split_string) == 1:
            seconds = int(split_string[0])
        elif len(split_string) == 2:
            seconds = int(split_string[0]) * 60 + int(split_string[1])
        elif len(split_string) == 3:
            seconds = (int(split_string[0]) * 3600) + (int(split_string[1]) * 60) + int(split_string[2])
        else:
            raise ValueError('expected str in format HH:MM:SS, received: ' + hms)
    else:
        raise TypeError('expected str, received: ' + type(hms))

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

        if seconds < 3600:
            hms = "%2d:%02d" % (m, s)
        elif seconds > 3599:
            hms = "%2d:%02d:%02d" % (h, m, s)
        else:
            raise ValueError('received a negative or invalid value for seconds')

    else:
        raise TypeError('seconds must be type int or float, received: ' + type(seconds))

    return hms


def generate(audio_file_path, tracklist_path=None, verbose=False):
    """
    The generate function, generates a .cue file from a .csv and audio file.

    audio_file_path should be a path to an audio file

    tracklist_path should be a path to a valid .csv file

    create_cue determines whether a .cue file is generated

    split_tracks determines whether the original audio file is split into separate tracks

    tracklist.csv should be 4 rows per column in the format Track#,Artist,Track Title,Track Index in HH:MM:SS
    if no tracklist csv file is provided, then tracklist.csv is loaded from the same directory as the audio file

    the cue file is generated in the same directory as the audio file
    the split tracks are generated in a 'split/' subdirectory of the audio file
    """
    # TODO change the CSV format to start with Track# THEN Track Index followed by Artist,Track Title
    # TODO make some nicer error messages if referenced files don't exist
    # TODO choose custom outputs for cue and split tracks...

    audio_file_directory = os.path.dirname(audio_file_path)
    audio_file = os.path.basename(audio_file_path)
    audio_file_extension = os.path.splitext(audio_file)[1]
    album_title = os.path.splitext(audio_file)[0]

    # if no tracklist_path defined, load tracklist from same directory as audio file (audio_file_path)
    if tracklist_path is None:
        tracklist_path = audio_file_directory + '/' + 'tracklist.csv'

    output_file = album_title + '.cue'

    # ffprobe utility can provide total duration of media file in seconds.
    ffprobe_cmd = 'ffprobe -i "' + audio_file_path + '" -show_entries format=duration -v quiet -of csv="p=0"'
    ffprobe_result = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    total_duration_seconds = ffprobe_result.communicate()[0].decode(encoding='utf-8')

    # Stripping line and carriage returns from total_duration_seconds result and converting to float for later use
    total_duration_seconds = total_duration_seconds.replace('\r', '')
    total_duration_seconds = total_duration_seconds.replace('\n', '')
    total_duration_seconds = float(total_duration_seconds)

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

    # TODO maybe move these information displays into their own function and make it optional
    # since there is no csv and file sanity checking yet, visual inspection is required
    print('')
    print(audio_file)
    print('')
    print(album_title + ' ' + audio_file_extension.upper()[1:])
    print('')
    print('Tracklist')
    print('')

    # this is a test

    # column headers
    print('{:>4}'.format('#') + '  ' +
          '{:<30}'.format('Track Artist')[:24] + '  ' +
          '{:<30}'.format('Track Title')[:24] + '  ' +
          '{:>10}'.format('Index')[-10:] + '  ' +
          '{:>10}'.format('Length')[-10:])
    print('-' * 80)
    # data
    for item in tracklist_data:
        print('{:>4}'.format(item[0]) + '  ' +
              '{:<30}'.format(item[1])[:24] + '  ' +
              '{:<30}'.format(item[2])[:24] + '  ' +
              '{:>10}'.format(get_hms(item[3]))[-10:] + '  ' +
              '{:>10}'.format(get_hms(item[4]))[-10:])

    # adding total length sanity check remove eventually
    calculated_length_seconds = 0
    for row in tracklist_data:
        calculated_length_seconds += row[4]
    print('{:>80}'.format(get_hms(calculated_length_seconds)))
    print('{:>80}'.format(get_hms(total_duration_seconds)))

    print('')
    user_decision = input('Continue? [y/n]:')
    if user_decision != 'y':
        print('')
        print('Exiting')
        input("Press enter key to finish...")
        print('')
        sys.exit(0)

    # if verbose mode is off it will create a cue file by default
    if verbose:
        print('')
        user_decision = input('Create .cue file at ' + audio_file_path + '? [y/n]:')
        print('')
        if user_decision[0].lower() == 'y':
            create_cue = True
            album_performer = input('Album performer:')
        else:
            create_cue = False
            album_performer = 'Various Artists'  # this wont actually do anything since the cue isn't be created
    else:
        create_cue = True
        album_performer = 'Various Artists'

    if create_cue:
        # outputting track section of .cue file
        cue_output_full_path = audio_file_directory + '/' + output_file
        with open(cue_output_full_path, 'w') as f:
            f.write('PERFORMER "' + album_performer + '"\n')
            f.write('TITLE "' + album_title + '"\n')
            f.write('FILE "' + audio_file + '" ' + audio_file_extension.upper()[1:] + '\n')
            for item in tracklist_data:
                f.write('  TRACK ' + item[0] + ' AUDIO\n')
                f.write('    TITLE "' + item[2] + '"\n')
                f.write('    PERFORMER "' + item[1] + '"\n')
                f.write('    INDEX 01 ' + get_hms(item[3]) + ':00\n')

        print('')
        print('CUE File written')
        print('')

    # same thing here, verbose gives option to split, it defaults to split without verbose
    if verbose:
        print('')
        user_decision = input('Split audio into individual tracks at ' + audio_file_path + '? [y/n]:')
        print('')
        if user_decision[0].lower() == 'y':
            split_tracks = True
        else:
            split_tracks = False
    else:
        split_tracks = True

    if split_tracks:
        # create split output directory
        split_output_directory = audio_file_directory + '/split'
        if not os.path.exists(split_output_directory):
            os.makedirs(split_output_directory)

        # splitting tracks and outputting to audio_file_directory/split directory
        for row in tracklist_data:

            # preparing arguments
            # track filenames are '# - Artist - Track.extension'
            track_filename = row[0] + ' - ' + row[1] + ' - ' + row[2] + audio_file_extension
            track_output_full_path = split_output_directory + '/' + track_filename

            # preparing track index and length respectively
            track_index = str(row[3])
            track_length = str(row[4])

            # ffmpeg command for splitting audio files into the same format
            cmd = ['ffmpeg', '-i', audio_file_path, '-ss', track_index,
                   '-t', track_length, '-c:a', 'copy', '-y', track_output_full_path]

            # TODO figure a way to error out the program if any of these ffmpeg instances error
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    print(line, end='')

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
