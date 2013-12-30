from __future__ import division
import nltk


def analyze_text(text, app):

    # load json with data into a python dictionary
    data = {'text': text}

    # extract text tokens (words and punctuation)
    tokens = nltk.wordpunct_tokenize(data['text'])
    sents = nltk.sent_tokenize(data['text'])
    sents = [sent for sent in sents if (sent not in ['!', '?'])]
    words = [word.lower() for word in tokens if word[0].isalnum()]

    # count word frequencies
    #word_freq_dist = FreqDist(words)

    # count number of sentences and their types
    declarative_count = 0
    interrogative_count = 0
    exclamative_count = 0
    for sent in sents:
        if sent[-1] == '.':
            declarative_count += 1
        elif sent[-1] == '?':
            interrogative_count += 1
        elif sent[-1] == '!':
            exclamative_count += 1
    data['sentence_count'] = len(sents)
    if data['sentence_count']:
        data['declarative_ratio'] = declarative_count / data['sentence_count']
        data['interrogative_ratio'] = interrogative_count / data['sentence_count']
        data['exclamative_ratio'] = exclamative_count / data['sentence_count']
    else:
        data['declarative_ratio'] = 0
        data['interrogative_ratio'] = 0
        data['exclamative_ratio'] = 0

    # count number of words
    data['word_count'] = len(words)

    # find vocabulary size
    data['vocabulary_size'] = len(set(words))

    return data
