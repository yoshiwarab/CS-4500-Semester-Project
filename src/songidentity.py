#!/usr/bin/env python

import fileutils
import numpy
import scipy
import sys
import wave
from array import array

class SongInfo():
    """Class to encapsulate song data and info."""
    @classmethod
    def from_file(self, filename):
        try:
            wavefile = wave.open(filename, 'r')
        except wave.Error:
            print "Error %s is invalid"
        nframes = wavefile.getnframes()
        nchannels = wavefile.getnchannels()
        song_info = self(filename, nchannels)
        bytestring = wavefile.readframes(nframes)
        song_info.byte_string_to_integer_array(bytestring)
        wavefile.close()
        return song_info

    def __init__(self, filename, nchannels):
        self.name = filename.split('/')[1]
        self.nchannels = nchannels
        self.wave_integer_array = None
        self.matches = []

    def compare_frames(self, song_info):
        """Compares song"""
        if song_info.frames == self.frames:
            self.matches.append(song_info.name)

    def byte_string_to_integer_array(self, bytestring):
        """Converts output string from wave.readframes into a signed integer array"""
        raw_array = array('h', bytestring)
        self.wave_integer_array = raw_array

    def compare(self, song_info):
        if len(self.wave_integer_array) == len(song_info.wave_integer_array):
            correlation_matrix = numpy.corrcoef(self.wave_integer_array,
                                                song_info.wave_integer_array)
            if correlation_matrix[0][1] > .7:
                print "MATCH: %s %s" % (self.name, song_info.name)
        elif (self.wave_integer_array in song_info.wave_integer_array or
              song_info.wave_integer_array in self.wave_integer_array):
            print "MATCH: %s %s" % (self.name, song_info.name)

    
def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    print thisrow[len(seq2) - 1]
    return thisrow[len(seq2) - 1]

def compare_song_info_lists(song_info_list1, song_info_list2):
    for song1 in song_info_list1:
        for song2 in song_info_list2:
            #song1.compare(song2)
            print levenshtein(song1.wave_integer_array, song2.wave_integer_array)


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
