from flask import Flask, render_template, request, jsonify
import os
from peewee import *
from text_analysis import analyze_text
from model import db_proxy, Text

app = Flask(__name__)

print app.config
print os.environ
app.config.update(**os.environ)
print app.config

db = MySQLDatabase(app.config['DATABASE'], host=app.config['HOST'], port=int(app.config['PORT']), user=app.config['USER'], passwd=app.config['PASSWORD'])
#db = MySQLDatabase('heroku_a05e28ca77685c2', host='us-cdbr-east-04.cleardb.com', port=int('3306'), user='b6924537e41c0f', passwd='09f66988')
db_proxy.initialize(db)
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
