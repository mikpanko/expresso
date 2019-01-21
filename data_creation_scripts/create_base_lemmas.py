import os
import nltk
import time
import cPickle as pickle

print 'starting...'
start = time.time()
dict_wn = nltk.corpus.wordnet
words = [w for w in list(set(w for w in dict_wn.words())) if ('_' not in w)]
print 'loaded WordNet data.'
print time.time()-start

print 'starting to look for base lemmas...'
base_lemmas = {}
for idx, word in enumerate(words):
  if (idx % 5000) == 0:
    print 'processing word ' + str(idx) + '...'
    print time.time()-start
  if word not in base_lemmas.keys():
    related_lemmas = []
    stack = [lm for lm in dict_wn.lemmas(word)]
    while len(stack):
      related_lemmas.extend(stack)
      stack = [lm for lemma in stack for lm in lemma.derivationally_related_forms() if (lm not in related_lemmas)]
    related_words = list(set([lm.name().lower() for lm in related_lemmas]))
    related_words_len = [len(w) for w in related_words]
    base_lemma = related_words[related_words_len.index(min(related_words_len))]
    base_lemmas.update({word: base_lemma for word in related_words if (word != base_lemma)})
print 'created dictionary of base lemmas.'
print time.time()-start
print ' '
print len(base_lemmas)

with open(os.path.join(os.environ.get('NLP_DATA'), 'base-lemmas.pkl'), 'wb') as f:
  pickle.dump(base_lemmas, f, pickle.HIGHEST_PROTOCOL)
