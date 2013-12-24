from flask import Flask, render_template, request, jsonify
import jinja2
from text_analysis import analyze_text

app = Flask(__name__)


@app.route('/')
def expresso():
    return render_template('expresso.html')


@app.route('/analyze-text', methods=['POST'])
def analyze():
    text = request.form.get('text', '', type=str)
    analyzed_text = analyze_text(text)
    return jsonify(analyzed_text)


if __name__ == '__main__':
    app.run(debug=True)
