from functools import wraps
from manager import *
import flask
import logging
import models
import time

UNEXPECTED_ERROR_DICT = dict(
                error=True,
                desc='UnexpectedError'
            )
STUDENT_NOT_FOUND_DICT = dict(
                error=True,
                desc='StudentNotFound'
            )
STUDENT_ALREADY_AUTHED_DICT = dict(
                error = True,
                desc='StudentAlreadyAuthed'
            )
ANOTHER_STUDENT_ALREADY_AUTHED_DICT = dict(
                error = True,
                desc='AnotherStudentAlreadyAuthed'
            )

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

app = flask.Flask(__name__)
app.db = None
try:
    app.db = Manager()
except Exception as e:
    app.db_error = e.args
    LOG.exception("Cannot init manager")


def availability(func):
    """Декоратор, который проверяет доступность менеджера по работе с Google
    Spreadsheets.

    Если инициализация менеджера обвалилась, то сервер выдает ошибку 500 и ее
    содержимое в JSON."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.db is None:
            return flask.jsonify(dict(error=True, message=app.db_error)), 500
        result = func(*args, **kwargs)
        return result

    return wrapper


@app.route("/")
def hello_world():
    return "Hello world!\n"


@app.route("/auth")
@availability
def auth():
    token = flask.request.args.get("token")
    tg_id = flask.request.args.get("tg_id")
    try:
        student = app.db.auth_by_token(token, tg_id)           
        return flask.jsonify(dict(
            student=student,
            error=False
        ))
    except StudentAlreadyAuthed:
        return flask.jsonify(STUDENT_ALREADY_AUTHED_DICT)
    except AnotherStudentAlreadyAuthed:
        return flask.jsonify(ANOTHER_STUDENT_ALREADY_AUTHED_DICT)
    except StudentNotFound: 
        return flask.jsonify(STUDENT_NOT_FOUND_DICT)
    except:
        return flask.jsonify(UNEXPECTED_ERROR_DICT)


@app.route("/grades")
@availability
def grades():
    """Возвращает оценки по id пользователя из телеграма."""
    tg_id = flask.request.args.get("tg_id")

    try:
        student = app.db.get_student_by_tg_id(tg_id)
        app.db.set_assignments_for_student(student)
        return flask.jsonify(
        dict(
            error=False,
            score=student.score,
            grade=student.grade,
            assignments=student.assignments,
        )
    )
    except StudentNotFound:
        return flask.jsonify(STUDENT_NOT_FOUND_DICT)
    except:
        return flask.jsonify(UNEXPECTED_ERROR_DICT)

    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
