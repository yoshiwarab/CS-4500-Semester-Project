import constants
import numpy as np
import wave
from array import array
from operator import itemgetter
from scipy.stats import linregress
import pylab

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

    def set_name(self, name):
        self.name = name

    def chunk_wavefile(self, wavefile):
        time = 0
        chunks = {}
        while True:
            chunk_string = wavefile.readframes(constants.CHUNK_SIZE)
            if len(chunk_string) > 0:
                chunk = SongChunk.from_bytestring(
                    time, chunk_string, self.nchannels)
                if chunk is not None:
                    chunks[chunk.hash()] = chunk
                time = round(time + (float(constants.CHUNK_SIZE) / self.sample_rate), 3)
            else:
                break
        self.chunks = chunks

    def compare(self, song2):
        match_times = []
        shorter, longer = (sorted([self, song2], key = lambda x: len(x.chunks)))
        for chunk_hash,chunk in shorter.chunks.items():
            if chunk_hash in longer.chunks:
                match_times.append((chunk.time, longer.chunks[chunk_hash].time))
        if match_times:
            #sorted_match_times = sorted(match_times, key=itemgetter(0))
            #print sorted_match_times
            #pylab.plot(zip(*sorted_match_times)[0], zip(*sorted_match_times)[1], '.')
            #pylab.show()
            if self.consecutive_time_matches(sorted(match_times, key=itemgetter(0)), constants.CHUNK_STEP_SIZE, constants.MATCH_THRESHOLD):
                print "MATCH %s %s" % (shorter.name, longer.name)
            else:
                print "NO MATCH"
        else:
            print "NO MATCH"

    def consecutive_time_matches(self, sorted_match_times, step_size, match_threshold):
        chains = []
        chain = []
        for i in range(len(sorted_match_times)-1):
            if not chain:
                chain.append(sorted_match_times[i])
            if ((0 < (sorted_match_times[i+1][0] - sorted_match_times[i][0]) <= step_size)
                and (0 < (sorted_match_times[i+1][1] - sorted_match_times[i][1]) <= step_size)):
                chain.append(sorted_match_times[i+1])
            else:
                chains.append(chain)
                chain = []
        chains.append(chain)
        if chains:
            longest_chain = max(chains, key=lambda k: len(k))
            #if longest_chain:
                #pylab.plot(zip(*longest_chain)[0], zip(*longest_chain)[1], '.')
                #pylab.show()
            if len(longest_chain) >= match_threshold:
                return True
            else:
                return False
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
        f = constants.HASH_FUZZ
        #return (d-(d%f)) * 100000000 + (c-(c%f)) * 100000 + (b-(b%f)) * 100 + (a-(a%f)) & 0xffffffff
        return (((a - a%f) << 24) | ((b - b%f) << 16) | ((c - c%f) << 8) | (d - d%f)) & 0xffffffff

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
