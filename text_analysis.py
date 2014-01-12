from __future__ import division
import os
import nltk
import re
from bs4 import BeautifulSoup
import operator
from numpy import std

# pre-load and pre-compile required variables and methods
html_div_br_div_re = re.compile('</div><div><br></div>')
html_newline_re = re.compile('(<br|</div|</p)')
quotation_re = re.compile(u'[\u00AB\u00BB\u201C\u201D\u201E\u201F\u2033\u2036\u301D\u301E]')
punct_error_re = re.compile('^(["\]\)\}]+)[ \n]')
ellipsis_re = re.compile('\.\.\.["\(\)\[\]\{\} ] [A-Z]')
newline_re = re.compile('\n["\(\[\{ ]*[A-Z]')
nominalization_re = re.compile('(?:ion|ions|ism|isms|ty|ties|ment|ments|ness|nesses|ance|ances|ence|ences)$')
stopset = set(nltk.corpus.stopwords.words('english'))
stemmer = nltk.PorterStemmer()
cmudict = nltk.corpus.cmudict.dict()
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/corpora/weak-verbs')) as f:
    dict_weak_verbs = f.read().splitlines()
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/corpora/entity-substitutions')) as f:
    dict_entity_substitutions = f.read().splitlines()
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/corpora/fillers')) as f:
    dict_fillers = f.read().splitlines()


