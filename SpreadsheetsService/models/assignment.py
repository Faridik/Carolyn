class Assignment(dict):
    """Задание."""

    def __init__(self, name: str, points: list, weight: float = 1, subject: str = None):
        self.name = name
        self.subject = subject
        self.weight = weight
        self.points = points
        dict.__init__(
            self,
            name=self.name,
            subject=self.subject,
            weight=self.weight,
            points=self.points,
            total=self.total,
        )

    @property
    def total(self) -> float:
        """Получить общую оценку по заданию.

        `вес*СУММ(рез-ты)`
        """
        return sum(self.points) * self.weight
