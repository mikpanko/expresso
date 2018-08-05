import os
import nltk
import time
import cPickle as pickle

print 'starting...'
start = time.time()
dict_cmu = nltk.corpus.cmudict.dict()
print 'loaded CMU data.'
print time.time()-start

print 'converting CMU data to optimize and use without nltk...'
cmu = {word: dict_cmu[word][0] for word in dict_cmu.keys()}
print 'converted CMU data.'
print time.time()-start

with open(os.path.join(os.environ.get('NLP_DATA'), 'phonemes.pkl'), 'wb') as f:
  pickle.dump(cmu, f, pickle.HIGHEST_PROTOCOL)
