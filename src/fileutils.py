import os
import subprocess
import wave
from songidentity import SongInfo

LAME_DECODE = "/course/cs4500f13/bin/lame --decode %s %s"

def mp3_to_wave_subprocess(mp3):
	"""convert mp3 to wave by calling lame in subprocess returns filename"""
	wav = "%s.wav" % os.path.splitext(mp3)[0]
	print wav
	decode = LAME_DECODE % (mp3, wav)
	print decode
	subprocess.check_call(decode.split(" "))
	return wav


def gen_file_list(dir):
	"""Generates a list of all files in the given directory"""
	filelist = []
	for file in os.listdir(dir):
		filelist.append(os.path.join(dir, file))
	return filelist

def readfiles(filelist):
	"""Records audio file info into SongInfo objects"""
	song_info_list = []
	for filename in filelist:
		try:
			song_info = SongInfo.from_file(filename)
		except wave.Error:
			print "%s is not in wave format, attempting to convert..." % filename
			try:
				wavefile = mp3_to_wave_subprocess(filename)
				SongInfo.from_file(wavefile)
			except subprocess.CalledProcessError as e:
				print "Invalid file %s. Error: %s" % (filename, e)
		if song_info:
			song_info_list.append(song_info)

	return song_info_list
