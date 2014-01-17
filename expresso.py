from flask import Flask, render_template, request, jsonify, g
import os
from peewee import *
from text_analysis import analyze_text
from model import db_proxy, Text
from datetime import datetime

app = Flask(__name__)
app.config.update(**os.environ)


@app.route('/')
def expresso_route():
    return render_template('expresso.html')


@app.route('/how-to-use')
def how_to_use_route():
    return render_template('how-to-use.html')


@app.route('/metrics')
def metrics_route():
    return render_template('metrics.html')


@app.route('/about')
def about_route():
    return render_template('about.html')


@app.route('/analyze-text', methods=['POST'])
def analyze():
    html = request.form.get('html', '')
    text, tokens, metrics = analyze_text(html, app)
    Text.create(text=text, timestamp=datetime.now().replace(microsecond=0), **metrics)
    return jsonify({'text': text, 'tokens': tokens, 'metrics': metrics})


@app.before_request
def before_request():
    g.db = MySQLDatabase(app.config['DATABASE_NAME'],
                         host=app.config['DATABASE_HOST'],
                         port=int(app.config['DATABASE_PORT']),
                         user=app.config['DATABASE_USER'],
                         passwd=app.config['DATABASE_PASSWORD'])
    db_proxy.initialize(g.db)
    g.db.connect()
    Text.create_table(fail_silently=True)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run()
