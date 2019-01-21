from __future__ import division
import os
import cPickle as pickle
import re
from bs4 import BeautifulSoup
from numpy import std
import spacy
import time

# pre-load and pre-compile required variables and methods
nlp = spacy.load('en_core_web_sm')
html_div_br_div_re = re.compile('</div><div><br></div>')
html_newline_re = re.compile('(<br|</div|</p)')
quotation_re = re.compile(u'[\u00AB\u00BB\u201C\u201D\u201E\u201F\u2033\u2036\u301D\u301E]')
apostrophe_re = re.compile(u'[\u02BC\u2019\u2032]')
nominalization_re = re.compile('(?:ion|ions|ism|isms|ty|ties|ment|ments|ness|nesses|ance|ances|ence|ences)$')
with open(os.path.join(os.environ.get('NLP_DATA'), 'synonyms.pkl')) as f:
  dict_synonyms = pickle.load(f)
with open(os.path.join(os.environ.get('NLP_DATA'), 'base-lemmas.pkl')) as f:
  dict_base_lemmas = pickle.load(f)
with open(os.path.join(os.environ.get('NLP_DATA'), 'phonemes.pkl')) as f:
  dict_phonemes = pickle.load(f)
with open(os.path.join(os.environ.get('NLP_DATA'), 'weak-verbs')) as f:
  dict_weak_verbs = f.read().splitlines()
with open(os.path.join(os.environ.get('NLP_DATA'), 'entity-substitutions')) as f:
  dict_entity_substitutions = f.read().splitlines()
with open(os.path.join(os.environ.get('NLP_DATA'), 'filler-words')) as f:
  dict_fillers = f.read().splitlines()
with open(os.path.join(os.environ.get('NLP_DATA'), 'stop-words')) as f:
  dict_stop_words = f.read().splitlines()
nlp.Defaults.stop_words = dict_stop_words
with open(os.path.join(os.environ.get('NLP_DATA'), 'word-frequencies.pkl')) as f:
  dict_word_freq = pickle.load(f)
def is_word(token):
  return token.text[0].isalnum() or (token.pos_ in ['VERB', 'PRON'])  # sometimes words are shortened to non-alnum strings like "'s"

