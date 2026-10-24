from __future__ import annotations
import os


def read_file_content(
    file_path: str = ".", limit_of_chars: int = 6000, offset: int = 0
) -> dict:

    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"Данный путь не существует: {file_path}",
            "result": None,
        }

    if not os.path.isfile(file_path):
        return {
            "success": False,
            "error": f"Не является файлом: {file_path}",
            "result": None,
        }

    if os.path.getsize(file_path) == 0:
        return {
            "success": True,
            "error": None,
            "result": f"Файл пуст (0 байт): {file_path}",
        }

    if not os.access(file_path, os.R_OK):
        return {
            "success": False,
            "error": f"Нет доступа к чтению файла: {file_path}",
            "result": None,
        }

    try:
        with open(file=file_path, mode="r", encoding="utf-8") as f:
            f.seek(offset)
            content = f.read(limit_of_chars)

            if not content:
                return {
                    "success": True,
                    "error": None,
                    "result": f"Достигнут конец файла {file_path}. Данных с индекса {offset} не существует.",
                }

            is_cutted = bool(f.read(1))

        if is_cutted:
            result_text = f"Данные из файла {file_path} (символы с индексом от {offset} до {offset + len(content) - 1}):\n{content}\n\n[ALERT] Файл обрезан. Чтобы прочитать продолжение, вызови функцию снова с offset={offset + len(content)}."
        else:
            result_text = f"Данные из файла {file_path} (символы с индексом от {offset} до {offset + len(content) - 1}):\n{content}"

        return {"success": True, "error": None, "result": result_text}

    except UnicodeDecodeError:
        return {
            "success": False,
            "error": f"Не удалось прочитать файл как текст (бинарный файл или другая кодировка): {file_path}",
            "result": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Произошла ошибка: {str(e)}",
            "result": None,
        }


read_file_content.tool_description = {
    "type": "function",
    "function": {
        "name": "read_file_content",
        "description": (
            "Читает и возвращает текстовое содержимое указанного файла.\n"
            "\n"
            "КОГДА ИСПОЛЬЗОВАТЬ:\n"
            "- Пользователь просит «прочитай файл ...», «что написано в ...», «покажи содержимое ...».\n"
            "- Нужно проанализировать код, логи, конфигурацию или любой текстовый файл.\n"
            "- Пользователь просит найти что-то в файле (сначала нужно прочитать его содержимое).\n"
            "\n"
            "АРГУМЕНТЫ:\n"
            "- file_path (обязательно): путь к файлу (например, 'main.py', '/home/user/notes.txt').\n"
            "- limit_of_chars (опционально): сколько символов прочитать за один раз. По умолчанию 6000.\n"
            "- offset (опционально): с какого индекса начать чтение. По умолчанию 0 (с начала файла).\n"
            "\n"
            "ФОРМАТ ОТВЕТА:\n"
            "Функция возвращает готовый текст в поле 'result'. В начале текста указаны индексы прочитанных символов.\n"
            "Если файл длиннее, чем limit_of_chars, в конце будет строка [ALERT]. "
            "В этой строке будет указан точный 'offset', который нужно передать при следующем вызове, чтобы прочитать продолжение.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА ПОЛЬЗОВАТЕЛЮ:\n"
            "1. Если пользователь попросил прочитать весь файл, а в ответе есть [ALERT] (файл обрезан), ты ОБЯЗАН вызвать эту же функцию снова, передав offset из [ALERT]. Повторяй это, пока не прочитаешь файл до конца (пока не исчезнет [ALERT]).\n"
            "2. Если пользователь просил только начало или определенный кусок, просто выведи прочитанный текст. Маркер [ALERT] в ответе пользователю выводить не нужно (просто упомяни, что файл длинный и показано только начало)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу, который нужно прочитать.",
                },
                "limit_of_chars": {
                    "type": "integer",
                    "description": "Максимальное количество символов для чтения за один раз. По умолчанию 6000.",
                    "minimum": 100,
                    "maximum": 20000,
                },
                "offset": {
                    "type": "integer",
                    "description": "Индекс символа, с которого начать чтение. По умолчанию 0.",
                    "minimum": 0,
                },
            },
            "required": ["file_path"],
            "additionalProperties": False,
        },
    },
}
