from .assignment import Assignment
import json


class Student:
    """Позволяет выполнять операции над студентами."""

    def __init__(self, number: int, name: str, group_id: int, tg_id: int = None):
        self.number: int = number
        self.name: str = name
        self.group_id: int = group_id
        self.tg_id: int = tg_id
        self.assignments = []

    def add_assignment(self, assignment: Assignment):
        self.assignments.append(assignment)

    @property
    def grade(self) -> float:
        """Получить среднюю оценку студента по текущему контролю."""
        return 2

    @property
    def score(self):
        """Количество баллов у студента."""
        return sum([a.total for a in self.assignments])

    def __str__(self):
        return json.dumps(
            {
                "number": self.number,
                "name": self.name,
                "group_id": self.group_id,
                "tg_id": self.tg_id,
            }
        )
