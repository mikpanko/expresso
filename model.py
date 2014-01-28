from peewee import *

db_proxy = Proxy()


class Text(Model):
    timestamp = DateTimeField()
    analysis_time = FloatField()
    character_count = IntegerField()
    word_count = IntegerField()
    sentence_count = IntegerField()

    class Meta:
        database = db_proxy