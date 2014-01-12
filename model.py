from peewee import *

db_proxy = Proxy()


class Text(Model):
    text = TextField()
    timestamp = DateTimeField()
    character_count = IntegerField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    words_per_sentence = FloatField()
    std_of_words_per_sentence = FloatField()
    long_sentences_ratio = FloatField()
    short_sentences_ratio = FloatField()
    vocabulary_size = IntegerField()
    declarative_ratio = FloatField()
    interrogative_ratio = FloatField()
    exclamative_ratio = FloatField()
    stopword_ratio = FloatField()
    syllables_per_word = FloatField()
    characters_per_word = FloatField()
    readability = FloatField()
    noun_ratio = FloatField()
    pronoun_ratio = FloatField()
    verb_ratio = FloatField()
    adjective_ratio = FloatField()
    adverb_ratio = FloatField()
    modal_ratio = FloatField()
    other_pos_ratio = FloatField()
    nominalization_ratio = FloatField()
    weak_verb_ratio = FloatField()
    entity_substitution_ratio = FloatField()
    filler_ratio = FloatField()
    negation_ratio = FloatField()
    word_freq = TextField()
    bigram_freq = TextField()
    trigram_freq = TextField()

    class Meta:
        database = db_proxy