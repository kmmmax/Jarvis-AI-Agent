from __future__ import annotations
import os


def read_file_content(
    file_path: str = "", limit_of_chars: int = 5000, offset: int = 0
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
            "Используй, если пользователь просит «прочитай файл...», «что написано в...», «покажи содержимое...», "
            "или нужно проанализировать код/логи/конфиг, или найти что-то в файле.\n"
            "\n"
            "Параметры:\n"
            "- file_path (обязательно): путь к файлу ('main.py', '/home/user/notes.txt').\n"
            "- limit_of_chars (опционально): сколько символов читать за раз. По умолчанию 5000.\n"
            "- offset (опционально): с какого индекса начать чтение. По умолчанию 0. "
            "Отсчёт индексов начинается с 0. Например, если пользователь просит «начать с 500-го символа», передай offset=499.\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает текст в поле 'result'. В начале указаны индексы прочитанных символов. "
            "Если файл длиннее limit_of_chars, в конце будет строка [ALERT] с точным 'offset' для следующего вызова.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Если пользователь попросил прочитать весь файл, а в ответе есть [ALERT], ты ОБЯЗАН вызвать функцию снова, передав offset из [ALERT]. "
            "Повторяй, пока файл не будет прочитан до конца (пока [ALERT] не исчезнет).\n"
            "2. Если просили только начало или кусок — просто выведи текст. Маркер [ALERT] пользователю не показывай, просто упомяни, что файл длинный и показана только часть."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу.",
                },
                "limit_of_chars": {
                    "type": "integer",
                    "description": "Максимум символов за раз. По умолчанию 5000.",
                    "minimum": 100,
                    "maximum": 20000,
                },
                "offset": {
                    "type": "integer",
                    "description": "Индекс символа, с которого начинать чтение (отсчёт с 0). Например, если пользователь просит «считать с 500-го символа», передай offset=499.",
                    "minimum": 0,
                },
            },
            "required": ["file_path"],
            "additionalProperties": False,
        },
    },
}
