CHUNK_SIZE = 2048
# CHUNK_SIZE is the number of frames each chunk is derived from.

CHUNK_STEP_SIZE = 1
# CHUNK_STEP_SIZE is the maximum temporal difference between chunk matches
# still considered to be part of a sequence of matches.

HASH_FUZZ = 2
# HASH_FUZZ is the amount of error correction applied when hashing
# SongChunk objects.

MATCH_THRESHOLD = 5
# MATCH_THRESHOLD is the number of sequential matches between two songs
# required for a match.

# LAME_DECODE = "/opt/local/bin/lame -a --silent --decode -s 24 %s %s"
# Used for testing on local machine.

LAME_DECODE = "/course/cs4500f13/bin/lame -a --silent --decode -s 24 %s %s"
# Lame call to decode an mp3 file.

# LAME_ENCODE = "/opt/local/bin/lame -a --silent %s %s"
# Used for testing on local machine.

LAME_ENCODE = "/course/cs4500f13/bin/lame -a --silent %s %s"
# Lame call to encode an mp3 file.

MP3_STRING = "MPEG ADTS, layer III"
# String used to recognize an mp3 file.
