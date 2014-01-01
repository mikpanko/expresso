from peewee import *

db_proxy = Proxy()


class Text(Model):
    text = TextField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    sentence_length = FloatField()
    vocabulary_size = IntegerField()
    declarative_ratio = FloatField()
    interrogative_ratio = FloatField()
    exclamative_ratio = FloatField()
    stopword_ratio = FloatField()
    word_freq = TextField()
    bigram_freq = TextField()
    trigram_freq = TextField()

    class Meta:
        database = db_proxy