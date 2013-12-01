import os
import string
import subprocess
import sys
import wave
from songidentity import SongInfo

LAME_DECODE = "/course/cs4500f13/bin/lame --decode %s %s"
LAME_ENCODE = "/course/cs4500f13/bin/lame -b 96 %s %s"
MP3_STRING = "MPEG ADTS, layer III"


def mp3_to_wave_subprocess(mp3):
    """convert mp3 to wave by calling lame in subprocess returns filename"""
    wav = "%s.wav" % os.path.splitext(mp3)[0]
    decode = LAME_DECODE % (mp3, wav)
    subprocess.check_call(decode.split(" "))
    return wav


def gen_file_list(flag_path_tup):
    """Generates a list of all files in the given directory"""
    filelist = []
    flag = flag_path_tup[0]
    pathname = flag_path_tup[1]
    if flag == "file":
        if not os.path.isfile(pathname):
            raise IOError("%s is not a valid file." % pathname)
        else:
            filelist.append(pathname)
    elif flag == "directory":
        if not os.path.isdir(pathname):
            raise IOError("%s is not a valid directory." % pathname)
        else:
            for filename in os.listdir(pathname):
                if not os.path.isfile(os.path.join(pathname, filename)):
                    sys.stderr.write(
                        "Error: %s in directory %s is not a valid file." % (filename, pathname))
                    continue
                else:
                    filelist.append(os.path.join(pathname, filename))
    return filelist


def is_mp3_file(filename):
    header_info = subprocess.Popen(
        ["file", filename], stdout=subprocess.PIPE).stdout.read()
    return MP3_STRING in header_info


def is_wave_file(filename):
    header_info = subprocess.Popen(
        ["file", filename], stdout=subprocess.PIPE).stdout.read()
    if (("RIFF" in header_info) and ("WAVE" in header_info)):
        return True
    else:
        return False


def read_file(filename):
    if is_mp3_file(filename):
        wavefile = mp3_to_wave_subprocess()
        song_info = SongInfo.from_file(wavefile)
    elif is_wave_file:
        song_info = SongInfo.from_file(filename)
    else:
        sys.stderr.write("%(filename)s is not in a supported format.")
    if song_info:
        return song_info
    



    # try:
    #     song_info = SongInfo.from_file(filename)
    # except wave.Error:
    #     try:
    #         wavefile = mp3_to_wave_subprocess(filename)
    #         song_info = SongInfo.from_file(wavefile)
    #     except subprocess.CalledProcessError as e:
    #         sys.stderr.write("Invalid file %s. Error: %s" % (filename, e))
    #     except Exception as e:
    #         sys.stderr.write("Exception: %s" % e)
    # if song_info:
    #     return song_info


def read_files(filelist):
    """Records audio file info into SongInfo objects"""
    song_info_list = []
    for filename in filelist:
        song_info = read_file(filename)
        if song_info:
            song_info_list.append(song_info)
    return song_info_list
