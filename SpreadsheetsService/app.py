from functools import wraps

from werkzeug.exceptions import *
from manager import *
import flask
import logging
import uuid

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
SUPER_USER = (420, 228)

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
            raise Exception("cannot init manager")
        result = func(*args, **kwargs)
        return result

    return wrapper


def superuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        god_mode = flask.request.args.get("god_mode", False)
        if god_mode.lower() != "true":
            tg_id = flask.request.args.get("tg_id", -1)
            student: Student = app.db.get_student_by_tg_id(tg_id)
            if student.number not in SUPER_USER:
                raise Forbidden(f"Доступ запрещен для студента {student.name}")
        result = func(*args, **kwargs)
        return result

    return wrapper


@app.route("/")
def hello_world():
    return "Hello world!\n"


@app.route("/auth")
@availability
def auth():
    token = flask.request.args.get("token", None)
    tg_id = flask.request.args.get("tg_id", None)
    if token is None or tg_id is None:
        raise BadRequest("Не предоставлены token и tg_id!")
    student = app.db.auth_by_token(token, tg_id)
    return flask.jsonify(dict(student=student))


@app.route("/grades")
@availability
def grades():
    """Возвращает оценки по id пользователя из телеграма."""
    tg_id = flask.request.args.get("tg_id")
    student = app.db.get_student_by_tg_id(tg_id)
    app.db.set_assignments_for_student(student)
    return flask.jsonify(
        dict(
            subjects=student.subjects,
            assignments=student.assignments,
        )
    )


@app.route("/grades/fingerprint")
@availability
def fingerprint():
    """Возвращает оценки в виде хеш-суммы."""
    tg_id = flask.request.args.get("tg_id")
    student = app.db.get_student_by_tg_id(tg_id)
    app.db.set_assignments_for_student(student)
    return flask.jsonify(
        dict(
            fingerprint=uuid.uuid3(uuid.NAMESPACE_DNS, "%s" % student.assignments),
        )
    )


@app.route("/students")
@availability
@superuser
def broadcast(*args, **kwargs):
    """Выполняет рассылку студентам."""
    sub_only = flask.request.args.get("sub_only", False)
    if sub_only.lower() == "true":
        return flask.jsonify(app.db.get_all_groups_only_sub_students())
    else:
        return flask.jsonify(app.db.get_all_groups())


@app.route("/sub")
@availability
def sub():
    tg_id = flask.request.args.get("tg_id", None)
    is_subbed = app.db.sub_by_tg_id(tg_id)
    return flask.jsonify(dict(is_subbed=is_subbed))


@app.route("/unsub")
@availability
def unsub():
    tg_id = flask.request.args.get("tg_id", None)
    is_unsubbed = app.db.unsub_by_tg_id(tg_id)
    return flask.jsonify(dict(is_unsubbed=is_unsubbed))


@app.errorhandler(StudentAlreadyAuthed)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.message}), 400


@app.errorhandler(AnotherStudentAlreadyAuthed)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.message}), 403


@app.errorhandler(StudentNotFound)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.message}), 404


@app.errorhandler(StudentAlreadySubbed)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.message}), 400


@app.errorhandler(StudentAlreadyUnsubbed)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.message}), 400


@app.errorhandler(BadRequest)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": err.description}), 400


# Любая другая ошибка вылетит вот здесь
@app.errorhandler(Exception)
def show_error(err):
    return flask.jsonify({"error": type(err).__name__, "message": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
