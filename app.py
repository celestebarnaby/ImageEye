from flask import Flask
app = Flask(__name__)

@app.route("/data")
def hello():
    return {
        'message': 'hello world!'
    }

if __name__ == "__main__":
    app.run(debug=True)