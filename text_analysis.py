from __future__ import division
import nltk
import re
import operator

newline_re = re.compile('\n+')
ellipsis_re = re.compile('\.\.\.["\u201C\u201D ]+[A-Z]')
stopset = set(nltk.corpus.stopwords.words('english'))
stemmer = nltk.PorterStemmer()
cmudict = nltk.corpus.cmudict.dict()


def analyze_text(text, app):

    # create data and metrics dictionary
    data = dict()
    metrics = dict()

    # tokenize text into sentences
    sents_draft = nltk.sent_tokenize(text)
    app.logger.debug('%s', sents_draft)

    # separate sentences at new line characters correctly
    sents_draft_2 = []
    for sent in sents_draft:
        idx = 0
        for newline_case in newline_re.finditer(sent):
            sents_draft_2.append(sent[idx:newline_case.start()])
            idx = newline_case.end()
        sents_draft_2.append(sent[idx:])

    # separate sentences at ellipsis characters correctly
    sents = []
    for sent in sents_draft_2:
        idx = 0
        for ellipsis_case in ellipsis_re.finditer(sent):
            sents.append(sent[idx:(ellipsis_case.start() + 3)])
            idx = ellipsis_case.start() + 3
        sents.append(sent[idx:])

    # move closing quotation marks to the sentence they belong
    for idx in range(len(sents[:-1])):
        if (sents[idx].count('"') + sents[idx].count('\u201C') + sents[idx].count('\u201D')) % 2 == 1:
            if sents[idx + 1][0] in '"\u201C\u201D':
                sents[idx] += sents[idx + 1][0]
                sents[idx + 1] = sents[idx + 1][1:]

    # delete sentences consisting only of punctuation marks
    sents = [sent for sent in sents if (sent not in '!?"\u201C\u201D')]
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

    # count number of words
    metrics['word_count'] = len(words)

    # count number of sentences
    if metrics['word_count']:
        metrics['sentence_count'] = len(sents)
    else:
        metrics['sentence_count'] = 0

    # count words per sentence
    sents_length = [len(sent) for sent in sents_words]
    app.logger.debug('%s', sents_length)
    if len(sents_length):
        metrics['words_per_sentence'] = sum(sents_length) / len(sents_length)
    else:
        metrics['words_per_sentence'] = 0

    # count sentence types
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

    # count number of characters in text
    metrics['character_count'] = len(text)

    # find vocabulary size
    metrics['vocabulary_size'] = len(set(stems))

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
    if metrics['words_per_sentence'] and metrics['syllables_per_word']:
        metrics['readability'] = 0.39 * metrics['words_per_sentence'] + 11.8 * metrics['syllables_per_word'] - 15.59
    else:
        metrics['readability'] = 0

    # count number of different parts of speech
    noun_count = 0
    pronoun_count = 0
    verb_count = 0
    adjective_count = 0
    adverb_count = 0
    determiner_count = 0
    for sent in sents_tokens_tags:
        for tag in sent:
            if tag[1][:2] == 'NN':
                noun_count += 1
            elif tag[1][:2] == 'PR':
                pronoun_count += 1
            elif tag[1][:2] == 'VB':
                verb_count += 1
            elif tag[1][:2] == 'JJ':
                adjective_count += 1
            elif tag[1][:2] == 'RB':
                adverb_count += 1
            elif tag[1][:2] in ['DT', 'WD', 'WP', 'WR']:
                determiner_count += 1
    if metrics['word_count']:
        metrics['noun_ratio'] = noun_count / metrics['word_count']
        metrics['pronoun_ratio'] = pronoun_count / metrics['word_count']
        metrics['verb_ratio'] = verb_count / metrics['word_count']
        metrics['adjective_ratio'] = adjective_count / metrics['word_count']
        metrics['adverb_ratio'] = adverb_count / metrics['word_count']
        metrics['determiner_ratio'] = determiner_count / metrics['word_count']
        metrics['other_pos_ratio'] = 1 - metrics['noun_ratio'] - metrics['pronoun_ratio'] - metrics['verb_ratio'] \
                                       - metrics['adjective_ratio'] - metrics['adverb_ratio'] \
                                       - metrics['determiner_ratio']
    else:
        metrics['noun_ratio'] = 0
        metrics['pronoun_ratio'] = 0
        metrics['verb_ratio'] = 0
        metrics['adjective_ratio'] = 0
        metrics['adverb_ratio'] = 0
        metrics['determiner_ratio'] = 0
        metrics['other_pos_ratio'] = 0

    # count word, bigram, and trigram frequencies
    bcf = nltk.TrigramCollocationFinder.from_words(stems)
    word_freq = bcf.word_fd
    bigram_freq = bcf.bigram_fd
    trigram_freq = bcf.ngram_fd

    # prepare string displaying word frequencies
    sorted_word_freq = sorted(word_freq.iteritems(), key=operator.itemgetter(1))
    sorted_word_freq.reverse()
    sorted_word_freq = [word for word in sorted_word_freq if (word[1] > 1) and (word[0] not in stopset)]
    sorted_word_freq = sorted_word_freq[:min(len(sorted_word_freq), 10)]
    sorted_word_freq = reduce(lambda x, y: x + y[0] + ' (' + str(y[1]) + ')<br>', sorted_word_freq, '')
    metrics['word_freq'] = sorted_word_freq[:-4]

    # prepare string displaying bigram frequencies
    sorted_bigram_freq = sorted(bigram_freq.iteritems(), key=operator.itemgetter(1))
    sorted_bigram_freq.reverse()
    sorted_bigram_freq = [bigram for bigram in sorted_bigram_freq if
                          (bigram[1] > 1) and (bigram[0][0] not in stopset) and (bigram[0][1] not in stopset)]
    sorted_bigram_freq = sorted_bigram_freq[:min(len(sorted_bigram_freq), 10)]
    sorted_bigram_freq = reduce(lambda x, y: x + y[0][0] + ' ' + y[0][1] + ' (' + str(y[1]) + ')<br>',
                                sorted_bigram_freq, '')
    metrics['bigram_freq'] = sorted_bigram_freq[:-4]

    # prepare string displaying trigram frequencies
    sorted_trigram_freq = sorted(trigram_freq.iteritems(), key=operator.itemgetter(1))
    sorted_trigram_freq.reverse()
    sorted_trigram_freq = [trigram for trigram in sorted_trigram_freq if trigram[1] > 1]
    sorted_trigram_freq = sorted_trigram_freq[:min(len(trigram_freq), 10)]
    sorted_trigram_freq = reduce(lambda x, y: x + y[0][0] + ' ' + y[0][1] + ' ' + y[0][2] + ' (' + str(y[1]) + ')<br>',
                                 sorted_trigram_freq, '')
    metrics['trigram_freq'] = sorted_trigram_freq[:-4]

    app.logger.debug('%s', data)

    return data, metrics