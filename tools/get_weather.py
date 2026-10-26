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
            "Используй, если пользователь спрашивает «Какая сейчас погода?», «Что на улице?», погоду в конкретном городе, температуру/дождь/ветер, "
            "или просит совет по одежде и планам на улице («Что надеть?», «Брать ли зонт?», «Можно ли гулять?»).\n"
            "\n"
            "Параметр city_name (опционально): название города на английском (например, 'Moscow', 'London'). "
            "Если пользователь назвал город — обязательно передай его. "
            "Если город не указан — не передавай параметр, функция возьмет город по умолчанию.\n"
            "\n"
            "Формат ответа: температура всегда в °C. В ответе будет указан город. "
            "Если пользователь не называл город, сообщи ему, что это погода для города по умолчанию. "
            "Если success=False — сообщи об ошибке."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": (
                        "Название города. Передавай только если пользователь явно его назвал. "
                        "Если не назван — не передавай параметр."
                    ),
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}
