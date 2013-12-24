from __future__ import division
import nltk


def analyze_text(text):

    # load json with data into a python dictionary
    data = {'text': text}

    # extract text tokens (words and punctuation)
    tokens = nltk.wordpunct_tokenize(data['text'])
    words = [word.lower() for word in tokens if word[0].isalnum()]

    # count word frequencies
    #word_freq_dist = FreqDist(words)

    # count number of sentence types
    declarative_count = tokens.count('.')
    interrogative_count = tokens.count('?')
    exclamative_count = tokens.count('!')

    # count number of words
    data['word_count'] = len(words)

    # find vocabulary size
    data['vocabulary_size'] = len(set(words))

    # count number of sentences and their types
    data['sentence_count'] = declarative_count + interrogative_count + exclamative_count
    if data['sentence_count']:
        data['declarative_ratio'] = declarative_count / data['sentence_count']
        data['interrogative_ratio'] = interrogative_count / data['sentence_count']
        data['exclamative_ratio'] = exclamative_count / data['sentence_count']
    else:
        data['declarative_ratio'] = 0
        data['interrogative_ratio'] = 0
        data['exclamative_ratio'] = 0

    return data
