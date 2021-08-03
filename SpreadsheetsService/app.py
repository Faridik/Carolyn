from functools import wraps
from manager import *
import flask
import logging
import models
import time

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
    student = app.db.get_student_by_name("Дзюба")
    return flask.jsonify(student)


@app.route("/grades")
@availability
def grades():
    """Возвращает оценки по id пользователя из телеграма."""
    tg_id = flask.request.args.get("tg_id")
    student = models.Student(1, "Фарид Михайлов", 5374)
    student.add_assignment(models.Assignment("ИДЗ 1", [1, 1, 0, 0, 1]))
    student.add_assignment(models.Assignment("КР 1", [0.4, 0.8, 1, 0.5, 1], 5))
    student.add_assignment(models.Assignment("ИДЗ 2", [1, 1, 1, 0, 1]))

    return flask.jsonify(
        dict(
            score=student.score,
            grade=student.grade,
            assignments=student.assignments,
        )
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
