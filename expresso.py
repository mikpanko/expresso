from flask import Flask, render_template, request, jsonify
import os
from peewee import *
from text_analysis import analyze_text
from model import db_proxy, Text

app = Flask(__name__)
app.config.update(**os.environ)

db = MySQLDatabase(app.config['DATABASE_NAME'], host=app.config['DATABASE_HOST'], port=int(app.config['DATABASE_PORT']), user=app.config['DATABASE_USER'], passwd=app.config['DATABASE_PASSWORD'])
db_proxy.initialize(db)
db.connect()

Text.create_table(fail_silently=True)


@app.route('/')
def expresso_route():
    return render_template('expresso.html')

@app.route('/about')
def about_route():
    return render_template('about.html')

@app.route('/analyze-text', methods=['POST'])
def analyze():
    text = request.form.get('text', '', type=str)
    analyzed_text = analyze_text(text)
    Text.create(**analyzed_text)
    return jsonify(analyzed_text)


if __name__ == '__main__':
    app.run()
