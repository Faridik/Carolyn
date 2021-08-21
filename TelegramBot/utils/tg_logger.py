import logging
from typing import Any, Optional


class TgLogger(logging.Logger):
    """Обертка на логгер, чтобы можно было использовать обычные лог-функции,
    но при этом получать логи в телеграм чат.

    Есть баг, который не позволяет вызывать лог с ленивыми аргументами. Если
    вызывать
    ```python
    LOG.warning("%s", var)
    ```
    , то можно получить такую ошибку:
    ```python
    TypeError: _log_to_telegram() got multiple values for argument 'msg'
    ```
    Поэтому используйте,
    ```
    LOG.warning(f"{var}")
    ```
    """

    CHAT_LOG_ID = -507530583  # ID канала где собираются логи

    def __init__(self, name, level=logging.NOTSET):
        self._bot = None
        return super(TgLogger, self).__init__(name, level)

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    def _log_to_telegram(
        self,
        msg: str,
        *args,
        emoji: str,
    ):
        if self._bot is not None:
            txt = f"{emoji} {msg};"
            self._bot.send_message(chat_id=self.CHAT_LOG_ID, text=txt)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="⚠", *args)
        return super().warning(
            msg,
            *args,
            **kwargs,
        )

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="💢", *args)
        return super().error(
            msg,
            *args,
            **kwargs,
        )

    def exception(self, msg, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="💥", *args)
        return super().exception(msg, *args, **kwargs)
