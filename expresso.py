from flask import Flask, render_template, request, jsonify, g
import os
from text_analysis import analyze_text

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


@app.route('/tutorial')
def tutorial_route():
    return render_template('tutorial.html')


@app.route('/about')
def about_route():
    return render_template('about.html')


@app.route('/analyze-text', methods=['POST'])
def analyze():
    html = request.form.get('html', '')
    text, tokens, metrics = analyze_text(html)
    return jsonify({'text': text, 'tokens': tokens, 'metrics': metrics})


if __name__ == '__main__':
    app.run()
