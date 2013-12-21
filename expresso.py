from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def expresso():
    return render_template('expresso.html')


if __name__ == '__main__':
    app.run()
