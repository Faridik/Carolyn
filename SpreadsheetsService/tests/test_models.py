import pytest
from models import *


ASSIGNMENTS = ((1, [1, 1, 1]), (10, [0.1, 0.8, 0.5]), (2, [1, 0, 1, 0]))
STUDENTS = (
    (1, "Бмэ Бобтубтйа"),
    (2, "Боупопгб Нймбоб"),
    (3, "Вспогбмэе Мёпойе"),
    (4, "Дсйщйо Туёрбо"),
    (5, "Еиёко Ейбоб"),
    (6, "Еиявб Бооб"),
    (7, "Ёмпглп Ебсэа"),
    (8, "Лмёёг Ебойм"),
    (9, "Лпсоёёг Лйсймм"),
    (10, "Лпсойёолп Ойлйуб"),
    (11, "Лпшлйо Йгбо"),
    (12, "Лфсвбо Йгбо"),
    (13, "Нбмэлпг Боесёк"),
    (14, "Нботфспг Гмбейнйс"),
    (15, "Нпйтёёг Лйсймм"),
    (16, "Обибспг Уйнпхёк"),
    (17, "Одфбезйп Одфёттпод Туйг Сб"),
    (18, "Псёцпг Гмбейтмбг"),
    (19, "Тёсёвсёоойлпгб Бобтубтйа"),
    (20, "Тусфшйо Бобупмйк"),
    (21, "Ублбмпгб Лбнйммб"),
    (22, "Убсбтёгйш Пмэдб"),
    (23, "Уплбсёг Тёсдёк"),
    (24, "Успхйнпгб Бобтубтйа"),
    (25, "Шфвбс Ебойм"),
    (26, "Щбупг Нйцбйм"),
)


class TestStudent:
    def test_init(self):
        student = Student(1, "Фарид Михайлов", "42")
        assert student.name == "Фарид Михайлов"
        assert student.number == 1

    def test_student_assignments(self):
        student = Student(1, "Фарид Михайлов", "42")

        ass = [Assignment(weight, values) for weight, values in ASSIGNMENTS]
        for a in ass:
            student.add_assignment(a)

        assert student.score > 0


class TestGroup:
    @staticmethod
    def init_group():
        group_id = 5374
        group = Group(5374)
        for el in STUDENTS:
            student = Student(el[0], el[1], group_id)
            group.add_student(student)
        return group

    def test_init(self):
        group = self.init_group()

        for student in group:
            assert type(student) is Student

    def test_search(self):
        group = self.init_group()

        ebob = group.get_student_by_number(5)
        assert ebob.name == "Еиёко Ейбоб"

        students = group.find_students("Йгбо")
        assert len(students) == 2
