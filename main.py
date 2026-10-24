from __future__ import annotations
import silence_warnings
from tools.get_current_time import get_current_time, DEFAULT_TIMEZONE
from tools.get_weather import get_weather, DEFAULT_CITY
from tools.list_dir import list_dir
from tools.read_file_content import read_file_content
import ollama
from transformers import AutoTokenizer
from loguru import logger
import sys

sys.stderr = silence_warnings.original_stderr
logger.remove()
logger.add(sys.stderr)

MODEL = "qwen3.8:27b"
MODEL_ID = "Qwen/Qwen3.8-27B"
CHAT_LIMIT = 10
TOKEN_LIMIT = 8192
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)


with open("system_prompt.txt", mode="r", encoding="utf-8") as f:
    system_prompt = f.read()


def tokens_in_chat(messages: list) -> int:

    messages_str = ""
    for i in messages:

        role = i.get("role", "")
        tool_name = i.get("tool_name", "")
        content = i.get("content", "")
        tool_calls = i.get("tool_calls", "")

        if role:
            messages_str += role + "\n"

        if tool_name:
            messages_str += tool_name + "\n"

        if content:
            messages_str += content + "\n"

        if tool_calls:
            messages_str += str(tool_calls) + "\n"

    list_of_tokens = tokenizer.encode(messages_str)
    count_of_tokens = len(list_of_tokens)
    return count_of_tokens


def truncate_messages(messages: list) -> list:
    head_size = 1 if messages and messages[0].get("role") == "system" else 0

    while len(messages) > head_size + 1 and tokens_in_chat(messages) > TOKEN_LIMIT:
        # Ищем следующий 'user' (начало следующей группы)
        next_user_idx = next(
            (i for i in range(head_size + 1, len(messages)) if messages[i].get("role") == "user"),
            None
        )
        if next_user_idx is None:
            break
        # Вырезаем старую группу целиком
        messages = messages[:head_size] + messages[next_user_idx:]

    return messages

def start_chat_mode() -> None:
    messages = [{"role": "system", "content": system_prompt}]
    MAX_TOOL_ITERATIONS = 5 # Защита от зацикливания (максимум 5 вызовов подряд)

    print()
    while True:
        print("\033[0m", end="")
        user_message = str(input("💬 Введите ваш запрос: "))
        
        if user_message in ["exit", "stop", ""] or user_message.isspace():
            print("🚪 Диалог завершен")
            return

        messages.append({"role": "user", "content": user_message})

        # Обрезаем историю перед началом (если она уже была большая)
        messages = truncate_messages(messages)

        tool_iteration = 0
        
        # Цикл шагов модели (вместо вложенного while tool_calls)
        while tool_iteration < MAX_TOOL_ITERATIONS:
            tool_iteration += 1
            
            # ВАЖНО: Обрезаем историю ПЕРЕД каждым запросом к модели!
            # Если инструмент вернул 10 000 токенов, тут они отрежутся.
            messages = truncate_messages(messages)

            try:
                stream = ollama.chat(
                    model=MODEL,
                    messages=messages,
                    stream=True,
                    tools=[
                        get_current_time.tool_description,
                        get_weather.tool_description,
                        list_dir.tool_description,
                        read_file_content.tool_description,
                    ],
                )
            except Exception as e:
                logger.error(f"Программа прервана, ошибка - {e}")
                print("🚨 Произошла ошибка, извините!")
                break

            # Флаги для вывода
            flag_for_first_response = True
            is_thinking_printed = False
            final_message = ""
            tool_calls = []
            
            print("⏳ ", end="")

            # Читаем ответ модели
            for chunk in stream:
                if chunk.get("message", {}).get("tool_calls"):
                    tool_calls.extend(chunk.get("message", {}).get("tool_calls"))

                if (chunk.get("message", {}).get("thinking") != None) and (chunk.get("message", {}).get("thinking") != ""):
                    print("\033[90m", end="", flush=True)
                    print(chunk.get("message", {}).get("thinking"), end="", flush=True)
                    is_thinking_printed = True
                    
                elif (chunk.get("message", {}).get("content") != None) and (chunk.get("message", {}).get("content") != "") and flag_for_first_response:
                    print("\033[0m", end="", flush=True)
                    if is_thinking_printed:
                        print(f"\n🤖 Ответ от {MODEL}: ", end="", flush=True)
                    else:
                        print(f"\n🤖 Ответ от {MODEL}: ", end="", flush=True)
                    print(chunk.get("message", {}).get("content"), end="", flush=True)
                    flag_for_first_response = False
                    final_message += chunk.get("message", {}).get("content")
                    
                elif (chunk.get("message", {}).get("content") != None) and (chunk.get("message", {}).get("content") != "") and not flag_for_first_response:
                    print(chunk.get("message", {}).get("content"), end="", flush=True)
                    final_message += chunk.get("message", {}).get("content")
                    
                else:
                    continue

            # --- ЛОГИКА ПОСЛЕ ОКОНЧАНИЯ СТРИМА ---

            # Если модель не вызвала инструменты, это финальный ответ. Выходим.
            if not tool_calls:
                messages.append({"role": "assistant", "content": final_message})
                print(f"\n({tokens_in_chat(messages)}/{TOKEN_LIMIT})\n")
                break 

            # Если вызвала инструменты, добавляем ответ ассистента с вызовами
            messages.append({
                "role": "assistant",
                "content": final_message,
                "tool_calls": tool_calls,
            })

            # Выводим инфу о вызовах
            lines = [f"   {tc.function.name} с параметрами {tc.function.arguments}" for tc in tool_calls]
            print(f"\n\033[96m✨ Вызовы инструментов:\033[0m")
            print("\n".join(lines))

            # Выполняем инструменты и добавляем результаты в messages
            for tool_call in tool_calls:
                if tool_call.function.name == "get_current_time":
                    result = get_current_time(**tool_call.function.arguments)
                    messages.append({"role": "tool", "tool_name": "get_current_time", "content": str(result)})
                elif tool_call.function.name == "get_weather":
                    result = get_weather(**tool_call.function.arguments)
                    messages.append({"role": "tool", "tool_name": "get_weather", "content": str(result)})
                elif tool_call.function.name == "list_dir":
                    result = list_dir(**tool_call.function.arguments)
                    messages.append({"role": "tool", "tool_name": "list_dir", "content": str(result)})
                elif tool_call.function.name == "read_file_content":
                    result = read_file_content(**tool_call.function.arguments)
                    messages.append({"role": "tool", "tool_name": "read_file_content", "content": str(result)})

            # Цикл while tool_iteration идет на следующий круг.
            # На следующем круге truncate_messages обрежет старье, если инструмент вернул много данных.
            
        else:
            # Если цикл сделал 5 шагов, а модель всё еще требует инструменты
            print("\n🚫 Достигнут лимит вызовов инструментов.")
            messages.append({"role": "user", "content": "[СИСТЕМНОЕ] Достигнут лимит вызовов инструментов. Ответь пользователю текстом."})
            # Можно сделать еще один вызов, чтобы модель ответила текстом, но для простоты просто выходим
            break

