from __future__ import division
import nltk
import re
import itertools


def analyze_text(text, app):

    # load json with data into a python dictionary
    data = {'text': text}

    # extract text tokens: sentences, words, stems and punctuation
    sents_draft = nltk.sent_tokenize(data['text'])
    app.logger.debug('%s', sents_draft)
    sents = []
    ellipsis_re = re.compile('\.\.\.["\u201C\u201D ]{1,}[A-Z]')
    for sent in sents_draft:
        idx = 0
        for ellipsis_case in ellipsis_re.finditer(sent):
            sents.append(sent[idx:(ellipsis_case.start()+3)])
            idx = ellipsis_case.start()+3
        sents.append(sent[idx:])
    for idx in range(len(sents[:-1])):
        if (sents[idx].count('"') + sents[idx].count('\u201C') + sents[idx].count('\u201D')) % 2 == 1:
            if sents[idx+1][0] in '"\u201C\u201D':
                sents[idx] += sents[idx+1][0]
                sents[idx+1] = sents[idx+1][1:]
    sents = [sent for sent in sents if (sent not in '!?"\u201C\u201D')]
    app.logger.debug('%s', sents)
    sents_tokens = [nltk.word_tokenize(sent) for sent in sents]
    app.logger.debug('%s', sents_tokens)
    sents_words = []
    for sent in sents_tokens:
        sents_words.append([token.lower() for token in sent if token[0].isalnum()])
    app.logger.debug('%s', sents_words)
    words = list(itertools.chain.from_iterable(sents_words))
    stemmer = nltk.PorterStemmer()
    stems = [stemmer.stem(word) for word in words]
    app.logger.debug('%s', stems)

    # count number of sentences
    data['sentence_count'] = len(sents)

    # count sentence lengths
    sents_length = [len(sent) for sent in sents_words]
    app.logger.debug('%s', sents_length)
    if len(sents_length):
        data['sentence_length'] = sum(sents_length) / len(sents_length)
    else:
        data['sentence_length'] = 0

    # count sentence types
    sents_end_punct = []
    for sent in sents_tokens:
        sents_end_punct.append('')
        for token in sent[::-1]:
            if token in ['.', '...', '?', '!']:
                sents_end_punct[-1] = token
            elif token[0].isalnum():
                break
    if data['sentence_count']:
        data['declarative_ratio'] = (sents_end_punct.count('.') + sents_end_punct.count('...')) / data['sentence_count']
        data['interrogative_ratio'] = sents_end_punct.count('?') / data['sentence_count']
        data['exclamative_ratio'] = sents_end_punct.count('!') / data['sentence_count']
    else:
        data['declarative_ratio'] = 0
        data['interrogative_ratio'] = 0
        data['exclamative_ratio'] = 0

    # count number of words
    data['word_count'] = len(words)

    # count word frequencies
    #word_freq_dist = nltk.FreqDist(stems)

    # find vocabulary size
    data['vocabulary_size'] = len(set(stems))

    return data