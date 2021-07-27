class Assignment:
    """Задание."""

    def __init__(self, weight: float, values):
        self.weight = weight
        self.values = values

    @property
    def total(self) -> float:
        """Получить общую оценку по заданию.

        `вес*СУММ(рез-ты)`
        """
        return sum(self.values) * self.weight