def analyze_text(html):
  # create data and metrics dictionaries
  data = dict()
  metrics = dict()

  ### parse text/html string

  # strip html tags
  html = html_div_br_div_re.sub(r'</div>\n', html)
  html = html_newline_re.sub(lambda m: '\n'+m.group(0), html)
  soup = BeautifulSoup(html, 'html.parser')
  original_text = soup.get_text().rstrip('\n')

  # standardize all quotation marks
  # this will make spaCy sentence segmentation more stable
  text = quotation_re.sub('"', original_text)
  text = apostrophe_re.sub("'", text)

  # parse text
  doc = nlp(text)
  data['values'] = [token.text for token in doc]
  data['parts_of_speech'] = [token.tag_ for token in doc]
  data['pos_high_level'] = [token.pos_ for token in doc]
  data['syntax_relations'] = [token.dep_ for token in doc]
  data['words'] = [is_word(token) for token in doc]
  data['punctuation_marks'] = [token.is_punct for token in doc]
  data['numbers_of_characters'] = [len(token.text) if is_word(token) else None for token in doc]
  data['stopwords'] = [(token.lower_ in dict_stop_words) if is_word(token) else None for token in doc]

  # find sentences
  # need to manually merge some of sentences identified by spaCy to make sure all of them end with an appropriate punctuation mark
  sents = []
  sents_end_punct = []
  sents_start_idx = []
  new_sent = []
  for sent in doc.sents:
    if not new_sent:
      sents_start_idx.append(sent.start)
    new_sent.extend(sent)
    for token in reversed(sent):
      if token.text[0] in ['.', '?', '!']:  # need to account for some sentences ending in several punctuation marks: "?!", "?-", etc
        sents.append(new_sent)
        sents_end_punct.append(token.text[0])
        new_sent = []
        break
  if new_sent:
    sents.append(new_sent)
    sents_end_punct.append(None)
  data['sentence_numbers'] = [(idx+1) for idx, sent in enumerate(sents) for token in sent]
  data['sentence_end_punctuations'] = [sents_end_punct[idx] for idx, sent in enumerate(sents) for token in sent]

  # find subjects, predicates, clauses and sentence types based on syntactic structure
  data['principal_parts'] = [None] * len(doc)
  data['independent_principal_parts'] = [None] * len(doc)
  sents_types = ['simple'] * len(sents)
  sents_clauses = [0] * len(sents)
  subj_tags = ['nsubj', 'nsubjpass', 'expl']
  for idx, sent in enumerate(sents):
    is_compound = False
    is_complex = False
    roots = [token for token in sent if (token.dep_ == 'ROOT') and (token.pos_ == 'VERB')]
    if len(roots) is 0:
      sents_types[idx] = 'fragment'
      sents_clauses[idx] = 1
      continue
    for root in roots:
      data['independent_principal_parts'][root.i] = 'predicate'
      data['principal_parts'][root.i] = 'predicate'
      sents_clauses[idx] += 1
    for subj in [token for token in sent if (token.dep_ in subj_tags) and (token.head.pos_ == 'VERB')]:
      data['principal_parts'][subj.i] = 'subject'
      if subj.head.dep_ == 'ROOT':
        data['independent_principal_parts'][subj.i] = 'subject'
      else:
        data['principal_parts'][subj.head.i] = 'predicate'
        sents_clauses[idx] += 1
        if subj.head.dep_ in ['parataxis', 'conj']:
          is_compound = True
        else:
          is_complex = True
    for conj in [token for token in sent if (token.dep_ == 'conj') and not data['principal_parts'][token.i]]:
        data['principal_parts'][conj.i] = data['principal_parts'][conj.head.i]
        data['independent_principal_parts'][conj.i] = data['independent_principal_parts'][conj.head.i]
    if is_complex and is_compound:
      sents_types[idx] = 'complex-compound'
    elif is_compound:
      sents_types[idx] = 'compound'
    elif is_complex:
      sents_types[idx] = 'complex'
  data['sentence_types'] = [sents_types[idx] for idx, sent in enumerate(sents) for token in sent]

  # find words
  words = []
  word2token_map = []
  for idx, token in enumerate(doc):
    if data['words'][idx]:
      words.append(token.lower_)
      word2token_map.append(idx)

  # find lemmas
  data['lemmas'] = [token.lemma_ if is_word(token) else None for token in doc]
  for idx, lemma in enumerate(data['lemmas']):
    if lemma == '-PRON-': # spaCy replaces pronouns with '-PRON-' so we need to fix it
      data['lemmas'][idx] = data['values'][idx].lower()

  # find groups of verbs making up predicates & auxiliary verbs within them
  data['verb_groups'] = [None] * len(doc)
  data['auxiliary_verbs'] = [False if is_word(token) else None for token in doc]
  verb_group_stack = []
  verb_group_count = 0
  for idx, token in enumerate(doc):
    if not verb_group_stack:
      if token.text in ["be", "am", "'m", "is", "are", "'re", "was", "were", "will", "'ll", "wo", "have", "'ve", "has", "had", "'d"]:
        verb_group_stack.append(idx)
      elif (token.text is "'s") and (token.pos_ is 'VERB'):
        verb_group_stack.append(idx)
    elif token.text in ['be', 'been', 'being', 'have', 'had']:
      verb_group_stack.append(idx)
    elif data['pos_high_level'][idx] == 'VERB':
      verb_group_stack.append(idx)
      verb_group_count += 1
      for i in verb_group_stack:
        data['verb_groups'][i] = verb_group_count
      for j in verb_group_stack[:-1]:
        data['auxiliary_verbs'][j] = True
      verb_group_stack = []
    elif data['parts_of_speech'][idx][:2] not in ['RB', 'PD']:
      if len(verb_group_stack) > 1:
        verb_group_count += 1
        for i in verb_group_stack:
          data['verb_groups'][i] = verb_group_count
        for j in verb_group_stack[:-1]:
          data['auxiliary_verbs'][j] = True
      verb_group_stack = []

  # find synonyms and base lemmas
  data['synonyms'] = [None] * len(doc)
  data['base_lemmas'] = [None] * len(doc)
  pos_map = {'NN': 'nouns', 'JJ': 'adjectives', 'VB': 'verbs', 'RB': 'adverbs'}
  for idx_word, word in enumerate(words):
    idx = word2token_map[idx_word]
    pos = data['parts_of_speech'][idx][:2]
    if (pos in pos_map) and (word in dict_synonyms[pos_map[pos]]):
      data['synonyms'][idx] = dict_synonyms[pos_map[pos]][word]
    else:
      data['synonyms'][idx] = []
    if data['lemmas'][idx] in dict_base_lemmas:
      data['base_lemmas'][idx] = dict_base_lemmas[data['lemmas'][idx]]
    else:
      data['base_lemmas'][idx] = data['lemmas'][idx]

  # find expected word frequencies
  data['expected_word_frequencies'] = [0 if is_word(token) else None for token in doc]
  for idx_word, word in enumerate(words):
    idx = word2token_map[idx_word]
    lemma = data['lemmas'][idx]
    base_lemma = data['base_lemmas'][idx]
    if lemma in dict_word_freq:
      data['expected_word_frequencies'][idx] = dict_word_freq[lemma]
    elif base_lemma in dict_word_freq:
      data['expected_word_frequencies'][idx] = dict_word_freq[base_lemma]

  ### compute metrics on parsed data

  # count number of sentences
  metrics['sentence_count'] = len(sents)

  # count number of words
  metrics['word_count'] = len(words)

  # count number of words per sentence and its standard deviation
  sents_words = [[token.lower_ for token in sent if is_word(token)] for sent in sents]
  sents_length = [len(sent) for sent in sents_words]
  if len(sents_length):
    metrics['words_per_sentence'] = sum(sents_length) / len(sents_length)
  else:
    metrics['words_per_sentence'] = 0
  if len(sents_length) >= 10:
    metrics['std_of_words_per_sentence'] = std(sents_length)
  else:
    metrics['std_of_words_per_sentence'] = -1

  # find extra long and short sentences
  if len(sents_length):
    metrics['long_sentences_ratio'] = len([1 for sent_length in sents_length if sent_length >= 40]) / len(sents_length)
    metrics['short_sentences_ratio'] = len([1 for sent_length in sents_length if sent_length <= 6]) / len(sents_length)
  else:
    metrics['long_sentences_ratio'] = 0
    metrics['short_sentences_ratio'] = 0

  # find vocabulary size
  metrics['vocabulary_size'] = len(set(data['base_lemmas'])) - 1  # subtract 1 for non-words

  # count sentence types based on ending punctuation mark
  if metrics['sentence_count']:
    metrics['declarative_ratio'] = sents_end_punct.count('.') / metrics['sentence_count']
    metrics['interrogative_ratio'] = sents_end_punct.count('?') / metrics['sentence_count']
    metrics['exclamative_ratio'] = sents_end_punct.count('!') / metrics['sentence_count']
  else:
    metrics['declarative_ratio'] = 0
    metrics['interrogative_ratio'] = 0
    metrics['exclamative_ratio'] = 0

  # count sentence types based on clause structure
  if metrics['sentence_count']:
    metrics['simple_ratio'] = sents_types.count('simple') / metrics['sentence_count']
    metrics['fragment_ratio'] = sents_types.count('fragment') / metrics['sentence_count']
    metrics['complex_ratio'] = sents_types.count('complex') / metrics['sentence_count']
    metrics['compound_ratio'] = sents_types.count('compound') / metrics['sentence_count']
    metrics['complex_compound_ratio'] = sents_types.count('complex-compound') / metrics['sentence_count']
  else:
    metrics['simple_ratio'] = 0
    metrics['fragment_ratio'] = 0
    metrics['complex_ratio'] = 0
    metrics['compound_ratio'] = 0
    metrics['complex_compound_ratio'] = 0

  # compute subject-, predicate- and clause-related metrics
  data['clause_heavy_sentences'] = [False] * len(doc)
  sents_predicate_depth = [0] * len(sents)
  data['late_predicates'] = [False] * len(doc)
  data['detached_subjects'] = [False] * len(doc)
  metrics['many_clauses_ratio'] = 0
  metrics['late_predicates_ratio'] = 0
  metrics['detached_subjects_ratio'] = 0
  sents_with_predicate_count = 0
  for idx, sent in enumerate(sents):
    s1 = sents_start_idx[idx]
    s2 = sents_start_idx[idx]+len(sent)
    syntax_mask = data['independent_principal_parts'][s1:s2]
    if 'predicate' in syntax_mask:
      pred_idx = syntax_mask.index('predicate')
      pred_depth = sum([1 for token in sent[:pred_idx] if is_word(token)]) + 1
      sents_with_predicate_count += 1
    else:
      continue
    sents_predicate_depth[idx] = pred_depth
    if sents_clauses[idx] >= 4:
      data['clause_heavy_sentences'][s1:s2] = [(i != None) for i in data['principal_parts'][s1:s2]]
      metrics['many_clauses_ratio'] += 1
    if pred_depth > 10:
      data['late_predicates'][sents_start_idx[idx]+pred_idx] = True
      metrics['late_predicates_ratio'] += 1
    if 'subject' in syntax_mask:
      subj_idx = syntax_mask.index('subject')
      subj_depth = sum([1 for token in sent[:subj_idx] if is_word(token)])
      if (pred_depth - subj_depth > 5):
        data['detached_subjects'][sents_start_idx[idx]+pred_idx] = True
        data['detached_subjects'][sents_start_idx[idx]+subj_idx] = True
        metrics['detached_subjects_ratio'] += 1
  if sents_with_predicate_count:
    metrics['predicate_depth'] = sum(sents_predicate_depth) / sents_with_predicate_count
    metrics['late_predicates_ratio'] = metrics['late_predicates_ratio'] / sents_with_predicate_count
    metrics['detached_subjects_ratio'] = metrics['detached_subjects_ratio'] / sents_with_predicate_count
  else:
    metrics['predicate_depth'] = 0
  if metrics['sentence_count']:
    metrics['clauses_per_sentence'] = sum(sents_clauses) / metrics['sentence_count']
    metrics['many_clauses_ratio'] = metrics['many_clauses_ratio'] / metrics['sentence_count']
  else:
    metrics['clauses_per_sentence'] = 0
    metrics['many_clauses_ratio'] = 0

  # count number of syllables per word
  cmu_words_count = 0
  cmu_syllables_count = 0
  data['numbers_of_syllables'] = [0 if is_word(token) else None for token in doc]
  for idx, word in enumerate(words):
    if word in dict_phonemes:
      cmu_words_count += 1
      syll_num = len([phoneme for phoneme in dict_phonemes[word] if phoneme[-1].isdigit()])
      cmu_syllables_count += syll_num
      data['numbers_of_syllables'][word2token_map[idx]] = syll_num
  if cmu_words_count:
    metrics['syllables_per_word'] = cmu_syllables_count / cmu_words_count
  else:
    metrics['syllables_per_word'] = 0

  # count number of characters in the whole text
  metrics['character_count'] = len(text)

  # count number of characters per word
  char_count = [len(word) for word in words]
  if metrics['word_count']:
    metrics['characters_per_word'] = sum(char_count) / metrics['word_count']
  else:
    metrics['characters_per_word'] = 0

  # count stopwords
  if metrics['word_count']:
    metrics['stopword_ratio'] = data['stopwords'].count(True) / metrics['word_count']
  else:
    metrics['stopword_ratio'] = 0

  # estimate test readability using Flesch-Kincaid Grade Level test
  if (metrics['word_count'] >= 100) and metrics['words_per_sentence'] and metrics['syllables_per_word']:
    metrics['readability'] = 0.39 * metrics['words_per_sentence'] + 11.8 * metrics['syllables_per_word'] - 15.59
  else:
    metrics['readability'] = 0

  # count number of different parts of speech
  noun_count = 0
  pronoun_count = 0
  pronoun_nonpossesive_count = 0
  verb_count = 0
  adjective_count = 0
  adverb_count = 0
  for tag in data['parts_of_speech']:
    if tag[:2] == 'NN':
      noun_count += 1
    elif tag[:2] in ['PR', 'WP', 'EX']:
      pronoun_count += 1
      if tag in ['PRP', 'WP', 'EX']:
        pronoun_nonpossesive_count += 1
    elif tag[:2] in ['VB', 'MD']:
      verb_count += 1
    elif tag[:2] == 'JJ':
      adjective_count += 1
    elif tag[:2] == 'RB':
      adverb_count += 1
  if metrics['word_count']:
    metrics['noun_ratio'] = noun_count / metrics['word_count']
    metrics['pronoun_ratio'] = pronoun_count / metrics['word_count']
    metrics['verb_ratio'] = verb_count / metrics['word_count']
    metrics['adjective_ratio'] = adjective_count / metrics['word_count']
    metrics['adverb_ratio'] = adverb_count / metrics['word_count']
    metrics['other_pos_ratio'] = 1 - metrics['noun_ratio'] - metrics['pronoun_ratio'] - metrics['verb_ratio'] \
                                   - metrics['adjective_ratio'] - metrics['adverb_ratio']
  else:
    metrics['noun_ratio'] = 0
    metrics['pronoun_ratio'] = 0
    metrics['verb_ratio'] = 0
    metrics['adjective_ratio'] = 0
    metrics['adverb_ratio'] = 0
    metrics['other_pos_ratio'] = 0

  # count number of modals
  modal_count = data['parts_of_speech'].count('MD')
  if metrics['word_count']:
    metrics['modal_ratio'] = modal_count / metrics['word_count']
  else:
    metrics['modal_ratio'] = 0

  # find and count nominalizations, weak verbs, entity substitutes, and filler words
  data['nominalizations'] = [False if is_word(token) else None for token in doc]
  data['weak_verbs'] = [False if is_word(token) else None for token in doc]
  data['entity_substitutions'] = [False if is_word(token) else None for token in doc]
  data['filler_words'] = [False if is_word(token) else None for token in doc]
  for idx_word, word in enumerate(words):
    idx = word2token_map[idx_word]
    data['nominalizations'][idx] = (data['numbers_of_characters'][idx] > 7) and (data['pos_high_level'][idx] != 'PROPN')\
                                    and (nominalization_re.search(word) is not None)
    data['weak_verbs'][idx] = (data['pos_high_level'][idx] == 'VERB') and (data['base_lemmas'][idx] in dict_weak_verbs)
    if data['weak_verbs'][idx] and data['auxiliary_verbs'][idx]:
      data['weak_verbs'][idx] = False
    data['entity_substitutions'][idx] = (word in dict_entity_substitutions) and (not data['values'][idx].isupper() or (word == 'i'))
    if word in ['this', 'that']:
      if (idx > 0) and (data['parts_of_speech'][idx-1][:2] in ['NN', 'PR']):
        data['entity_substitutions'][idx] = False
      if (idx < len(doc)) and ((data['parts_of_speech'][idx+1][:2] in ['NN', 'PR', 'WP', 'JJ', 'DT', 'WD', 'WP'])
                          or (doc[idx+1].lower_ in ['there', 'that', 'this', 'here'])):
        data['entity_substitutions'][idx] = False
    data['filler_words'][idx] = (word in dict_fillers)
  if (noun_count + pronoun_nonpossesive_count) > 0:
    metrics['nominalization_ratio'] = data['nominalizations'].count(True) / (noun_count + pronoun_nonpossesive_count)
    metrics['entity_substitution_ratio'] = data['entity_substitutions'].count(True) / (noun_count + pronoun_nonpossesive_count)
  else:
    metrics['nominalization_ratio'] = 0
    metrics['entity_substitution_ratio'] = 0
  if verb_count > 0:
    metrics['weak_verb_ratio'] = data['weak_verbs'].count(True) / verb_count
  else:
    metrics['weak_verb_ratio'] = 0
  if len(words) > 0:
    metrics['filler_ratio'] = data['filler_words'].count(True) / len(words)
  else:
    metrics['filler_ratio'] = 0

  # find and count negations
  data['negations'] = [False if is_word(token) else None for token in doc]
  for idx_word, word in enumerate(words):
    idx = word2token_map[idx_word]
    if word in ["not", "n't", "no", "neither", "nor", "nothing", "nobody", "nowhere", "never"]:
      data['negations'][idx] = True
    elif (word[:2] == 'un') and (word[2:] in dict_phonemes) and (data['base_lemmas'][idx] not in ['unit', 'under', 'union', 'until']):
      data['negations'][idx] = True
    elif (word[:3] == 'mis') and (word[3:] in dict_phonemes) and (data['base_lemmas'][idx] != 'miss'):
      data['negations'][idx] = True
  if metrics['sentence_count']:
    metrics['negation_ratio'] = data['negations'].count(True) / metrics['sentence_count']
  else:
    metrics['negation_ratio'] = 0

  # find and count noun clusters
  data['noun_clusters'] = [None] * len(doc)
  noun_cluster_count = 0
  noun_count_in_cluster = 0
  total_noun_count_in_cluster = 0
  noun_cluster_span = [None, None]
  for idx, token in enumerate(doc):
    if data['parts_of_speech'][idx][:2] == 'NN':
      if noun_cluster_span[0] is None:
        noun_cluster_span = [idx, idx+1]
        noun_count_in_cluster = 1
      else:
        noun_cluster_span[1] = idx+1
        noun_count_in_cluster += 1
    elif token.lower_ not in ["'s", "of"]:
      if noun_count_in_cluster >= 3:
        noun_cluster_count += 1
        data['noun_clusters'][noun_cluster_span[0]:noun_cluster_span[1]] = \
            [noun_cluster_count] * (noun_cluster_span[1] - noun_cluster_span[0])
        total_noun_count_in_cluster += noun_count_in_cluster
      noun_cluster_span = [None, None]
      noun_count_in_cluster = 0
  if noun_count > 0:
      metrics['noun_cluster_ratio'] = total_noun_count_in_cluster / noun_count
  else:
      metrics['noun_cluster_ratio'] = 0

  # find and count long noun phrases
  data['long_noun_phrases'] = [None] * len(doc)
  noun_phrase_count = 0
  long_noun_phrase_count = 0
  for noun_phrase in doc.noun_chunks:
    noun_phrase_count += 1
    phrase_len = sum([1 for token in noun_phrase if not \
                 (token.pos_ in ['PUNCT', 'DET', 'ADP', 'CCONJ', 'PART'])])
    if phrase_len >= 5:
      long_noun_phrase_count += 1
      data['long_noun_phrases'][noun_phrase.start:noun_phrase.end] = \
          [long_noun_phrase_count] * len(noun_phrase)
  if noun_phrase_count > 0:
    metrics['long_noun_phrase_ratio'] = long_noun_phrase_count / noun_phrase_count
  else:
    metrics['long_noun_phrase_ratio'] = 0

  # find and count passive voice cases
  data['passive_voice_cases'] = [None] * len(doc)
  passive_voice_count = 0
  for i in range(verb_group_count):
    verb_group_stack = [idx for idx in range(len(doc)) if data['verb_groups'][idx] == i+1]
    if data['parts_of_speech'][verb_group_stack[-1]] in ['VBN', 'VBD']:
      for j in verb_group_stack[:-1]:
        if doc[j].lower_ in ["am", "'m", "is", "'s", "are", "'re", "was", "were", "be", "been", "being"]:
          passive_voice_count += 1
          data['passive_voice_cases'][j] = passive_voice_count
          data['passive_voice_cases'][verb_group_stack[-1]] = passive_voice_count
          break
  if metrics['sentence_count']:
    metrics['passive_voice_ratio'] = passive_voice_count / metrics['sentence_count']
  else:
    metrics['passive_voice_ratio'] = 0

  # count rare words
  if len(words):
    metrics['rare_word_ratio'] = data['expected_word_frequencies'].count(0) / len(words)
  else:
    metrics['rare_word_ratio'] = 0

  # count word, bigram, and trigram frequencies
  word_freq = {}
  bigram_freq = {}
  trigram_freq = {}
  lemmas = [data['base_lemmas'][i] for i in word2token_map]
  for idx, word in enumerate(lemmas[:-2]):
    if word in word_freq:
      word_freq[word] += 1
    else:
      word_freq[word] = 1
    mask = word + '|' + lemmas[idx+1]
    if mask in bigram_freq:
      bigram_freq[mask] += 1
    else:
      bigram_freq[mask] = 1
    mask = word + '|' + lemmas[idx+1] + '|' + lemmas[idx+2]
    if mask in trigram_freq:
      trigram_freq[mask] += 1
    else:
      trigram_freq[mask] = 1
  if lemmas[-2] in word_freq:
    word_freq[lemmas[-2]] += 1
  else:
    word_freq[lemmas[-2]] = 1
  if lemmas[-1] in word_freq:
    word_freq[lemmas[-1]] += 1
  else:
    word_freq[lemmas[-1]] = 1
  mask = lemmas[-2] + '|' + lemmas[-1]
  if mask in bigram_freq:
    bigram_freq[mask] += 1
  else:
    bigram_freq[mask] = 1
  word_freq_list = []
  for word, freq in word_freq.iteritems():
    if (freq > 1) and (word not in dict_stop_words):
      word_freq_list.append([word, freq])
  word_freq_list.sort(reverse=True, key=lambda x: x[1])
  if word_freq_list:
    metrics['word_freq'] = word_freq_list
  else:
    metrics['word_freq'] = []
  bigram_freq_list = []
  for mask, freq in bigram_freq.iteritems():
    w1, w2 = mask.split('|')
    if (freq > 1) and (w1 not in dict_stop_words) and (w2 not in dict_stop_words):
      bigram_freq_list.append([[w1, w2], freq])
  bigram_freq_list.sort(reverse=True, key=lambda x: x[1])
  if bigram_freq_list:
    metrics['bigram_freq'] = bigram_freq_list
  else:
    metrics['bigram_freq'] = []
  trigram_freq_list = []
  for mask, freq in trigram_freq.iteritems():
    w1, w2, w3 = mask.split('|')
    if (freq > 1):
      trigram_freq_list.append([[w1, w2, w3], freq])
  trigram_freq_list.sort(reverse=True, key=lambda x: x[1])
  if trigram_freq_list:
    metrics['trigram_freq'] = trigram_freq_list
  else:
    metrics['trigram_freq'] = []

  return original_text, data, metrics
