from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from tzlocal import get_localzone_name
from config import DEFAULT_TIMEZONE


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
            "Используй, если пользователь спрашивает «который час?», «сколько времени?», текущее время, дату или время в конкретном городе/стране (например, «который час в Москве?»).\n"
            "НЕ используй для вопросов о прошлом/будущем (например, «что было вчера?») или абстрактных рассуждений о времени.\n"
            "\n"
            "Параметр timezone (опционально): IANA-имя зоны (например, 'Europe/Moscow', 'America/New_York', 'UTC'). "
            "Если пользователь назвал город — сам преобразуй его в IANA-зону (Москва -> Europe/Moscow). "
            "Если зона не указана — не передавай параметр, функция возьмет локальную. "
            "Указывай 'UTC' только если просят именно UTC.\n"
            "\n"
            "Функция возвращает словарь:\n"
            "- success (bool): True/False.\n"
            "- error (str): текст ошибки (или None).\n"
            "- result (str): время в формате 'YYYY-MM-DD HH:MM:SS' (или None).\n"
            "Если success=False — сообщи об ошибке текстом из поля error, не выдумывай время. "
            "Если success=True — используй result для ответа."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": (
                        "IANA-имя таймзоны ('Europe/Moscow', 'UTC' и т.д.). "
                        "Оставь пустым, если пользователь не указал зону. "
                        "Регистр важен."
                    ),
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}
