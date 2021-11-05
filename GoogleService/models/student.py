from .assignment import Assignment
import uuid


class Student(dict):
    """Позволяет выполнять операции над студентами."""

    def __init__(
        self,
        number: int,
        name: str,
        group_id: str,
        tg_id: int = None,
        subjects: list = None,
        is_subbed: bool = False,
    ):
        self.number: int = number
        self.name: str = name
        self.group_id: str = group_id
        self.tg_id: int = tg_id
        self.subjects = subjects
        self.assignments = []
        self.is_subbed = is_subbed
        self.fingerprint = ""

        dict.__init__(
            self,
            number=self.number,
            name=self.name,
            group_id=self.group_id,
            tg_id=self.tg_id,
            assignments=self.assignments,
            fingerprint=self.fingerprint,
            is_subbed=self.is_subbed,
        )

    def add_assignment(self, assignment: Assignment):
        self.assignments.append(assignment)
        self._update_fingerprint()

    @property
    def score(self):
        """Количество баллов у студента."""
        return sum([a.total for a in self.assignments])

    def _update_fingerprint(self) -> None:
        fingerprint = uuid.uuid3(uuid.NAMESPACE_DNS, "%s" % self.assignments)
        self.fingerprint = fingerprint
        self["fingerprint"] = fingerprint
