from __future__ import annotations
import os


def list_dir(dir_path: str = ".", limit: int = 50) -> dict:

    if not os.path.exists(dir_path):
        return {
            "success": False,
            "error": f"Путь не найден: {dir_path}",
            "result": None,
        }
    if not os.path.isdir(dir_path):
        return {
            "success": False,
            "error": f"Это не директория: {dir_path}",
            "result": None,
        }

    try:
        items = os.listdir(dir_path)

        if not items:
            return {
                "success": True,
                "error": None,
                "result": f"Директория пуста: {dir_path}",
            }

        items.sort(
            key=lambda item_name: (
                not os.path.isdir(os.path.join(dir_path, item_name)),
                item_name.lower(),
            )
        )

        is_cutted = False
        total_items = len(items)
        if len(items) > limit:
            is_cutted = True
            difference = total_items - limit
            items = items[:limit]

        result = ""
        for item in items:
            if os.path.isdir(os.path.join(dir_path, item)):
                result += f"[DIR]   {item}\n"
            else:
                result += f"[FILE] {item}\n"

        result = result.rstrip("\n")
        if is_cutted == True:
            result += f"\n\n[ALERT] Показаны первые {limit} элементов из {total_items}. Скрыто: {difference}"

        return {"success": True, "error": None, "result": result}

    except PermissionError:
        return {
            "success": False,
            "error": f"Нет прав на чтение данных этой директории: {dir_path}",
            "result": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Произошла ошибка: {str(e)}",
            "result": None,
        }


list_dir.tool_description = {
    "type": "function",
    "function": {
        "name": "list_dir",
        "description": (
            "Возвращает список файлов и папок в указанной директории.\n"
            "Используй, если пользователь просит показать файлы/папки, узнать структуру проекта или посмотреть, что доступно для чтения/изменения.\n"
            "\n"
            "Параметры:\n"
            "- dir_path (опционально): путь к папке (например, '.', 'tools', '/home/user'). По умолчанию текущая директория.\n"
            "- limit (опционально): максимум элементов (от 1 до 200). По умолчанию 50. Передавай, если пользователь просит больше/меньше.\n"
            "\n"
            "Формат ответа:\n"
            "Функция возвращает готовый текст в поле 'result'. В нем строки уже размечены:\n"
            "- '[DIR]  ' — папка.\n"
            "- '[FILE] ' — файл.\n"
            "Если папка пуста или элементов больше limit (будет маркер [ALERT]), функция сообщит об этом.\n"
            "\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "1. Можешь написать короткую вступительную фразу (например, «Вот что находится в папке...:»).\n"
            "2. Сразу после нее ты ОБЯЗАН вставить текст из 'result' БЕЗ ИЗМЕНЕНИЙ. "
            "КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО убирать маркеры '[DIR]' и '[FILE]', менять их на свои категории ('**Папки:**'), переставлять элементы, объединять их в строку или удалять переносы. "
            "Текст должен быть скопирован ровно как пришел.\n"
            "3. Если есть [ALERT], просто оставь его в конце скопированного текста, ничего не сокращая."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": (
                        "Путь к директории. Можно относительный ('tools') или абсолютный ('/home/user'). "
                        "По умолчанию '.'."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Максимум элементов. По умолчанию 50. Минимум 1, максимум 200."
                    ),
                    "minimum": 1,
                    "maximum": 200
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}
