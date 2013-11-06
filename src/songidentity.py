import fileutils
import numpy as np
import scipy
import sys
import wave
from array import array

class SongInfo(object):
    """Class to encapsulate song data and info."""

    @classmethod
    def from_file(self, filename):
        """Create song_info object from wave file"""
        wavefile = wave.open(filename, 'r')
        nframes = wavefile.getnframes()
        nchannels = wavefile.getnchannels()
        song_info = self(filename, nchannels)
        bytestring = wavefile.readframes(nframes)
        song_info.byte_string_to_integer_array(bytestring)
        wavefile.close()
        return song_info
    
    def __init__(self, filename, nchannels):
        """Constructor for SongInfo.
        filename is a string indicating a path to a wave file.
        nchannels is the number of channels the wave file contains.
        """
        self.name = self.get_name(filename)
        self.nchannels = nchannels
        self.wave_integer_array = None
        self.matches = []

    def get_name(self, filepath):
        """Given a full filepath, returns just the wave file name"""
        pathlist = filepath.split('/')
        name = pathlist[len(pathlist)-1]
        return name

    def compare_bytestring(self, song_info):
        """Compares song bytestrings directly. Adds song being compared
        to self.matches if there is an exact match.
        """
        if song_info.bytestring == self.bytestring:
            self.matches.append(song_info.name)

    def byte_string_to_integer_array(self, bytestring):
        """Converts output bytestring from wave.readframes into a 
        signed integer array
        """
        raw_array = array('h', bytestring)
        if self.nchannels == 2:
            left = raw_array[0::2]
            right = raw_array[1::2]
            mono = [(left[i] + right[i])/2 for i in range(0, len(left))]
        else:
            mono = raw_array
        self.wave_integer_array = mono

    def compare(self, song_info):
        """If the files are the same length do a numpy correlation 
        check otherwise string search.
        """
        if len(self.wave_integer_array) == len(song_info.wave_integer_array):
            correlation_matrix = np.corrcoef(self.wave_integer_array,
                                                song_info.wave_integer_array)
            if correlation_matrix[0][1] > .7:
                print "MATCH: %s %s" % (self.name, song_info.name)
        elif (self.wave_integer_array in song_info.wave_integer_array or
              song_info.wave_integer_array in self.wave_integer_array):
            print "MATCH: %s %s" % (self.name, song_info.name)
