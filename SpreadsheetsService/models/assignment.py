class Assignment:
    """Задание."""

    def __init__(self, name: str, values: list, weight: float=1):
        self.name = name
        self.weight = weight
        self.values = values

    @property
    def total(self) -> float:
        """Получить общую оценку по заданию.

        `вес*СУММ(рез-ты)`
        """
        return sum(self.values) * self.weight
