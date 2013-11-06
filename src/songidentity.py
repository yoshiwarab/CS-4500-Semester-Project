#!/usr/bin/env python
import fileutils
import numpy as np
import scipy
import sys
import wave
from array import array

class SongInfo():
    """Class to encapsulate song data and info."""

    @classmethod
    def from_file(self, filename):
        wavefile = wave.open(filename, 'r')
        nframes = wavefile.getnframes()
        nchannels = wavefile.getnchannels()
        song_info = self(filename, nchannels)
        bytestring = wavefile.readframes(nframes)
        song_info.byte_string_to_integer_array(bytestring)
        wavefile.close()
        return song_info
    
    def __init__(self, filename, nchannels):
        self.name = self.get_name(filename)
        self.nchannels = nchannels
        self.wave_integer_array = None
        self.matches = []

    def get_name(self, filepath):
        pathlist = filepath.split('/')
        name = pathlist[len(pathlist)-1]
        return name

    def compare_bytestring(self, song_info):
        """Compares song"""
        if song_info.bytestring == self.bytestring:
            self.matches.append(song_info.name)

    def byte_string_to_integer_array(self, bytestring):
        """Converts output string from wave.readframes into a signed integer array"""
        raw_array = array('h', bytestring)
        if self.nchannels == 2:
            left = raw_array[0::2]
            right = raw_array[1::2]
            mono = [(left[i] + right[i])/2 for i in range(0, len(left))]
        else:
            mono = raw_array
        self.wave_integer_array = mono

    def compare(self, song_info):
        """If the files are the same lenght do a numpy correlation check otherwise string search."""
        if len(self.wave_integer_array) == len(song_info.wave_integer_array):
            correlation_matrix = np.corrcoef(self.wave_integer_array,
                                                song_info.wave_integer_array)
            if correlation_matrix[0][1] > .7:
                print "MATCH: %s %s" % (self.name, song_info.name)
        elif (self.wave_integer_array in song_info.wave_integer_array or
              song_info.wave_integer_array in self.wave_integer_array):
            print "MATCH: %s %s" % (self.name, song_info.name)

def compare_song_info_lists(song_info_list1, song_info_list2):
    for song1 in song_info_list1:
        for song2 in song_info_list2:
            if song1 and song2:
                song1.compare(song2)

def main(argv):
    dir1 = argv[1]
    dir2 = argv[2]
    filelist1 = fileutils.gen_file_list(dir1)
    filelist2 = fileutils.gen_file_list(dir2)
    song_info_list1 = fileutils.readfiles(filelist1)
    song_info_list2 = fileutils.readfiles(filelist2)
    compare_song_info_lists(song_info_list1, song_info_list2)

if __name__ == '__main__':
    main(sys.argv)
