import constants
import os
import shutil
import subprocess
import sys
import tempfile
from songidentity import SongInfo
import wave

def is_mp3_file(filename):
    """Checks the header information in a specified file to determine if
    it is in mp3 format.
    """
    header_info = subprocess.Popen(
        ["file", filename], stdout=subprocess.PIPE).stdout.read()
    return constants.MP3_STRING in header_info


def is_wave_file(filename):
    """Checks the header information in a specified file to determine if
    it is in wave format.
    """
    header_info = subprocess.Popen(
        ["file", filename], stdout=subprocess.PIPE).stdout.read()
    if (("RIFF" in header_info) and ("WAVE" in header_info)):
        return True
    else:
        return False


def mp3_to_canonical(mp3, tempdir):
    """Converts an mp3 file to canonical wave format"""
    base = os.path.basename(mp3)
    mp3two = "%s/%s.mp3" % (tempdir, base)
    mp3_canonical = "%s/%s_canonical.mp3" % (tempdir, base)
    wav_canonical = "%s/%s_canonical.wav" % (tempdir, base)
    shutil.copy(mp3, mp3two)
    encode = constants.LAME_ENCODE % (mp3two, mp3_canonical)
    subprocess.call(encode.split(" "))
    decode = constants.LAME_DECODE % (mp3_canonical, wav_canonical)
    subprocess.call(decode.split(" "))
    return wav_canonical


def wav_to_canonical(wav, tempdir):
    """Converts a wave file to canoncial format"""
    base = os.path.basename(wav)
    mp3 = "%s/%s.mp3" % (tempdir, base)
    wav2 = "%s/%s.wav" % (tempdir, base)
    wav_canonical = "%s/%s_canonical.wav" % (tempdir, base)
    shutil.copy(wav, wav2)
    encode = constants.LAME_ENCODE % (wav2, mp3)
    subprocess.call(encode.split(" "))
    decode = constants.LAME_DECODE % (mp3, wav_canonical)
    subprocess.call(decode.split(" "))
    return wav_canonical


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
                if os.path.isdir(os.path.join(pathname, filename)):
                    sys.stderr.write(
                        ("ERROR: %s is a subdirectory of %s and will " 
                         "not be handled\n" % (filename, pathname)))
                if not os.path.isfile(os.path.join(pathname, filename)):
                    sys.stderr.write(
                        ("ERROR: %s in directory %s is not a valid " 
                         "file.\n") % (filename, pathname))
                    continue
                else:
                    filelist.append(os.path.join(pathname, filename))
    return filelist


def read_file(filename, tempdir):
    """Checks that the specified file is valid and returns a SongInfo
    object representing the file data if it is.
    """
    if is_mp3_file(filename):
        name = os.path.basename(filename)
        canonical_wave = mp3_to_canonical(filename, tempdir)
        song_info = SongInfo.from_file(canonical_wave)
        song_info.set_name(name)
        return song_info
    elif is_wave_file(filename):
        name = os.path.basename(filename)
        canonical_wave = wav_to_canonical(filename, tempdir)
        song_info = SongInfo.from_file(canonical_wave)
        song_info.set_name(name)
        return song_info
    else:
        sys.stderr.write("ERROR: %s is not in a supported format.\n" % filename)


def read_files(filelist):
    """Records audio file info into SongInfo objects"""
    song_info_list = []
    tempdir = tempfile.mkdtemp(prefix='/tmp/')
    for filename in filelist:
        song_info = read_file(filename, tempdir)
        if song_info:
            song_info_list.append(song_info)
    shutil.rmtree(tempdir)
    return song_info_list
