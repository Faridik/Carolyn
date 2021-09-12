from collections import defaultdict
import os.path
import pathlib
from sys import path
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from googleapiclient.discovery import _MEDIA_SIZE_BIT_SHIFTS, build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models.student import Student
from models.group import Group
from models.assignment import Assignment
from models.group import StudentNotFound

STUDENT_NUMBERS = 0
STUDENT_NAMES = 1
GROUP_IDS = 2  # for StudentList and AssignmentList
STUDENT_SUBJECTS = 3
STUDENT_TELEGRAM_IDS = 4
AUTH_TOKEN = 5
STUDENT_SUBSCRIPTION = 6
ASSIGNMENT_NAMES = 1
ASSIGNMENT_GROUP = 2
ASSIGNMENT_SUBJECT = 3
ASSIGNMENT_WEIGHTS = 4
ASSIGNMENT_RANGES = 5
ASSIGNMENT_ALLOWS = 6
ASSIGNMENT_HOW_TO_DISPLAY = 7
ASSIGNMENT_NOTES_RANGES = 8
ASSIGNMENT_DEADLINE = 9

TOKEN_FILE = pathlib.Path() / ".secrets" / "token.json"
CLIENT_SECRET_FILE = pathlib.Path() / ".secrets" / "client_secret.json"
NON_CACHED_RANGES = ("StudentList",)


def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            print(*args)
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


