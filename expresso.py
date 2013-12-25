from flask import Flask, render_template, request, jsonify
import os
from peewee import *
from text_analysis import analyze_text

app = Flask(__name__)

app.config.update(**os.environ)

#from model import Text

db = MySQLDatabase(app.config['DATABASE'], user=app.config['USER'], passwd=app.config['PASSWORD'])


class Text(Model):
    text = TextField()
    word_count = IntegerField()
    sentence_count = IntegerField()
    vocabulary_size = IntegerField()
    declarative_ratio = FloatField()
    interrogative_ratio = FloatField()
    exclamative_ratio = FloatField()

    class Meta:
        database = db


db.connect()

Text.create_table(fail_silently=True)


@app.route('/')
def expresso():
    return render_template('expresso.html')


@app.route('/analyze-text', methods=['POST'])
def analyze():
    text = request.form.get('text', '', type=str)
    analyzed_text = analyze_text(text)
    Text.create(**analyzed_text)
    return jsonify(analyzed_text)


if __name__ == '__main__':
    app.run()
