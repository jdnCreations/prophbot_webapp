from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/play-sound')
def playsound():


if __name__ == '__main__':
    app.run(debug=True)
