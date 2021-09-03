from .assignment import Assignment


class Student(dict):
    """Позволяет выполнять операции над студентами."""

    def __init__(self, number: int, name: str, group_id: str, 
                    tg_id: int = None, subjects: list = None,
                    is_subbed: bool = False):
        self.number: int = number
        self.name: str = name
        self.group_id: str = group_id
        self.tg_id: int = tg_id
        self.subjects = subjects
        self.assignments = []
        self.is_subbed = is_subbed

        dict.__init__(
            self,
            number=self.number,
            name=self.name,
            group_id=self.group_id,
            tg_id=self.tg_id,
            assignments=self.assignments,
            is_subbed=self.is_subbed
        )

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
