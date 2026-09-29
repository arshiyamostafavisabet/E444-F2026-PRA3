from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

#cruicial -> wont work without it
if __name__ == '__main__':
    app.run(debug=True)