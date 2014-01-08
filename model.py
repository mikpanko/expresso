from peewee import *

db_proxy = Proxy()


class Text(Model):
    text = TextField()
    timestamp = DateTimeField()
    character_count = IntegerField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    words_per_sentence = FloatField()
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
    word_freq = TextField()
    bigram_freq = TextField()
    trigram_freq = TextField()

    class Meta:
        database = db_proxy