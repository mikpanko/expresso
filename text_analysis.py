from __future__ import division
import nltk
import re
import operator


def analyze_text(text, app):

    # load json with data into a python dictionary
    data = {'text': text}

    # tokenize text into sentences
    sents_draft = nltk.sent_tokenize(data['text'])
    app.logger.debug('%s', sents_draft)

    # separate sentences at new line characters correctly
    sents_draft_2 = []
    newline_re = re.compile('\n+')
    for sent in sents_draft:
        idx = 0
        for newline_case in newline_re.finditer(sent):
            sents_draft_2.append(sent[idx:newline_case.start()])
            idx = newline_case.end()
        sents_draft_2.append(sent[idx:])

    # separate sentences at ellipsis characters correctly
    sents = []
    ellipsis_re = re.compile('\.\.\.["\u201C\u201D ]+[A-Z]')
    for sent in sents_draft_2:
        idx = 0
        for ellipsis_case in ellipsis_re.finditer(sent):
            sents.append(sent[idx:(ellipsis_case.start()+3)])
            idx = ellipsis_case.start()+3
        sents.append(sent[idx:])

    # move closing quotation marks to the sentence they belong
    for idx in range(len(sents[:-1])):
        if (sents[idx].count('"') + sents[idx].count('\u201C') + sents[idx].count('\u201D')) % 2 == 1:
            if sents[idx+1][0] in '"\u201C\u201D':
                sents[idx] += sents[idx+1][0]
                sents[idx+1] = sents[idx+1][1:]

    # delete sentences consisting only of punctuation marks
    sents = [sent for sent in sents if (sent not in '!?"\u201C\u201D')]
    app.logger.debug('%s', sents)

    # tokenize sentences into words and punctuation marks
    sents_tokens = [nltk.word_tokenize(sent) for sent in sents]
    app.logger.debug('%s', sents_tokens)

    # find words
    sents_words = [[token.lower() for token in sent if token[0].isalnum()] for sent in sents_tokens]
    app.logger.debug('%s', sents_words)
    words = [word for sent in sents_words for word in sent]

    # find word stems
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
        for token in reversed(sent):
            if token in ['.', '...', '?', '!']:
                sents_end_punct[-1] = token
            elif token[0].isalnum():
                break
    if data['sentence_count']:
        data['declarative_ratio'] = (sents_end_punct.count('.') + sents_end_punct.count('...')) / data['sentence_count']
        data['interrogative_ratio'] = sents_end_punct.count('?') / data['sentence_count']
        data['exclamative_ratio'] = sents_end_punct.count('!') / data['sentence_count']
    else:
        data['declarative_ratio'] = data['interrogative_ratio'] = data['exclamative_ratio'] = 0

    # count number of words
    data['word_count'] = len(words)

    # find vocabulary size
    data['vocabulary_size'] = len(set(stems))

    # count number of stopwords
    stopset = set(nltk.corpus.stopwords.words('english'))
    data['stopword_ratio'] = reduce(lambda x, y: x + (y in stopset), words, 0) / data['word_count']

    # count word, bigram, and trigram frequencies
    bcf = nltk.TrigramCollocationFinder.from_words(stems)
    #bcf.apply_word_filter(lambda w: w in stopset)
    word_freq = bcf.word_fd
    bigram_freq = bcf.bigram_fd
    trigram_freq = bcf.ngram_fd
    n = 10
    sorted_word_freq = sorted(word_freq.iteritems(), key=operator.itemgetter(1))
    sorted_word_freq.reverse()
    sorted_word_freq = sorted_word_freq[:min(len(word_freq), n)]
    data['word_freq'] = str(sorted_word_freq)
    bigram_freq_2 = {}
    for key, val in bigram_freq.iteritems():
        bigram_freq_2[' '.join(key)] = val
    sorted_bigram_freq = sorted(bigram_freq_2.iteritems(), key=operator.itemgetter(1))
    sorted_bigram_freq.reverse()
    sorted_bigram_freq = sorted_bigram_freq[:min(len(bigram_freq), n)]
    data['bigram_freq'] = str(sorted_bigram_freq)
    trigram_freq_2 = {}
    for key, val in trigram_freq.iteritems():
        trigram_freq_2[' '.join(key)] = val
    sorted_trigram_freq = sorted(trigram_freq_2.iteritems(), key=operator.itemgetter(1))
    sorted_trigram_freq.reverse()
    sorted_trigram_freq = sorted_trigram_freq[:min(len(trigram_freq), n)]
    data['trigram_freq'] = str(sorted_trigram_freq)

    return data