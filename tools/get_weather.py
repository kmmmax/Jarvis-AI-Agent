from __future__ import annotations
import requests

DEFAULT_CITY = "moscow"
PROXIES = {"http": "http://192.168.88.250:10808"}


def get_weather(city_name: str | None = None) -> dict:

    if isinstance(city_name, str):
        url = f"http://wttr.in/{city_name}?format=j1"
        city = city_name.capitalize()
    else:
        url = f"http://wttr.in/{DEFAULT_CITY}?format=j1"
        city = DEFAULT_CITY.capitalize()

    try:
        data = requests.get(url, proxies=PROXIES).json()

        current_condition = data["current_condition"][0]
        temperature = current_condition["temp_C"]
        how_feels = current_condition["FeelsLikeC"]
        humidity = current_condition["humidity"]
        description = current_condition["weatherDesc"][0]["value"]

        forecast_today = data["weather"][0]
        max_temp = forecast_today["maxtempC"]
    except:
        return {
            "success": False,
            "error": "Произошла ошибка при получении данных с API.",
            "result": None,
        }

    return {
        "success": True,
        "error": None,
        "result": f"Погода в городе {city}: {description}. Температура: {temperature}°C (ощущается как {how_feels}°C). Влажность: {humidity}%. Прогноз максимальной температуры на сегодня: {max_temp}°C.",
    }


get_weather.tool_description = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Возвращает текущую погоду и максимальную температуру на сегодня.\n"
            "\n"
            "КОГДА ИСПОЛЬЗОВАТЬ:\n"
            "- Пользователь спрашивает «Какая сейчас погода?», «Что на улице?».\n"
            "- Пользователь спрашивает погоду в конкретном городе («Какая погода в Москве?»).\n"
            "- Пользователь спрашивает про температуру, дождь, ветер, влажность.\n"
            "- Пользователь спрашивает, как одеться («Что мне надеть?», «В чем идти сегодня?», «Нужна ли куртка?», «Брать ли зонт?»).\n"
            "- Пользователь строит планы на улице («Можно ли сегодня гулять?», «Стоит ли идти на пробежку?»).\n"
            "\n"
            "АРГУМЕНТЫ:\n"
            "- city_name (опционально): название города (например, 'Moscow', 'London', 'Санкт-Петербург').\n"
            "  Если пользователь указал город — ОБЯЗАТЕЛЬНО передай его в этом параметре.\n"
            "  Если пользователь НЕ указал город (просто «какая погода?» или «что надеть?») — не передавай этот параметр. "
            "Функция автоматически подставит город по умолчанию (Москва).\n"
            "\n"
            "ФОРМАТ ОТВЕТА:\n"
            "Функция всегда возвращает температуру в градусах Цельсия (°C).\n"
            "В ответе всегда будет указан город, для которого получена погода. "
            "Если город не был указан пользователем, используй город, который вернула функция "
            "(город по умолчанию), и сообщи пользователю, что это погода для этого города.\n"
            "Если success=False — сообщи об ошибке."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": (
                        "Название города, для которого нужна погода. "
                        "Передавай только если пользователь явно назвал город. "
                        "Если город не назван — не передавай параметр."
                    ),
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}
