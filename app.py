from flask import Flask
from utils import *
app = Flask(__name__)

@app.route("/data")
def hello():
    img_to_environment = preprocess("react-todo-app/src/components/ui/images/", 100)
    return {
        'message': img_to_environment
    }

if __name__ == "__main__":
    app.run(debug=True)