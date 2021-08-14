from .student import Student


class StudentNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Group(dict):
    """Объект "Группа" для работы со списком студентов.
    Используется для работы с множеством студентов.
    """

    def __init__(self, group_id: str):
        self._group_id: str = group_id
        self._students: Student = []

        dict.__init__(
            self,
            group_id=self.group_id,
            students=self._students,
        )

    def __iter__(self):
        """Делегирует итератор на список студентов.

        Так, можно использовать конструкцию
        ```python
        for student in group
        ```
        """
        return iter(self._students)

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, value):
        self["group_id"] = value
        self._group_id = value

    def add_student(self, student: Student):
        """Добавить студента в группу."""
        self._students.append(student)

    def get_student_by_number(self, number: int) -> Student:
        """Возвращает студента по его номеру, если номера нет, то поднимает
        ошибку."""
        f = lambda s: number == s.number
        try:
            return next(filter(f, self._students))
        except StopIteration:
            raise StudentNotFound("Не могу найти студента по номеру")

    def find_students(self, name: str) -> list:
        """Найти студентов в группе по имени.

        Возвращает список найденных студентов. Если никого не найдет, вернет
        пустой список.

        Arguments:
            name (str): текстовое поле, часть имени.
        """

        f = lambda s: name.lower() in s.name.lower()
        return list(filter(f, self._students))

    def top(self, n: int = None) -> list:
        """Топ N студентов группы по среднему баллу. Возвращает весь список,
        если N не указано."""
        n = len(self._students) if n is None else n
        return sorted(self._students, key=lambda student: student.grade)[:n]

    def between(self, a: float, b: float) -> list:
        """Список студентов, у которых оценка между [a, b]."""
        f = lambda student: a < student.average < b
        return list(filter(f, self._students))
