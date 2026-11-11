from __future__ import annotations
import os
from config import SANDBOX_DIR


def touch_dir(dir_path: str = "") -> dict:

    if not dir_path:
        return {
            "success": False,
            "error": "Не указан путь для директории",
            "result": None,
        }

    absolute_path = os.path.realpath(dir_path)

    if not absolute_path.startswith(SANDBOX_DIR + os.sep):
        return {
            "success": False,
            "error": f"Доступ запрещён. Создавать директории можно только внутри песочницы: {SANDBOX_DIR}",
            "result": None,
        }

    try:
        os.makedirs(absolute_path)

        return {
            "success": True,
            "error": None,
            "result": f"Пустая директория успешно создана: {dir_path}",
        }

    except FileExistsError:
        return {
            "success": False,
            "error": f"Объект уже существует: {dir_path}",
            "result": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Произошла ошибка: {str(e)}",
            "result": None,
        }


touch_dir.tool_description = {
    "type": "function",
    "function": {
        "name": "touch_dir",
        "description": (
            "Создаёт новую пустую директорию (папку) по указанному пути.\n"
            "Используй, если пользователь просит «создай папку...», «сделай директорию...», «создай папку для...». "
            "Если родительских папок не существует, они будут созданы автоматически. "
            "Если папка с таким именем уже существует, вернёт ошибку.\n"
            "\n"
            "Параметры:\n"
            "- dir_path (обязательно): путь к новой директории ('logs', 'src/utils', '/home/user/data').\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает статус в поле 'success', текст ошибки в 'error' (если есть) "
            "и сообщение в 'result'. Если папка создана, 'success' будет True, а в 'result' — путь.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Если пользователь просит создать папку внутри другой папки, которой нет, функция создаст всю цепочку автоматически.\n"
            "2. Если папка уже существует, функция вернёт ошибку. В этом случае не пытайся создать её снова, "
            "а сообщи пользователю, что она уже есть."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "Путь к новой директории.",
                },
            },
            "required": ["dir_path"],
            "additionalProperties": False,
        },
    },
}
