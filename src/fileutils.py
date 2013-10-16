import os
from songidentity import SongInfo

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
		song_info = SongInfo.from_file(filename)
		song_info_list.append(song_info)
	return song_info_list
