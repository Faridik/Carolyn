import random


class Messages:
    class Auth:
        def __init__(self):
            self.NO_AUTH = "[Правила авторизации](https://github.com/Faridik/Carolyn/wiki/%F0%9F%A6%B8%E2%80%8D%E2%99%82%EF%B8%8F-%D0%90%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)"
            self.START = "🔑 Авторизация..."
            self.NO_ACCESS = "⛔ Нет доступа"

        def hello(self, data):
            return f"Привет, {data} 👋"

    class Score:
        def get(self, grade, score, n_of_assignments):
            summary = (
                f"Ранг: <b>{score:.2f}</b> {n_of_assignments} зад.\n"
                + f"Оценка: <b>{grade:.2f}</b>"
            )
            return summary

    class Spreadsheets:
        def __init__(self):
            self.DEAD = "⚰ Сервис «таблицы» недоступен"

    class Stickers:
        def __init__(self):
            # Воробей павлик с колокольчиком и надписью "позор"
            self.POZOR = "CAACAgIAAxkBAAEm1RhhBZg-2D6NypUeTsnbToD8_LMFTAACuUcAAulVBRjfnofQTkeMnCAE"
            # кот Сима в петле плачет и показывает палец вверх
            self.ROPE = "CAACAgIAAxkBAAEm1SFhBZjLaZgFIkvyxfBmAplwUWQFwwACBS0AAulVBRiIaSQ42WLoyyAE"
            # Акио смотрит на брокколи
            self.BROCCOLI = "CAACAgIAAxkBAAEm1SVhBZkd24Dy2B_wYSCi6UrNuUjgwQACEUkAAulVBRiykDzrzywbmiAE"
            # Ян показывает палец вниз
            self.THUMB_DOWN = "CAACAgIAAxkBAAEm1SthBZlcos0_TbJo8W7mAcqGLNAh2wACJ5cAAp7OCwABDddMclD7Tf8gBA"
            # Тигр закатывает глаза
            self.EYES_UP = "CAACAgEAAxkBAAEm1TBhBZmIZTrwzhGSzC47rNFbewQe6QAC4gADOA6CEeTgk4YIcTeWIAQ"
            # Нутри большими глазами и надписью "пипец"
            self.PPTS = "CAACAgIAAxkBAAEm1TZhBZnNVwLXmrbZwvdGjxiSwefzDAACn0sAAulVBRhECmBPSGCXHSAE"
            # Попугай Кент с недовольной мордахой
            self.GRUMPY_KENT = "CAACAgIAAxkBAAEm1UBhBZn1gXmRfxaK_RqFTj1aFxLY-gACy0EAAulVBRhgQdlH2rd0uyAE"
            # wojak
            self.WOJAK = "CAACAgIAAxkBAAEm1UJhBZpfHNYVT_ZLrxUpyi8qRLWJGgACPAADB7lDCi2YrzAEyxJeIAQ"
            # Лэтишный котик и надпись "ОЙ"
            self.OOPS = "CAACAgIAAxkBAAEm1URhBZp2li7w2E1M6PirG7UnqLOc2QACSxEAAlTE4UoR1Olz8RANZCAE"
            # Мем "оп ахах неловко вышло"
            self.NELOVKO = "CAACAgIAAxkBAAEm1UZhBZqZ94SFa1e6d-Zy5I-6_SC_fQACgwgAAh8MqEiLbHl9nugoYSAE"
            # Попугай смотрит в зеркало "посмотри что с тобой стало"
            self.MIRROR = "CAACAgIAAxkBAAEm1VFhBZudma_FmFhybGgXikz3csc0BQAC2UEAAulVBRgkdje995ir7iAE"
            # Попугай с сигаретой
            self.CIG = "CAACAgIAAxkBAAEm1VZhBZv6p7GsHS6wcyt2mCXoHJCo-wAC0UEAAulVBRghLLSQAcU6rSAE"
            # Попугай и песок
            self.SAND = "CAACAgIAAxkBAAEm1VhhBZwbw83_UVS8A5Crsf3EVAABvWIAAshBAALpVQUYl51K7ci-ClIgBA"
            # Акио падает в обморок
            self.PANIC = "CAACAgIAAxkBAAEm1VxhBZxwqRUJmVXDtzmsPJUIIGJgegACB0kAAulVBRiMI-hzK3GcKiAE"
            # Эникей надпись "умер"
            self.DEAD = "CAACAgIAAxkBAAEm1aRhBaWXRb_tcI03O1onx0jW0bHmuAACejcAAulVBRi1oSUXeBATmiAE"

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

    def __init__(self):
        self.auth = self.Auth()
        self.score = self.Score()
        self.spreadsheets = self.Spreadsheets()
        self.stickers = self.Stickers()
