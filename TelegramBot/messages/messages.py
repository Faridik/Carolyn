import random


class Messages:
    class Auth:
        NO_AUTH = "[Правила авторизации](https://github.com/Faridik/Carolyn/wiki/%F0%9F%A6%B8%E2%80%8D%E2%99%82%EF%B8%8F-%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)"
        START = "🔑 Авторизация..."
        NO_ACCESS = "⛔ Нет доступа"

        @staticmethod
        def hello(data):
            name = data.get("name", "студент")
            return f"Привет, {name} 👋"

        @staticmethod
        def failure(err: str):
            cases = {
                "StudentNotFound": "⛔ Ссылка больше не работает",
                "StudentAlreadyAuthed": "⛔ Регистрация по этой ссылке уже прошла",
                "AnotherStudentAlreadyAuthed": "😨 Кто-то другой уже зерегистрировался по этой ссылке",
            }
            return cases.get(err, "😟 Возникли неполадки")

    class Assignments:
        START = "👀 Посмотрим (~3с) ..."
        SELECT_COURSE = "👇 Выбери дисциплину"
        SELECT_ASSNT = "👇 Выбери работу"
        END = "😉 Всего наилучшего"
        TIMEOUT = "🕛 Время запроса вышло"

        @staticmethod
        def get(name: str, assignment: list, how_to_display: str, notes: str):
            is_float, n_cols, n_rows = how_to_display.split(',')
            n_cols, n_rows = int(n_cols), int(n_rows)
            summary = f'<b>{name}</b>:\n'
            if is_float == 'z':
                d = {0 : '❎', 1 : '✅'}
                for item in range(0, len(assignment), n_cols):
                    summary += ''.join(list(map(d.get, 
                        assignment[item : item + n_cols]))) + '\n'
            elif is_float == 'r':
                to_str = lambda x: f'{x:.2f}'
                for item in range(0, len(assignment), n_cols):
                    summary += ' '.join(list(map(to_str,
                        assignment[item: item + n_cols]))) + '\n'
                summary += f'Σ: {to_str(sum(assignment))}\n'
            summary += f"\n{notes}"
            return summary

        @staticmethod
        def timeit(t: float):
            return f"⏱ Посмотрели за {t:.2f}с"

    class Spreadsheets:
        pass

    class Stickers:
        # Воробей павлик с колокольчиком и надписью "позор"
        POZOR = (
            "CAACAgIAAxkBAAEm1RhhBZg-2D6NypUeTsnbToD8_LMFTAACuUcAAulVBRjfnofQTkeMnCAE"
        )
        # кот Сима в петле плачет и показывает палец вверх
        ROPE = (
            "CAACAgIAAxkBAAEm1SFhBZjLaZgFIkvyxfBmAplwUWQFwwACBS0AAulVBRiIaSQ42WLoyyAE"
        )
        # Акио смотрит на брокколи
        BROCCOLI = (
            "CAACAgIAAxkBAAEm1SVhBZkd24Dy2B_wYSCi6UrNuUjgwQACEUkAAulVBRiykDzrzywbmiAE"
        )
        # Ян показывает палец вниз
        THUMB_DOWN = (
            "CAACAgIAAxkBAAEm1SthBZlcos0_TbJo8W7mAcqGLNAh2wACJ5cAAp7OCwABDddMclD7Tf8gBA"
        )
        # Тигр закатывает глаза
        EYES_UP = (
            "CAACAgEAAxkBAAEm1TBhBZmIZTrwzhGSzC47rNFbewQe6QAC4gADOA6CEeTgk4YIcTeWIAQ"
        )
        # Нутри большими глазами и надписью "пипец"
        PPTS = (
            "CAACAgIAAxkBAAEm1TZhBZnNVwLXmrbZwvdGjxiSwefzDAACn0sAAulVBRhECmBPSGCXHSAE"
        )
        # Попугай Кент с недовольной мордахой
        GRUMPY_KENT = (
            "CAACAgIAAxkBAAEm1UBhBZn1gXmRfxaK_RqFTj1aFxLY-gACy0EAAulVBRhgQdlH2rd0uyAE"
        )
        # wojak
        WOJAK = (
            "CAACAgIAAxkBAAEm1UJhBZpfHNYVT_ZLrxUpyi8qRLWJGgACPAADB7lDCi2YrzAEyxJeIAQ"
        )
        # Лэтишный котик и надпись "ОЙ"
        OOPS = (
            "CAACAgIAAxkBAAEm1URhBZp2li7w2E1M6PirG7UnqLOc2QACSxEAAlTE4UoR1Olz8RANZCAE"
        )
        # Мем "оп ахах неловко вышло"
        NELOVKO = (
            "CAACAgIAAxkBAAEm1UZhBZqZ94SFa1e6d-Zy5I-6_SC_fQACgwgAAh8MqEiLbHl9nugoYSAE"
        )
        # Попугай смотрит в зеркало "посмотри что с тобой стало"
        MIRROR = (
            "CAACAgIAAxkBAAEm1VFhBZudma_FmFhybGgXikz3csc0BQAC2UEAAulVBRgkdje995ir7iAE"
        )
        # Попугай с сигаретой
        CIG = "CAACAgIAAxkBAAEm1VZhBZv6p7GsHS6wcyt2mCXoHJCo-wAC0UEAAulVBRghLLSQAcU6rSAE"
        # Попугай и песок
        SAND = (
            "CAACAgIAAxkBAAEm1VhhBZwbw83_UVS8A5Crsf3EVAABvWIAAshBAALpVQUYl51K7ci-ClIgBA"
        )
        # Акио падает в обморок
        PANIC = (
            "CAACAgIAAxkBAAEm1VxhBZxwqRUJmVXDtzmsPJUIIGJgegACB0kAAulVBRiMI-hzK3GcKiAE"
        )
        # Эникей надпись "умер"
        DEAD = (
            "CAACAgIAAxkBAAEm1aRhBaWXRb_tcI03O1onx0jW0bHmuAACejcAAulVBRi1oSUXeBATmiAE"
        )

        @classmethod
        def bad(self):
            """Возвращает стикер с грустным смыслом."""
            return random.choice(
                [
                    self.POZOR,
                    self.ROPE,
                    self.BROCCOLI,
                    self.THUMB_DOWN,
                    self.EYES_UP,
                    self.PPTS,
                    self.GRUMPY_KENT,
                    self.WOJAK,
                    self.OOPS,
                    self.NELOVKO,
                    self.MIRROR,
                    self.CIG,
                    self.SAND,
                    self.PANIC,
                ]
            )
