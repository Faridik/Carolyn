from logging import addLevelName
import uuid


class Assignment(dict):
    """Задание."""

    def __init__(
        self,
        name: str,
        points: list,
        weight: float = 1,
        subject: str = None,
        allow_to_display: bool = False,
        how_to_display: str = "z,1,1",
        notes: str = "Замечаний по работе нет.",
    ):
        self.name = name
        self.subject = subject
        self.weight = weight
        self.points = points
        self.allow_to_display = allow_to_display
        self.how_to_display = how_to_display
        self.notes = notes
        self.uuid = uuid.uuid3(uuid.NAMESPACE_DNS, f"{name}{subject}")
        dict.__init__(
            self,
            name=self.name,
            subject=self.subject,
            weight=self.weight,
            points=self.points,
            total=self.total,
            allow_to_display=self.allow_to_display,
            how_to_display=self.how_to_display,
            notes=self.notes,
            uuid=self.uuid,
        )

    @property
    def total(self) -> float:
        """Получить общую оценку по заданию.

        `вес*СУММ(рез-ты)`
        """
        return sum(self.points) * self.weight
