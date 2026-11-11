from __future__ import annotations
import os
from config import SANDBOX_DIR


def write_file(file_path: str = "", content: str = "") -> dict:

    if not file_path:
        return {
            "success": False,
            "error": "Не указан путь для файла",
            "result": None,
        }

    absolute_path = os.path.realpath(file_path)

    if not absolute_path.startswith(SANDBOX_DIR + os.sep):
        return {
            "success": False,
            "error": f"Доступ запрещён. Записывать файлы можно только внутри песочницы: {SANDBOX_DIR}",
            "result": None,
        }

    if not os.path.exists(absolute_path):
        return {
            "success": False,
            "error": f"Данный путь не существует: {file_path}",
            "result": None,
        }

    if not os.path.isfile(absolute_path):
        return {
            "success": False,
            "error": f"Не является файлом: {file_path}",
            "result": None,
        }

    if not os.access(absolute_path, os.W_OK):
        return {
            "success": False,
            "error": f"Нет доступа к записи в файл: {file_path}",
            "result": None,
        }

    try:
        with open(file=absolute_path, mode="w", encoding="utf-8") as f:
            f.write(content)

        if content == "":
            result_text = f"Файл {file_path} успешно очищен (удалено все содержимое)"
        else:
            result_text = (
                f"Файл {file_path} успешно перезаписан ({len(content)} символов)"
            )

        return {"success": True, "error": None, "result": result_text}

    except Exception as e:
        return {
            "success": False,
            "error": f"Произошла ошибка: {str(e)}",
            "result": None,
        }


write_file.tool_description = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": (
            "Полностью перезаписывает существующий файл новым текстом.\n"
            "Используй, если пользователь просит «перепиши файл...», «измени содержимое...», "
            "«сохрани изменения в...» или «очисти файл».\n"
            "\n"
            "Параметры:\n"
            "- file_path (обязательно): путь к файлу ('main.py', 'notes/todo.txt').\n"
            "- content (обязательно): новый текст, который нужно записать. "
            "Если нужно полностью очистить файл, передай пустую строку ''.\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает статус в поле 'success', текст ошибки в 'error' (если есть) "
            "и сообщение в 'result'. Если запись прошла успешно, 'success' будет True.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Файл должен уже существовать и находиться внутри песочницы. Если его нет или путь ведет за её пределы, вернётся ошибка.\n"
            "2. Если пользователь просит «очисти файл», передай content='' (пустую строку).\n"
            "3. Если пользователь просит изменить только часть файла, сначала вызови read_file_content, "
            "измени текст, а затем передай сюда весь новый текст целиком."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу, который нужно перезаписать.",
                },
                "content": {
                    "type": "string",
                    "description": "Новый текст для файла. Передай пустую строку '', чтобы полностью стереть содержимое.",
                },
            },
            "required": ["file_path", "content"],
            "additionalProperties": False,
        },
    },
}
