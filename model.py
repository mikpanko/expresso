from peewee import *
import os

db = MySQLDatabase(os.environ['DATABASE'], user=os.environ['USER'], passwd=os.environ['PASSWORD'])


class Text(db.Model):
    text = TextField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    vocabulary_size = IntegerField()
    declarative_ratio = FloatField()
    interrogative_ratio = FloatField()
    exclamative_ratio = FloatField()


db.connect()

Text.create_table(fail_silently=True)