def start_generate_mode() -> None:

    print()
    while True:

        user_message = str(input("💬 Введите ваш запрос: "))
        message_is_spaces = user_message.isspace()

        if (
            (user_message == "exit")
            or (user_message == "stop")
            or (user_message == "")
            or (message_is_spaces == True)
        ):
            print("🚪 Диалог завершен")
            return 0

        user_message = system_prompt + "\n" + user_message
        if tokens_in_chat([{"role": "user", "content": user_message}]) > TOKEN_LIMIT:
            print(f"🚫 Ваш запрос превысил лимит токенов! ({TOKEN_LIMIT})\n")
            continue

        try:
            stream = ollama.generate(model=MODEL, prompt=user_message, stream=True)
            flag_for_first_response = True
            print("⏳ ", end="")
            for chunk in stream:
                if (chunk.get("thinking") != None) and (chunk.get("thinking") != ""):
                    print("\033[90m", end="", flush=True)
                    print(chunk.get("thinking"), end="", flush=True)
                elif (
                    (chunk.get("response") != None)
                    and (chunk.get("response") != "")
                    and (flag_for_first_response == True)
                ):
                    print("\033[0m", end="", flush=True)
                    print("\n", end="", flush=True)
                    print(f"🤖 Ответ от {MODEL}: ", end="", flush=True)
                    print(chunk.get("response"), end="", flush=True)
                    flag_for_first_response = False
                elif (
                    (chunk.get("response") != None)
                    and (chunk.get("response") != "")
                    and (flag_for_first_response == False)
                ):
                    print(chunk.get("response"), end="", flush=True)
                else:
                    continue
            print("\n", end="")
        except Exception as e:
            logger.error(f"Программа прервана, ошибка - {e}")
            print("🚨 Произошла ошибка, извините!")
            return 0

        return 0


def main():

    print(
        "\033[91mJ\033[0m-\033[93mA\033[0m-\033[92mR\033[0m-\033[96mV\033[0m-\033[94mI\033[0m-\033[95mS\033[0m"
    )
    try:
        selected_mode = int(
            input(
                "ИИ-помощник для общения, ответов на вопросы и выполнения задач.\n"
                "Для выхода - введите stop, exit или сочетание клавиш Ctrl+C.\n\n"
                f"🧠 Текущая модель: {MODEL}\n"
                f"📊 Лимит токенов для нее: {TOKEN_LIMIT}\n"
                f"📚 Лимит истории собщений для режима Chat: {CHAT_LIMIT}\n"
                f"🌍 Дефолтная таймзона: {DEFAULT_TIMEZONE}\n"
                f"🏠 Дефолтный город для расчета погоды: {DEFAULT_CITY.capitalize()}\n\n"
                f"🚀 Доступные инструменты:\n"
                f"⏰ get_current_time — текущее время в любом часовом поясе.\n"
                f"🧭 get_weather — текущая погода и прогноз на сегодня.\n\n"
                "✅ Выберите режим взаимодействия с моделью.\n"
                "1) Chat - бесконечный цикл с сохранением истории (поддерживает инструменты)\n"
                "2) Generate - один запрос, один ответ, выход (без использования инструментов!)\n"
                "Введите цифру: "
            )
        )

    except ValueError:
        print("🚫 Вы ввели не цифру.")
        return 0

    if selected_mode == 1:
        start_chat_mode()
    elif selected_mode == 2:
        start_generate_mode()
    else:
        print("😟 Такого режима не существует.")
        return 0


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("\033[0m", end="\n")
        print("🚪 Прервано по KeyboardInterrupt")