def analyze_text(html, app):

    # create data and metrics dictionaries
    data = dict()
    metrics = dict()

    app.logger.debug('%s', html)

    ### parse text/html string

    # strip html tags
    html = html_div_br_div_re.sub(r'</div>\n', html)
    html = html_newline_re.sub(lambda m: '\n'+m.group(0), html)
    soup = BeautifulSoup(html)
    original_text = soup.get_text().rstrip('\n')
    app.logger.debug('%s', original_text)

    # standardize all quotation marks
    text = quotation_re.sub('"', original_text)

    # tokenize text into sentences
    sents_draft = nltk.sent_tokenize(text)
    for idx, sent in enumerate(sents_draft[:]):
        if idx > 0:
            punct_error = punct_error_re.findall(sent)
            if punct_error:
                sents_draft[idx-1] += punct_error[0]
                sents_draft[idx] = sents_draft[idx][len(punct_error[0])+1:]

    # separate sentences at ellipsis characters correctly
    sents_draft_2 = []
    for sent in sents_draft:
        idx = 0
        for ellipsis_case in ellipsis_re.finditer(sent):
            sents_draft_2.append(sent[idx:(ellipsis_case.start() + 3)])
            idx = ellipsis_case.start() + 3
        sents_draft_2.append(sent[idx:])
    app.logger.debug('%s', sents_draft_2)

    # separate sentences at newline characters correctly
    sents = []
    for sent in sents_draft_2:
        idx = 0
        for newline_case in newline_re.finditer(sent):
            sents.append(sent[idx:(newline_case.start() + 1)])
            idx = newline_case.start() + 1
        sents.append(sent[idx:])
    app.logger.debug('%s', sents)

    # tokenize sentences into words and punctuation marks
    sents_tokens = [nltk.word_tokenize(sent) for sent in sents]
    app.logger.debug('%s', sents_tokens)
    tokens = [token for sent in sents_tokens for token in sent]
    data['value'] = tokens
    data['sentence_number'] = [(idx+1) for idx, sent in enumerate(sents_tokens) for token in sent]

    # find words
    sents_words = [[token.lower() for token in sent if token[0].isalnum()] for sent in sents_tokens]
    app.logger.debug('%s', sents_words)
    words = []
    word2token_map = []
    for idx, token in enumerate(tokens):
        if token[0].isalnum():
            words.append(token.lower())
            word2token_map.append(idx)

    # find word stems
    stems = [stemmer.stem(word) for word in words]
    app.logger.debug('%s', stems)
    data['stem'] = [None] * len(tokens)
    for idx, stem in enumerate(stems):
        data['stem'][word2token_map[idx]] = stem

    # tag tokens as part-of-speech
    sents_tokens_tags = nltk.batch_pos_tag(sents_tokens)
    data['part_of_speech'] = [pos for sent in sents_tokens_tags for (token, pos) in sent]

    # fix symbol tags
    for idx, token in enumerate(tokens):
        if (not token[0].isalnum()) and (data['part_of_speech'][idx].isalnum()):
            data['part_of_speech'][idx] = 'SYM'

    ### compute metrics on parsed data

    # count number of sentences
    metrics['sentence_count'] = len(sents)

    # count number of words
    metrics['word_count'] = len(words)

    # count number of words per sentence and its standard deviation
    sents_length = [len(sent) for sent in sents_words]
    if len(sents_length):
        metrics['words_per_sentence'] = sum(sents_length) / len(sents_length)
    else:
        metrics['words_per_sentence'] = 0
    if len(sents_length) >= 10:
        metrics['std_of_words_per_sentence'] = std(sents_length)
    else:
        metrics['std_of_words_per_sentence'] = -1

    # find extra long sentences
    if len(sents_length):
        metrics['long_sentences_ratio'] = len([1 for sent_length in sents_length if sent_length >= 40]) / len(sents_length)
    else:
        metrics['long_sentences_ratio'] = 0

    # find vocabulary size
    metrics['vocabulary_size'] = len(set(stems))

    # count sentence types based on ending punctuation mark
    sents_end_punct = []
    for sent in sents_tokens:
        sents_end_punct.append('')
        for token in reversed(sent):
            if token in ['.', '...', '?', '!']:
                sents_end_punct[-1] = token
            elif token[0].isalnum():
                break
    data['sentence_end_punctuation'] = [sents_end_punct[idx] for idx, sent in enumerate(sents_tokens) for token in sent]
    if metrics['sentence_count']:
        metrics['declarative_ratio'] = (sents_end_punct.count('.') + sents_end_punct.count('...')) \
                                       / metrics['sentence_count']
        metrics['interrogative_ratio'] = sents_end_punct.count('?') / metrics['sentence_count']
        metrics['exclamative_ratio'] = sents_end_punct.count('!') / metrics['sentence_count']
    else:
        metrics['declarative_ratio'] = metrics['interrogative_ratio'] = metrics['exclamative_ratio'] = 0

    # count number of characters in the whole text
    metrics['character_count'] = len(text)

    # count number of stopwords
    metrics['stopword_ratio'] = 0
    data['stopword'] = [None] * len(tokens)
    for idx, word in enumerate(words):
        if word in stopset:
            metrics['stopword_ratio'] += 1
            data['stopword'][word2token_map[idx]] = True
        else:
            data['stopword'][word2token_map[idx]] = False
    if metrics['word_count']:
        metrics['stopword_ratio'] /= metrics['word_count']

    # count number of syllables per word
    cmu_words_count = 0
    cmu_syllables_count = 0
    data['number_of_syllables'] = [None] * len(tokens)
    for idx, word in enumerate(words):
        if word in cmudict:
            cmu_words_count += 1
            syll_num = len([phoneme for phoneme in cmudict[word][0] if phoneme[-1].isdigit()])
            cmu_syllables_count += syll_num
            data['number_of_syllables'][word2token_map[idx]] = syll_num
    if cmu_words_count:
        metrics['syllables_per_word'] = cmu_syllables_count / cmu_words_count
    else:
        metrics['syllables_per_word'] = 0

    # count number of characters per word
    char_count = [len(word) for word in words]
    if metrics['word_count']:
        metrics['characters_per_word'] = sum(char_count) / metrics['word_count']
    else:
        metrics['characters_per_word'] = 0
    data['number_of_characters'] = [len(token) if token[0].isalnum() else None for token in tokens]

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
    modal_count = 0
    for tag in data['part_of_speech']:
        if tag[:2] == 'NN':
            noun_count += 1
        elif tag[:2] in ['PR', 'WP', 'EX']:
            pronoun_count += 1
            if tag in ['PRP', 'WP', 'EX']:
                pronoun_nonpossesive_count += 1
        elif tag[:2] == 'VB':
            verb_count += 1
        elif tag[:2] == 'JJ':
            adjective_count += 1
        elif tag[:2] == 'RB':
            adverb_count += 1
        elif tag[:2] == 'MD':
            modal_count += 1
    if metrics['word_count']:
        metrics['noun_ratio'] = noun_count / metrics['word_count']
        metrics['pronoun_ratio'] = pronoun_count / metrics['word_count']
        metrics['verb_ratio'] = verb_count / metrics['word_count']
        metrics['adjective_ratio'] = adjective_count / metrics['word_count']
        metrics['adverb_ratio'] = adverb_count / metrics['word_count']
        metrics['modal_ratio'] = modal_count / metrics['word_count']
        metrics['other_pos_ratio'] = 1 - metrics['noun_ratio'] - metrics['pronoun_ratio'] - metrics['verb_ratio'] \
                                       - metrics['adjective_ratio'] - metrics['adverb_ratio'] - metrics['modal_ratio']
    else:
        metrics['noun_ratio'] = 0
        metrics['pronoun_ratio'] = 0
        metrics['verb_ratio'] = 0
        metrics['adjective_ratio'] = 0
        metrics['adverb_ratio'] = 0
        metrics['modal_ratio'] = 0
        metrics['other_pos_ratio'] = 0

    # find nominalizations, weak verbs, entity substitutes, and filler words
    data['nominalizations'] = [None] * len(tokens)
    data['weak_verbs'] = [None] * len(tokens)
    data['entity_substitutions'] = [None] * len(tokens)
    data['filler_words'] = [None] * len(tokens)
    for idx_word, word in enumerate(words):
        idx = word2token_map[idx_word]
        data['nominalizations'][idx] = (data['number_of_characters'][idx] > 7) and (data['part_of_speech'][idx] != 'NNP')\
                                        and (nominalization_re.search(word) is not None)
        data['weak_verbs'][idx] = (data['part_of_speech'][idx][:2] == 'VB') and (data['stem'][idx] in dict_weak_verbs)
        data['entity_substitutions'][idx] = (word in dict_entity_substitutions)
        if word in ['this', 'that']:
            if (idx > 0) and (data['part_of_speech'][idx-1][:2] in ['NN', 'PR']):
                data['entity_substitutions'][idx] = False
            if (idx < len(tokens)) and ((data['part_of_speech'][idx+1][:2] in ['NN', 'PR', 'WP', 'JJ', 'DT', 'WD', 'WP'])
                                        or (tokens[idx+1] in ['there', 'that', 'this', 'here'])):
                data['entity_substitutions'][idx] = False
        data['filler_words'][idx] = (word in dict_fillers)
    if (noun_count + pronoun_nonpossesive_count) > 0:
        metrics['nominalization_ratio'] = data['nominalizations'].count(True) / (noun_count + pronoun_nonpossesive_count)
        metrics['entity_substitution_ratio'] = data['entity_substitutions'].count(True) / (noun_count +
                                                                                           pronoun_nonpossesive_count)
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

    # count word, bigram, and trigram frequencies
    bcf = nltk.TrigramCollocationFinder.from_words(stems)
    word_freq = bcf.word_fd
    bigram_freq = bcf.bigram_fd
    trigram_freq = bcf.ngram_fd

    # sort and filter word frequencies
    sorted_word_freq = sorted(word_freq.iteritems(), key=operator.itemgetter(1))
    sorted_word_freq.reverse()
    sorted_word_freq = [word for word in sorted_word_freq if (word[1] > 1) and (word[0] not in stopset)]
    if sorted_word_freq:
        metrics['word_freq'] = sorted_word_freq
    else:
        metrics['word_freq'] = []

    # sort and filter bigram frequencies
    sorted_bigram_freq = sorted(bigram_freq.iteritems(), key=operator.itemgetter(1))
    sorted_bigram_freq.reverse()
    sorted_bigram_freq = [bigram for bigram in sorted_bigram_freq if
                          (bigram[1] > 1) and (bigram[0][0] not in stopset) and (bigram[0][1] not in stopset)]
    if sorted_bigram_freq:
        metrics['bigram_freq'] = sorted_bigram_freq
    else:
        metrics['bigram_freq'] = []

    # sort and filter trigram frequencies
    sorted_trigram_freq = sorted(trigram_freq.iteritems(), key=operator.itemgetter(1))
    sorted_trigram_freq.reverse()
    sorted_trigram_freq = [trigram for trigram in sorted_trigram_freq if trigram[1] > 1]
    if sorted_trigram_freq:
        metrics['trigram_freq'] = sorted_trigram_freq
    else:
        metrics['trigram_freq'] = []

    return original_text, data, metrics