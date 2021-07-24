from flask import Flask
import time

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!\n"


@app.route("/auth")
def auth():
    is_auth = int(time.time())
    return f"{is_auth % 2 == 0}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
