from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from tzlocal import get_localzone_name

DEFAULT_TIMEZONE = "Europe/Moscow"


def local_timezone() -> str:
    timezone = get_localzone_name()
    if isinstance(timezone, str):
        return timezone
    else:
        return DEFAULT_TIMEZONE


def get_current_time(timezone: str | None = None) -> dict:

    if timezone is None:
        timezone = local_timezone()

    if not isinstance(timezone, str):
        return {
            "success": False,
            "error": "Неверный тип данных для параметра timezone. "
            "Ожидается строка с названием таймзоны или None, если пользователь не указал зону.",
            "result": None,
        }

    try:
        object_of_timezone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return {
            "success": False,
            "error": "Не удалось создать объект таймзоны. Проверьте название часового пояса.",
            "result": None,
        }
    time = datetime.now(object_of_timezone)
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return {"success": True, "error": None, "result": formatted_time}


get_current_time.tool_description = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": (
            "Возвращает текущие дату и время в указанной таймзоне.\n"
            "\n"
            "КОГДА ИСПОЛЬЗОВАТЬ:\n"
            "- Пользователь спрашивает «сколько сейчас времени?», «который час?».\n"
            "- Пользователь спрашивает «какое сегодня число?», «какая дата?».\n"
            "- Пользователь спрашивает время в конкретном городе или стране "
            "(«который час в Москве?», «сколько времени в Нью-Йорке?»).\n"
            "- Пользователь просит узнать текущее время для любой цели.\n"
            "\n"
            "КОГДА НЕ ИСПОЛЬЗОВАТЬ:\n"
            "- Пользователь спрашивает о прошлом или будущем («что было вчера?», "
            "«какой день будет через неделю?»).\n"
            "- Пользователь спрашивает о времени в абстрактном смысле, без привязки "
            "к текущему моменту.\n"
            "- Вопрос не связан с текущим временем или датой.\n"
            "\n"
            "АРГУМЕНТЫ:\n"
            "- timezone (опционально): имя таймзоны в формате IANA, например "
            "'Europe/Moscow', 'America/New_York', 'Asia/Tokyo', 'UTC'.\n"
            "  Если пользователь назвал город — сам преобразуй его в подходящую "
            "IANA-таймзону. Например, «Москва» → 'Europe/Moscow', "
            "«Нью-Йорк» → 'America/New_York'.\n"
            "  Если пользователь не указал таймзону — не передавай параметр, "
            "функция сама подставит локальную таймзону компьютера.\n"
            "  Явно указывай 'UTC' только если пользователь просит именно UTC.\n"
            "\n"
            "ЧТО ВОЗВРАЩАЕТ:\n"
            "Словарь с тремя ключами:\n"
            "- success (bool): True если время получено, False при ошибке.\n"
            "- error (str | None): текст ошибки или None при успехе.\n"
            "- result (str | None): строка с датой и временем в формате "
            "'YYYY-MM-DD HH:MM:SS' или None при ошибке.\n"
            "\n"
            "Если success=False — сообщи пользователю об ошибке, используя текст "
            "из поля error. Не пытайся выдумать время самостоятельно.\n"
            "Если success=True — используй значение из поля result для ответа "
            "пользователю."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": (
                        "Имя таймзоны в формате IANA, например "
                        "'Europe/Moscow', 'Europe/Berlin', 'America/New_York', 'UTC'. "
                        "Регистр важен. Если пользователь не указал таймзону — "
                        "не передавай этот параметр, функция сама подставит "
                        "локальную таймзону компьютера."
                    ),
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}
