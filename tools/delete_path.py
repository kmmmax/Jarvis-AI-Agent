from __future__ import annotations
import os
import shutil
from config import SANDBOX_DIR


def delete_path(target_path: str = "") -> dict:

    if not target_path:
        return {"success": False, "error": "Не указан путь для файла", "result": None}

    absolute_target_path = os.path.realpath(target_path)

    if not absolute_target_path.startswith(SANDBOX_DIR + os.sep):
        return {
            "success": False,
            "error": f"Доступ запрещён. Удалять можно только внутри песочницы: {SANDBOX_DIR}",
            "result": None,
        }

    if not os.path.lexists(target_path):
        return {
            "success": False,
            "error": f"Данный путь не существует: {target_path}",
            "result": None,
        }

    try:
        if os.path.islink(target_path):
            os.remove(target_path)
            return {"success": True, "error": None, "result": f"Симлинк удалён: {target_path}"}
        elif os.path.isfile(absolute_target_path):
            os.remove(absolute_target_path)
            return {"success": True, "error": None, "result": f"Файл удалён: {target_path}"}
        elif os.path.isdir(absolute_target_path):
            shutil.rmtree(absolute_target_path)
            return {"success": True, "error": None, "result": f"Директория удалена: {target_path}"}
    except Exception as e:
        return {"success": False, "error": f"Произошла ошибка при удалении: {str(e)}", "result": None}


delete_path.tool_description = {
    "type": "function",
    "function": {
        "name": "delete_path",
        "description": (
            "Удаляет файл, папку или символическую ссылку по указанному пути.\n"
            "Используй, если пользователь просит «удали файл...», «удали папку...», «сотри...». "
            "Удаление папок происходит рекурсивно (со всем содержимым).\n"
            "\n"
            "Параметры:\n"
            "- target_path (обязательно): путь к файлу, папке или ссылке.\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает статус в поле 'success', текст ошибки в 'error' (если есть) "
            "и сообщение в 'result'. Если удаление прошло успешно, 'success' будет True.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Если путь не существует или находится вне песочницы, вернётся ошибка.\n"
            "2. Никогда не пытайся удалить что-то без явной просьбы пользователя."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target_path": {
                    "type": "string",
                    "description": "Путь к файлу, папке или символической ссылке.",
                },
            },
            "required": ["target_path"],
            "additionalProperties": False,
        },
    },
}