from peewee import *

db = MySQLDatabase('people.db', user='root', passwd='move1on')


class Person(Model):
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db  # this model uses the people database


class Pet(Model):
    owner = ForeignKeyField(Person, related_name='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db  # this model uses the people database