import os
import time
import cPickle as pickle

print 'starting...'
start = time.time()

with open(os.path.join(os.environ.get('NLP_DATA'), 'word-frequencies-pos')) as f:
  dict_word_freq_lines = f.read().splitlines()
  dict_word_freq_lines = [line.split(',') for line in dict_word_freq_lines]
  dict_word_freq = {}
  for word, pos, freq in dict_word_freq_lines:
    if word in dict_word_freq:
      dict_word_freq[word] += float(freq)
    else:
      dict_word_freq[word] = float(freq)

### Frequency split by part of speech - cannot map to spaCy "pos_" yet
# pos_map = {
#   'a': 'DET',
#   'c': 'CONJ',
#   'd': 'DET',
#   'e': 'ADV',
#   'i': 'ADP',
#   'j': 'ADJ',
#   'm': 'NUM',
#   'n': 'NOUN',
#   'p': 'PRON',
#   'r': 'ADV',
#   't': 'PART',
#   'u': 'INTJ',
#   'v': 'VERB',
#   'x': 'ADV'
# }
# with open(os.path.join(os.environ.get('NLP_DATA'), 'word-frequencies')) as f:
#   dict_word_freq_lines = f.read().splitlines()
#   dict_word_freq_lines = [line.split(',') for line in dict_word_freq_lines]
#   dict_word_freq = {}
#   for word, pos, freq in dict_word_freq_lines:
#     if word in dict_word_freq:
#       dict_word_freq[word][pos_map[pos]] = float(freq)
#     else:
#       dict_word_freq[word] = {pos_map[pos]: float(freq)}

print 'loaded word frequency data.'
print time.time()-start

with open(os.path.join(os.environ.get('NLP_DATA'), 'word-frequencies.pkl'), 'wb') as f:
 pickle.dump(dict_word_freq, f, pickle.HIGHEST_PROTOCOL)
