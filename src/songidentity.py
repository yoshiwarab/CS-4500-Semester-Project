import numpy as np
import wave
from array import array
from operator import itemgetter
from scipy.stats import linregress
import pylab
import hashlib

CHUNK_SIZE = 1024


class SongInfo(object):

    """Class to encapsulate song data and info."""

    @classmethod
    def from_file(cls, filename):
        """Create song_info object from wave file"""
        wavefile = wave.open(filename, 'r')
        nchannels = wavefile.getnchannels()
        sample_rate = wavefile.getframerate()
        song_info = cls(filename, nchannels, sample_rate)
        song_info.chunk_wavefile(wavefile)
        wavefile.close()
        return song_info

    def __init__(self, filename, nchannels, sample_rate):
        """Constructor for SongInfo.
        filename is a string indicating a path to a wave file.
        nchannels is the number of channels the wave file contains.
        """
        self.name = self.get_name(filename)
        self.nchannels = nchannels
        self.sample_rate = sample_rate

    def get_name(self, filepath):
        """Given a full filepath, returns just the wave file name"""
        pathlist = filepath.split('/')
        name = pathlist[len(pathlist) - 1]
        return name

    def chunk_wavefile(self, wavefile):
        time = 0
        chunks = {}
        while True:
            chunk_string = wavefile.readframes(CHUNK_SIZE)
            if len(chunk_string) > 0:
                chunk = SongChunk.from_bytestring(
                    time, chunk_string, self.nchannels)
                if chunk is not None:
                    chunks[chunk.hash()] = chunk
                time += round((float(CHUNK_SIZE) / self.sample_rate), 3)
            else:
                break
        self.chunks = chunks

    """def compare(self, song2):
                    song1_chunks_set = set(self.chunks.keys())
                    song2_chunks_set = set(song2.chunks.keys())
                    intersection = song1_chunks_set.intersection(song2_chunks_set)
                    if float(len(intersection))/len(song2_chunks_set) > 0.3:
                        print 'Match: %s %s' % (self.name, song2.name)
                    elif float(len(intersection))/len(song1_chunks_set) > 0.3:
                        print 'Match: %s %s' % (self.name, song2.name)"""

    def compare(self, song2):
        song1_match_times = []
        song2_match_times = []
        for chunk_hash,chunk in self.chunks.items():
            if chunk_hash in song2.chunks:
                song1_match_times.append(chunk.time)
                song2_match_times.append(song2.chunks[chunk_hash].time)
            #print "Comparing: %s %s" % (self.name, song2.name)
            #pylab.plot(song1_match_times, song2_match_times, '.')
            #pylab.show()
        #print "%s Match Times: %s\n" % (self.name, sorted(song1_match_times))
        #print "%s Match Times: %s\n" % (song2.name, sorted(song2_match_times))
        if self.consecutive_time_chunk_match(sorted(song1_match_times), 1):
            print "Match: %s %s" % (self.name, song2.name)
        """if len(song1_match_times) > 5:
                                    r2 = linregress(np.array(song1_match_times), np.array(song2_match_times))[2]**2
                                    if r2 > .5:
                                        print "Match: %s %s" % (self.name, song2.name)"""

    def consecutive_time_chunk_match(self, song1_chunk_times, song2_chunk_times, step_size, match_threshol):
        chain = []
        prev = None
        for i in range(len(sorted_list)-1):
            if not chain:
                chain.append(sorted_list[i])
            if len(chain) > 20:
                return True
            if (sorted_list[i+1] - sorted_list[i]) <= step_size:
                chain.append(sorted_list[i+1])
            else:
                return False



class SongChunk(object):

    """Class to encapsulate a chunk from a song"""

    @classmethod
    def from_bytestring(cls, time, bytestring, nchannels):
        integer_array = byte_string_to_integer_array(bytestring, nchannels)
        frequencies = abs(np.fft.rfft(integer_array))
        if len(frequencies) < 181:
            return None
        return cls(time, [get_max_per_range(frequencies, x[0], x[1]) for x in ((40, 80), (80, 120), (120, 180), (180, 300))])

    def __init__(self, time, bins):
        self.time = time
        self.bins = bins

    def hash(self):
        """ Returns a 32-bit int identifying the chunk """
        a, b, c, d = [x[0] for x in self.bins]
        f = 2
        return (d-(d%f)) * 100000000 + (c-(c%f)) * 100000 + (b-(b%f)) * 100 + (a-(a%f)) & 0xffffffff

def get_max_per_range(r, a, b):
    """ Returns the maximum value within the given range
    in the form (index, value).
    """
    return max(enumerate(r[a:b], a), key=itemgetter(1))


def byte_string_to_integer_array(bytestring, nchannels):
        """Converts output bytestring from wave.readframes into a 
        signed integer array and converts from stereo to mono
        if neccessary.
        """
        raw_array = array('h', bytestring)
        if nchannels == 2:
            left = raw_array[0::2]
            right = raw_array[1::2]
            mono = [(left[i] + right[i]) / 2 for i in range(0, len(left))]
        else:
            mono = raw_array
        return mono