class StudentAlreadyAuthed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class AnotherStudentAlreadyAuthed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class StudentAlreadySubbed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class StudentAlreadyUnsubbed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Manager:
    """Позволяет выполнять операции с Google таблицами."""

    def __init__(
        self,
        spreadsheet_id: str = "1GKfmLwDVGjcpXFQAUyxM4RMQ5Nx6HAZ5VWenz2z--d0",
        scopes: list = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive",
        ],
    ):

        self.spreadsheet_id = spreadsheet_id

        creds = None

        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRET_FILE), scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with TOKEN_FILE.open("w") as token:
                token.write(creds.to_json())

        service = build("sheets", "v4", credentials=creds)
        self.sheet = service.spreadsheets()

    def get_values(self, range_name: str = "StudentList") -> list:
        if range_name in NON_CACHED_RANGES:
            return self._get_values(range_name)
        else:
            return self._cached_get_values(range_name)

    @timed_lru_cache(minutes=25)
    def _cached_get_values(self, range_name):
        return self._get_values(range_name)

    def _get_values(self, range_name: str = "StudentList") -> list:
        """Получить значения с таблицы.

        Returns:
            list of rows [[val1, val2, ...], [], ...]
        """
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=range_name)
            .execute()
        )
        return result.get("values", [])

    def write_values(self, values: list, range_name: str):
        """Записать значения в таблицу."""

        body = {"values": values}
        result = (
            self.sheet.values()
            .update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )

    def get_group(self, group_id: str) -> Group:
        """Получить группу со студентами."""

        values = self.get_values()

        group = Group(group_id)

        f = lambda row: group_id == row[GROUP_IDS]
        for row in filter(f, values):
            group.add_student(
                Student(
                    int(row[STUDENT_NUMBERS]),
                    row[STUDENT_NAMES],
                    group_id,
                    row[STUDENT_TELEGRAM_IDS],
                )
            )

        return group

    def get_all_groups(self) -> list:
        """Получить список всех групп."""
        values = self.get_values()
        groups = defaultdict(lambda: Group("0"))
        for row in values:
            groups[row[GROUP_IDS]].group_id = row[GROUP_IDS]
            groups[row[GROUP_IDS]].add_student(
                Student(
                    number=int(row[STUDENT_NUMBERS]),
                    name=row[STUDENT_NAMES],
                    group_id=row[GROUP_IDS],
                    tg_id=row[STUDENT_TELEGRAM_IDS],
                    subjects=row[STUDENT_SUBJECTS].split(","),
                    is_subbed=bool(int(row[STUDENT_SUBSCRIPTION])),
                )
            )

        return groups

    def get_all_groups_only_sub_students(self) -> list:
        """Получить список всех групп."""
        values = self.get_values()
        groups = defaultdict(lambda: Group("0"))
        f = lambda row: row[STUDENT_SUBSCRIPTION] == "1"
        for row in filter(f, values):
            groups[row[GROUP_IDS]].group_id = row[GROUP_IDS]
            groups[row[GROUP_IDS]].add_student(
                Student(
                    number=int(row[STUDENT_NUMBERS]),
                    name=row[STUDENT_NAMES],
                    group_id=row[GROUP_IDS],
                    tg_id=row[STUDENT_TELEGRAM_IDS],
                    subjects=row[STUDENT_SUBJECTS].split(","),
                    is_subbed=bool(int(row[STUDENT_SUBSCRIPTION])),
                )
            )

        return groups

    def get_student_by_name(self, name: str) -> Student:
        """Получить студента по имени."""

        values = self.get_values("StudentList")

        f = lambda row: name in row[STUDENT_NAMES]
        try:
            row = next(filter(f, values))
            return Student(
                int(row[STUDENT_NUMBERS]),
                name,
                row[GROUP_IDS],
                row[STUDENT_TELEGRAM_IDS],
                row[STUDENT_SUBJECTS].split(","),
            )
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по имени")

    def get_student_by_tg_id(self, tg_id: int) -> Student:
        """Получить студента по telegram id."""

        values = self.get_values("StudentList")

        f = lambda row: tg_id == row[STUDENT_TELEGRAM_IDS]
        try:
            row = next(filter(f, values))
            return Student(
                int(row[STUDENT_NUMBERS]),
                row[STUDENT_NAMES],
                row[GROUP_IDS],
                tg_id,
                row[STUDENT_SUBJECTS].split(","),
            )
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по telegram id")

    def set_assignments_for_student(self, student: Student):
        """Добавить задания студенту."""

        values = self.get_values("AssignmentList")

        f = lambda row: student.group_id == row[GROUP_IDS]  # TODO add subject
        for row in filter(f, values):
            assignment_values = self.get_values(row[ASSIGNMENT_RANGES])
            toFloat = lambda x: float(x.replace(",", "."))
            assignment_value = list(map(toFloat, assignment_values[student.number - 1]))
            notes_range, n_row = row[ASSIGNMENT_NOTES_RANGES].split(",")
            note = self.get_values(notes_range)[student.number - 1][int(n_row)]
            note = "Замечаний по работе нет." if note == "-" else f"Замечания:\n{note}"
            student.add_assignment(
                Assignment(
                    name=row[ASSIGNMENT_NAMES],
                    points=assignment_value,
                    weight=toFloat(row[ASSIGNMENT_WEIGHTS]),
                    subject=row[ASSIGNMENT_SUBJECT],
                    allow_to_display=bool(int(row[ASSIGNMENT_ALLOWS])),
                    how_to_display=row[ASSIGNMENT_HOW_TO_DISPLAY],
                    notes=note,
                    deadline=row[ASSIGNMENT_DEADLINE],
                )
            )

    def auth_by_token(self, token: str, tg_id: str) -> Student:
        """Аутентификация пользователя через token."""

        values = self.get_values("StudentList")

        f = lambda row: token == row[AUTH_TOKEN]
        try:
            row = next(filter(f, values))
            if row[STUDENT_TELEGRAM_IDS] == tg_id:
                raise StudentAlreadyAuthed("Студент уже зарегистрировался")
            elif row[STUDENT_TELEGRAM_IDS]:
                raise AnotherStudentAlreadyAuthed(
                    "Другой студент зарегистрировался по token"
                )
            row[STUDENT_TELEGRAM_IDS] = tg_id
            self.write_values(values, "StudentList")
            return Student(
                int(row[STUDENT_NUMBERS]),
                row[STUDENT_NAMES],
                row[GROUP_IDS],
                tg_id,
                row[STUDENT_SUBJECTS].split(","),
            )
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по token")

    def sub_by_tg_id(self, tg_id: str) -> bool:
        """Подписка пользователя по tg_id"""

        values = self.get_values("StudentList")

        f = lambda row: tg_id == row[STUDENT_TELEGRAM_IDS]
        try:
            row = next(filter(f, values))
            if row[STUDENT_SUBSCRIPTION] == "1":
                raise StudentAlreadySubbed("Студент уже подписался")

            row[STUDENT_SUBSCRIPTION] = 1
            self.write_values(values, "StudentList")
            return True
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по tg_id")

    def unsub_by_tg_id(self, tg_id: str) -> bool:
        """Подписка пользователя по tg_id"""

        values = self.get_values("StudentList")

        f = lambda row: tg_id == row[STUDENT_TELEGRAM_IDS]
        try:
            row = next(filter(f, values))
            if row[STUDENT_SUBSCRIPTION] == "0":
                raise StudentAlreadyUnsubbed(
                    "Студент уже не подписан (или никогда не был)"
                )

            row[STUDENT_SUBSCRIPTION] = 0
            self.write_values(values, "StudentList")
            return True
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по tg_id")
