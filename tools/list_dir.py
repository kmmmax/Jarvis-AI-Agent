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
            "\n"
            "КОГДА ИСПОЛЬЗОВАТЬ:\n"
            "- Пользователь просит «покажи файлы в папке», «что находится в директории», «посмотри, что тут есть».\n"
            "- Пользователь хочет узнать структуру проекта или папки.\n"
            "- Нужно понять, какие файлы доступны для чтения или изменения.\n"
            "\n"
            "АРГУМЕНТЫ:\n"
            "- dir_path (опционально): путь к директории (например, '.', '/home/user/documents', 'tools').\n"
            "  Если не указан, используется текущая директория ('.').\n"
            "- limit (опционально): максимальное количество элементов для вывода (от 1 до 200). "
            "По умолчанию 50. Если пользователь просит показать больше или меньше, передай это значение в параметре.\n"
            "\n"
            "ФОРМАТ ОТВЕТА:\n"
            "Функция возвращает готовый отформатированный текст в поле 'result'. "
            "В этом тексте каждая строка уже начинается с маркера:\n"
            "- '[DIR]  ' — если это папка.\n"
            "- '[FILE] ' — если это файл.\n"
            "Если папка пуста — функция сообщит об этом.\n"
            "Если элементов больше, чем указано в limit, в конце будет строка [ALERT].\n"
            "\n"
            "ПРАВИЛА ОТВЕТА ПОЛЬЗОВАТЕЛЮ:\n"
            "1. Ты можешь написать короткую вступительную фразу (например, «Вот что находится в папке ...:»).\n"
            "2. Сразу после вступительной фразы ты ОБЯЗАН вставить поле 'result' БЕЗ ИЗМЕНЕНИЙ. "
            "КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО убирать маркеры '[DIR]' и '[FILE]', менять их на свои категории ('**Папки:**', '**Файлы:**'), переставлять элементы, объединять их в одну строку или удалять пустые строки. "
            "Текст из 'result' должен быть скопирован ровно в том виде, в котором он пришел (сохраняя все переносы строк).\n"
            "3. Если в ответе есть [ALERT], не пытайся ничего сокращать, просто оставь его в конце скопированного текста."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": (
                        "Путь к директории для просмотра. "
                        "Можно использовать относительные пути (например, 'tools') или абсолютные (например, '/home/user'). "
                        "По умолчанию '.' (текущая директория)."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": (
                        "Максимальное количество элементов для вывода. "
                        "По умолчанию 50. Минимум 1, максимум 200."
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
