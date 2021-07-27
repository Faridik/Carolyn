from .assignment import Assignment


class Student:
    """Позволяет выполнять операции над студентами."""

    def __init__(self, number: int, name: str):
        self.number: int = number
        self.name: str = name
        self.tg_id = None
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
