import constants
import numpy as np
import wave
from array import array
from operator import itemgetter


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
        """Set the chunk file name attribute."""
        self.name = name

    def chunk_wavefile(self, wavefile):
        """Read in the wavefile and create a list of SongChunk objects
        to represent it.
        """
        time = 0
        chunks = {}
        while True:
            chunk_string = wavefile.readframes(constants.CHUNK_SIZE)
            if len(chunk_string) > 0:
                chunk = SongChunk.from_bytestring(
                    time, chunk_string, self.nchannels)
                if chunk is not None:
                    chunks[chunk.hash()] = chunk
                time = round(time +
                             (float(constants.CHUNK_SIZE) / self.sample_rate),
                             3)
            else:
                break
        self.chunks = chunks

    def compare(self, song2):
        """
        Compares self to another song SongInfo object.  If the songs the
        objects are derived from are likely from the same source we print
        MATCH and the name attribute of the two objects.  If not, we print
        NO MATCH.
        """
        match_times = []
        shorter, longer = (sorted([self, song2],
                                  key=lambda x: len(x.chunks)))
        for chunk_hash, chunk in shorter.chunks.items():
            if chunk_hash in longer.chunks:
                match_times.append(
                    (chunk.time, longer.chunks[chunk_hash].time))
        if match_times:
            sorted_match_times = sorted(match_times, key=itemgetter(1))
            if self.consecutive_time_matches(sorted_match_times,
                                             constants.CHUNK_STEP_SIZE,
                                             constants.MATCH_THRESHOLD):
                print "MATCH %s %s" % (shorter.name, longer.name)
            else:
                print "NO MATCH"
        else:
            print "NO MATCH"

    def consecutive_time_matches(self, sorted_match_times, step_size,
                                 match_threshold):
        """Returns true if the number of sequential matches in
        sorted_match_times is greater than the match match_threshold.
        Step size is used to determine what is considered sequential.
        """
        chains = []
        chain = []
        for i in range(len(sorted_match_times) - 1):
            shorter_match_diff = sorted_match_times[i + 1][0] - \
                sorted_match_times[i][0]
            longer_match_diff = sorted_match_times[i + 1][1] - \
                sorted_match_times[i][1]

            if not chain:
                chain.append(sorted_match_times[i])
            if (0 < longer_match_diff <= step_size):
                    #and (0 < s2_match_diff <= step_size)):
                chain.append(sorted_match_times[i + 1])
            else:
                chains.append(chain)
                chain = []
        chains.append(chain)
        if chains:
            longest_chain = max(chains, key=lambda k: len(k))
            if len(longest_chain) >= match_threshold:
                return True
            else:
                return False
        return False


class SongChunk(object):

    """Class to encapsulate a chunk from a song"""

    @classmethod
    def from_bytestring(cls, time, bytestring, nchannels):
        """Create a SongChunk object from a bytestring.
        """
        integer_array = byte_string_to_integer_array(bytestring, nchannels)
        frequencies = abs(np.fft.rfft(integer_array))
        if len(frequencies) < 181:
            return None
        return cls(time,
                   [get_max_per_range(frequencies, x[0], x[1]) for x in
                    ((40, 80), (80, 120), (120, 180), (180, 300))])

    def __init__(self, time, bins):
        self.time = time
        self.bins = bins

    def hash(self):
        """ Returns an identifying the chunk """
        a, b, c, d = [x[0] for x in self.bins]
        f = constants.HASH_FUZZ
        return hash((d - d % f, c - c % f, b - b % f, a - a % f))


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
