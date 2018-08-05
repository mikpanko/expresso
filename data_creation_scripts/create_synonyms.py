import os
import nltk
import time
import cPickle as pickle
with open(os.path.join(os.environ.get('NLP_DATA'), 'vulgar-words')) as f:
  dict_vulgar_words = f.read().splitlines()

print 'starting...'
start = time.time()
dict_wn = nltk.corpus.wordnet
words = [w for w in list(set(w for w in dict_wn.words())) if ('_' not in w)]
pos_map = {'nouns': ['n'], 'adjectives': ['a', 's'], 'verbs': ['v'], 'adverbs': ['r']}
print 'loaded WordNet data.'
print time.time()-start

print 'starting to look for synonyms...'
all_synonyms = {'nouns': {}, 'verbs': {}, 'adjectives': {}, 'adverbs': {}}
for idx, word in enumerate(words):
  if (idx % 5000) == 0:
    print 'processing word ' + str(idx) + '...'
    print time.time()-start
  for pos in pos_map.keys():
    synonyms = []
    for synset in dict_wn.synsets(word, pos=pos_map[pos]):
      synonyms.extend([syn.lower() for syn in synset.lemma_names() if ((syn not in dict_vulgar_words) and ('_' not in syn))])
    synonyms = list(set(synonyms) - set([word]))
    if len(synonyms):
      all_synonyms[pos][word] = synonyms
print 'created dictionary of synonyms.'
print time.time()-start
print ' '
print len(all_synonyms['nouns'])
print len(all_synonyms['verbs'])
print len(all_synonyms['adjectives'])
print len(all_synonyms['adverbs'])

with open(os.path.join(os.environ.get('NLP_DATA'), 'synonyms.pkl'), 'wb') as f:
  pickle.dump(all_synonyms, f, pickle.HIGHEST_PROTOCOL)
