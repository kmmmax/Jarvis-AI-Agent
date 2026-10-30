from __future__ import annotations
import os


def touch_file(file_path: str = "") -> dict:

    if not file_path:
        return {
            "success": False,
            "error": f"Не указан путь для файла: {file_path}",
            "result": None,
        }

    try:
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(file=file_path, mode="x", encoding="utf-8") as f:
            pass

        return {
            "success": True,
            "error": None,
            "result": f"Пустой файл успешно создан: {file_path}",
        }

    except FileExistsError:
        return {
            "success": False,
            "error": f"Файл уже существует: {file_path}",
            "result": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Произошла ошибка: {str(e)}",
            "result": None,
        }


touch_file.tool_description = {
    "type": "function",
    "function": {
        "name": "touch_file",
        "description": (
            "Создаёт новый пустой файл по указанному пути.\n"
            "Используй, если пользователь просит «создай файл...», «сделай пустой файл...», «создай заготовку...». "
            "Если файл с таким именем уже существует, вернёт ошибку и НЕ перезапишет его.\n"
            "\n"
            "Параметры:\n"
            "- file_path (обязательно): путь к файлу ('main.py', 'notes/todo.txt', '/home/user/file.txt').\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает статус в поле 'success', текст ошибки в 'error' (если есть) "
            "и сообщение в 'result'. Если файл создан, 'success' будет True, а в 'result' — путь.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Если пользователь просит создать файл в папке, которой нет, функция создаст папку автоматически.\n"
            "2. Если файл уже существует, функция вернёт ошибку. В этом случае не пытайся создать его снова, "
            "а сообщи пользователю, что файл уже есть."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Путь к новому файлу.",
                },
            },
            "required": ["file_path"],
            "additionalProperties": False,
        },
    },
}
