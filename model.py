from peewee import *

db_proxy = Proxy()


class Text(Model):
    text = TextField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    vocabulary_size = IntegerField()
    declarative_ratio = FloatField()
    interrogative_ratio = FloatField()
    exclamative_ratio = FloatField()

    class Meta:
        database = db_proxy