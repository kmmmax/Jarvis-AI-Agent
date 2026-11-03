from __future__ import annotations
import os
import shutil


def delete_path(target_path: str = "") -> dict:

    if not target_path:
        return {"success": False, "error": "Не указан путь для файла", "result": None}

    absolute_target_path = os.path.realpath(target_path)
    root_items = os.listdir("/")
    home_dir = os.path.realpath(os.path.expanduser("~"))
    home_parent = os.path.dirname(home_dir)

    if not os.path.exists(absolute_target_path):
        return {
            "success": False,
            "error": f"Данный путь не существует: {absolute_target_path}",
            "result": None,
        }

    protected_paths_only = ["/", home_parent, home_dir]
    no_delete_inside_paths = [os.path.realpath(os.getcwd())] + [
        os.path.realpath(os.path.join("/", item))
        for item in root_items
        if os.path.realpath(os.path.join("/", item)) != home_parent
    ]

    if absolute_target_path in protected_paths_only:
        return {
            "success": False,
            "error": f"Удаление самого этого пути запрещено: {absolute_target_path}. Если это директория, удалять ее содержимое разрешено.",
            "result": None,
        }

    for protected_path in no_delete_inside_paths:
        if absolute_target_path == protected_path:
            return {
                "success": False,
                "error": f"Запрещено удалять защищённую директорию: {absolute_target_path}",
                "result": None,
            }
        if absolute_target_path.startswith(protected_path + os.sep):
            return {
                "success": False,
                "error": f"Запрещено удалять объект {absolute_target_path}, так как он находится внутри защищённой директории: {protected_path}",
                "result": None,
            }

    if os.path.islink(target_path):

        parent_dir = os.path.dirname(target_path)
        if not parent_dir:
            parent_dir = os.getcwd()

        if not os.access(parent_dir, os.W_OK):
            return {
                "success": False,
                "error": f"Нет прав на удаление: {target_path}. Родительская директория защищена: {parent_dir}",
                "result": None,
            }

        try:
            os.remove(target_path)
            return {
                "success": True,
                "error": None,
                "result": f"Симлинк удалён: {target_path}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка: {str(e)}",
                "result": None,
            }

    if os.path.isfile(absolute_target_path):
        parent_dir = os.path.dirname(absolute_target_path)
        if not os.access(parent_dir, os.W_OK):
            return {
                "success": False,
                "error": f"Нет прав на удаление: {absolute_target_path}. Родительская директория защищена: {parent_dir}",
                "result": None,
            }

        try:
            os.remove(absolute_target_path)
            return {
                "success": True,
                "error": None,
                "result": f"Файл удалён: {absolute_target_path}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка: {str(e)}",
                "result": None,
            }

    if os.path.isdir(absolute_target_path):
        parent_dir = os.path.dirname(absolute_target_path)
        if not os.access(parent_dir, os.W_OK):
            return {
                "success": False,
                "error": f"Нет прав на удаление: {absolute_target_path}. Родительская директория защищена: {parent_dir}",
                "result": None,
            }

        try:
            shutil.rmtree(absolute_target_path)
            return {
                "success": True,
                "error": None,
                "result": f"Директория удалена: {absolute_target_path}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка: {str(e)}",
                "result": None,
            }


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
            "- target_path (обязательно): путь к файлу, папке или ссылке ('old.txt', 'temp/', '/tmp/file').\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает статус в поле 'success', текст ошибки в 'error' (если есть) "
            "и сообщение в 'result'. Если удаление прошло успешно, 'success' будет True.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Если путь не существует, вернётся ошибка.\n"
            "2. Если нет прав на удаление (родительская директория защищена), вернётся ошибка.\n"
            "3. Никогда не пытайся удалить что-то без явной просьбы пользователя."
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
