import os
import shutil
import string
import subprocess
import sys
import tempfile 
import wave
from songidentity import SongInfo

#LAME_DECODE = "/course/cs4500f13/bin/lame -a --silent --decode -b 96 %s %s"
LAME_DECODE = "/opt/local/bin/lame -a --silent --decode -s 24 %s %s"
#LAME_ENCODE = "/course/cs4500f13/bin/lame -a --silent -b 96 %s %s"
LAME_ENCODE = "/opt/local/bin/lame -a --silent %s %s"
MP3_STRING = "MPEG ADTS, layer III"


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

def mp3_to_canonical(mp3, tempdir):
    wav = "%s/%s.wav" % (tempdir, os.path.splitext(os.path.basename(mp3))[0])
    decode = LAME_DECODE % (mp3, wav)
    subprocess.call(decode.split(" "))
    return wav

def wav_to_canonical(wav, tempdir):
    mp3 = "%s/%s.mp3" % (tempdir, os.path.splitext(os.path.basename(wav))[0])
    wav2 = "%s/%s.wav" % (tempdir, os.path.splitext(os.path.basename(wav))[0])
    encode = LAME_ENCODE % (wav, mp3)
    subprocess.call(encode.split(" "))
    decode = LAME_DECODE % (mp3, wav2)
    subprocess.call(decode.split(" "))
    return wav2

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


def read_file(filename, tempdir):
    if is_mp3_file(filename):
        name = os.path.basename(filename)
        canonical_wave = mp3_to_canonical(filename, tempdir)
        song_info = SongInfo.from_file(canonical_wave)
        song_info.set_name(name)
        return song_info
    elif is_wave_file(filename):
        canonical_wave = wav_to_canonical(filename, tempdir)
        song_info = SongInfo.from_file(canonical_wave)
        return song_info
    else:
        sys.stderr.write("%s is not in a supported format." % filename)


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
