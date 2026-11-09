from __future__ import annotations
import os
import shutil


def delete_path(target_path: str = "") -> dict:

    if not target_path:
        return {"success": False, "error": "Не указан путь для файла", "result": None}

    if not os.path.lexists(target_path):
        return {
            "success": False,
            "error": f"Данный путь не существует: {target_path}",
            "result": None,
        }

    is_symlink = os.path.islink(target_path)

    if is_symlink:
        absolute_link = os.path.abspath(target_path)

        parent_dir = os.path.realpath(os.path.dirname(absolute_link))

        absolute_target_path = os.path.join(
            parent_dir,
            os.path.basename(absolute_link),
        )
    else:
        absolute_target_path = os.path.realpath(target_path)

    root_items = os.listdir("/")
    home_dir = os.path.realpath(os.path.expanduser("~"))
    home_parent = os.path.dirname(home_dir)

    protected_paths_only = ["/", home_parent, home_dir]
    no_delete_inside_paths = [os.path.realpath(os.getcwd())] + [
        os.path.realpath(os.path.join("/", item))
        for item in root_items
        if os.path.realpath(os.path.join("/", item)) != home_parent
    ]

    if is_symlink and os.path.dirname(absolute_target_path) == os.sep:
        return {
            "success": False,
            "error": f"Запрещено удалять симлинк из корневой директории: {target_path}",
            "result": None,
        }

    if absolute_target_path in protected_paths_only:
        if absolute_target_path == target_path:
            error_msg = f"Удаление самого этого пути запрещено: {target_path}"
        else:
            error_msg = f"Удаление самого этого пути запрещено: {target_path} (реальный путь: {absolute_target_path})"
        return {
            "success": False,
            "error": error_msg,
            "result": None,
        }

    for protected_path in no_delete_inside_paths:
        if absolute_target_path == protected_path:
            if absolute_target_path == target_path:
                error_msg = f"Запрещено удалять защищённый путь: {target_path}"
            else:
                error_msg = f"Запрещено удалять защищённый путь: {target_path} (реальный путь: {absolute_target_path})"
            return {
                "success": False,
                "error": error_msg,
                "result": None,
            }

        if absolute_target_path.startswith(protected_path + os.sep):
            if absolute_target_path == target_path:
                error_msg = f"Запрещено удалять объект {target_path}, так как он находится внутри защищённого пути: {protected_path}"
            else:
                error_msg = f"Запрещено удалять объект {target_path} (реальный путь: {absolute_target_path}), так как он находится внутри защищённого пути: {protected_path}"
            return {
                "success": False,
                "error": error_msg,
                "result": None,
            }

    if is_symlink:

        if not os.access(parent_dir, os.W_OK):
            if absolute_target_path == target_path:
                error_msg = f"Нет прав на удаление симлинка: {target_path}. Нет прав на запись в родительскую директорию: {parent_dir}"
            else:
                error_msg = f"Нет прав на удаление симлинка: {target_path} (реальный путь: {absolute_target_path}). Нет прав на запись в родительскую директорию: {parent_dir}"
            return {
                "success": False,
                "error": error_msg,
                "result": None,
            }

        try:
            os.remove(target_path)
            if absolute_target_path == target_path:
                result_msg = f"Симлинк удалён: {target_path}"
            else:
                result_msg = (
                    f"Симлинк удалён: {target_path} (реальный путь: {absolute_target_path})"
                )
            return {
                "success": True,
                "error": None,
                "result": result_msg,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка при удалении симлинка: {str(e)}",
                "result": None,
            }

    if os.path.isfile(absolute_target_path):
        parent_dir = os.path.dirname(absolute_target_path)
        if not os.access(parent_dir, os.W_OK):
            if absolute_target_path == target_path:
                error_msg = f"Нет прав на удаление файла: {target_path}. Нет прав на запись в родительскую директорию: {parent_dir}"
            else:
                error_msg = f"Нет прав на удаление файла: {target_path} (реальный путь: {absolute_target_path}). Нет прав на запись в родительскую директорию: {parent_dir}"
            return {
                "success": False,
                "error": error_msg,
                "result": None,
            }

        try:
            os.remove(absolute_target_path)
            if absolute_target_path == target_path:
                result_msg = f"Файл успешно удалён: {target_path}"
            else:
                result_msg = f"Файл успешно удалён: {target_path} (реальный путь: {absolute_target_path})"
            return {
                "success": True,
                "error": None,
                "result": result_msg,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка при удалении файла: {str(e)}",
                "result": None,
            }

    if os.path.isdir(absolute_target_path):
        parent_dir = os.path.dirname(absolute_target_path)
        if not os.access(parent_dir, os.W_OK):
            if absolute_target_path == target_path:
                error_msg = f"Нет прав на удаление директории: {target_path}. Нет прав на запись в родительскую директорию: {parent_dir}"
            else:
                error_msg = f"Нет прав на удаление директории: {target_path} (реальный путь: {absolute_target_path}). Нет прав на запись в родительскую директорию: {parent_dir}"
            return {
                "success": False,
                "error": error_msg,
                "result": None,
            }

        try:
            shutil.rmtree(absolute_target_path)
            if absolute_target_path == target_path:
                result_msg = f"Директория успешно удалена: {target_path}"
            else:
                result_msg = f"Директория успешно удалена: {target_path} (реальный путь: {absolute_target_path})"
            return {
                "success": True,
                "error": None,
                "result": result_msg,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Произошла ошибка при удалении директории: {str(e)}",
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
            "2. Если нет прав на запись в родительскую директорию, вернётся ошибка.\n"
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
