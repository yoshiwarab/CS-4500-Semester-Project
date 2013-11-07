import fileutils
import numpy as np
import scipy
import sys
import wave
from array import array


class SongInfo(object):

    """Class to encapsulate song data and info."""

    @classmethod
    def from_file(cls, filename):
        """Create song_info object from wave file"""
        wavefile = wave.open(filename, 'r')
        nframes = wavefile.getnframes()
        nchannels = wavefile.getnchannels()
        sample_rate = wavefile.getframerate()
        song_info = cls(filename, nchannels, sample_rate)
        return song_info

    def __init__(self, filename, nchannels, sample_rate):
        """Constructor for SongInfo.
        filename is a string indicating a path to a wave file.
        nchannels is the number of channels the wave file contains.
        """
        self.name = self.get_name(filename)
        self.nchannels = nchannels
        self.sample_rate = sample_rate
        self.matches = []

    def get_name(self, filepath):
        """Given a full filepath, returns just the wave file name"""
        pathlist = filepath.split('/')
        name = pathlist[len(pathlist) - 1]
        return name

    def get_chunks(self, wavefile):
        id awld


class SongChunk(object):

    """Class to encapsulate a chunk from a song"""

    def generate_chunks(self, bytestring):

