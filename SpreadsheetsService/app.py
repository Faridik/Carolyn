import flask
import time
import models
from manager import *

app = flask.Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!\n"


@app.route("/auth")
def auth():
    # TODO: return json text instead of text/html.
    token = flask.request.args.get("token")
    tg_id = flask.request.args.get("tg_id")
    manager = Manager()
    student = manager.get_student_by_name("Дзюба")
    return str(student)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
