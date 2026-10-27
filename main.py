from __future__ import annotations
import silence_warnings
from tools.get_current_time import get_current_time, DEFAULT_TIMEZONE
from tools.get_weather import get_weather, DEFAULT_CITY, PROXIES
from tools.list_dir import list_dir
from tools.read_file_content import read_file_content
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
import ollama
from ollama import Client
from transformers import AutoTokenizer
from dotenv import load_dotenv
from loguru import logger
import base64
import os
import sys

sys.stderr = silence_warnings.original_stderr
logger.remove()
logger.add(sys.stderr)

load_dotenv()
host = os.getenv("OLLAMA_HOST")
user = os.getenv("OLLAMA_USER")
password = os.getenv("OLLAMA_PASSWORD")

if user and password:
    auth_string = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("utf-8")
    client = Client(host=host, headers={"Authorization": f"Basic {auth_string}"})
else:
    client = Client(host=host)


MODEL = "qwen3.5-9b-8k"
MODEL_ID = "Qwen/Qwen3.5-9B"
CHAT_LIMIT = 10
TOKEN_LIMIT = 8192
MAX_TOOL_ITERATIONS = 20

bindings = KeyBindings()


@bindings.add("c-c")
def _(event):
    raise KeyboardInterrupt


tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)


with open("system_prompt_chat.txt", mode="r", encoding="utf-8") as f:
    system_prompt_chat = f.read()
with open("system_prompt_generate.txt", mode="r", encoding="utf-8") as f:
    system_prompt_generate = f.read()


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


def truncate_messages(messages: list) -> tuple[list, bool]:

    is_critical_overflow = False

    while len(messages) > 2 and tokens_in_chat(messages) > TOKEN_LIMIT:
        user_indexes = []
        for i in range(len(messages)):
            if messages[i].get("role") == "user":
                user_indexes.append(i)

        if len(user_indexes) < 2:
            messages = [messages[0], messages[user_indexes[0]]]
            is_critical_overflow = True
            break

        second_user_index = user_indexes[1]
        messages = [messages[0]] + messages[second_user_index:]

    return messages, is_critical_overflow


def start_chat_mode() -> None:
    messages = [{"role": "system", "content": system_prompt_chat}]

    print()
    while True:
        print("\033[0m", end="")
        try:
            user_message = prompt(
                "💬 Введите ваш запрос: ", key_bindings=bindings, multiline=True
            )
        except KeyboardInterrupt:
            print("\033[0m🚪 Прервано по KeyboardInterrupt")
            return 0

        if user_message in ["exit", "stop", ""] or user_message.isspace():
            print("🚪 Диалог завершен")
            return 0

        user_tokens = tokens_in_chat([{"role": "user", "content": user_message}])
        system_tokens = tokens_in_chat([{"role": "system", "content": system_prompt_chat}])

        if user_tokens + system_tokens > TOKEN_LIMIT:
            print(
                f"\033[91m🚫 Ваш запрос слишком длинный! ({user_tokens} токенов). Пожалуйста, напишите короче.\033[0m\n"
            )
            continue

        messages.append({"role": "user", "content": user_message})

        is_clock_printed = False
        tool_iteration = 0

        while tool_iteration < MAX_TOOL_ITERATIONS:
            tool_iteration += 1

            messages, is_critical = truncate_messages(messages)
            if is_critical:
                print(
                    f"\n\033[91m🚨 Переполнение лимита токенов ({TOKEN_LIMIT})! История сброшена до вашего текущего запроса. Модель начинает размышления с нуля.\033[0m\n"
                )
                is_clock_printed = False

            try:
                stream = client.chat(
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
                print("\033[91m🚨 Произошла ошибка, извините!\033[0m\n")
                break

            flag_for_first_response = True
            is_thinking_printed = False
            final_message = ""
            tool_calls = []

            try:
                for chunk in stream:
                    if not is_clock_printed:
                        print("⏳ ", end="")
                        is_clock_printed = True

                    if chunk.get("message", {}).get("tool_calls"):
                        tool_calls.extend(chunk.get("message", {}).get("tool_calls"))

                    if (chunk.get("message", {}).get("thinking") != None) and (
                        chunk.get("message", {}).get("thinking") != ""
                    ):
                        print("\033[90m", end="", flush=True)
                        print(
                            chunk.get("message", {}).get("thinking"), end="", flush=True
                        )
                        is_thinking_printed = True

                    elif (
                        (chunk.get("message", {}).get("content") != None)
                        and (chunk.get("message", {}).get("content") != "")
                        and flag_for_first_response
                    ):
                        print("\033[0m", end="", flush=True)
                        if is_thinking_printed:
                            print(f"\n🤖 Ответ от {MODEL}: ", end="", flush=True)
                        else:
                            print(f"🤖 Ответ от {MODEL}: ", end="", flush=True)
                        print(
                            chunk.get("message", {}).get("content"), end="", flush=True
                        )
                        flag_for_first_response = False
                        final_message += chunk.get("message", {}).get("content")

                    elif (
                        (chunk.get("message", {}).get("content") != None)
                        and (chunk.get("message", {}).get("content") != "")
                        and not flag_for_first_response
                    ):
                        print(
                            chunk.get("message", {}).get("content"), end="", flush=True
                        )
                        final_message += chunk.get("message", {}).get("content")

                    else:
                        continue
            except KeyboardInterrupt:
                print("\n\033[0m🚪 Прервано по KeyboardInterrupt")
                return 0

            if not tool_calls:
                messages.append({"role": "assistant", "content": final_message})
                print(f"\n({tokens_in_chat(messages)}/{TOKEN_LIMIT})\n")
                break

            messages.append(
                {
                    "role": "assistant",
                    "content": final_message,
                    "tool_calls": tool_calls,
                }
            )

            lines = []
            for tool_call in tool_calls:
                lines.append(
                    f"   {tool_call.function.name} с параметрами {tool_call.function.arguments}"
                )

            print(f"\n\033[96m✨ Вызовы инструментов:\033[0m")
            print("\n".join(lines))

            for tool_call in tool_calls:
                if tool_call.function.name == "get_current_time":
                    result = get_current_time(**tool_call.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": "get_current_time",
                            "content": str(result),
                        }
                    )
                elif tool_call.function.name == "get_weather":
                    result = get_weather(**tool_call.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": "get_weather",
                            "content": str(result),
                        }
                    )
                elif tool_call.function.name == "list_dir":
                    result = list_dir(**tool_call.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": "list_dir",
                            "content": str(result),
                        }
                    )
                elif tool_call.function.name == "read_file_content":
                    result = read_file_content(**tool_call.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": "read_file_content",
                            "content": str(result),
                        }
                    )

        else:
            print(
                f"\033[91m🚫 Достигнут лимит вызовов инструментов! ({MAX_TOOL_ITERATIONS})\033[0m\n"
            )


def start_generate_mode() -> None:

    print()
    while True:
        try:
            user_message = prompt(
                "💬 Введите ваш запрос: ",
                key_bindings=bindings,
                multiline=True,
            )
        except KeyboardInterrupt:
            print("\033[0m🚪 Прервано по KeyboardInterrupt")
            return 0

        if user_message in ["exit", "stop", ""] or user_message.isspace():
            print("🚪 Диалог завершен")
            return 0

        full_message = system_prompt_generate + "\n" + user_message
        user_tokens = len(tokenizer.encode(user_message))

        if len(tokenizer.encode(full_message)) > TOKEN_LIMIT:
            print(
                f"\033[91m🚫 Ваш запрос слишком длинный! ({user_tokens} токенов). Пожалуйста, напишите короче.\033[0m\n"
            )
            continue

        try:
            stream = client.generate(model=MODEL, prompt=full_message, stream=True)
            flag_for_first_response = True
            is_clock_printed = False

            for chunk in stream:
                if not is_clock_printed:
                    print("⏳ ", end="")
                    is_clock_printed = True

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
        except KeyboardInterrupt:
            print("\n\033[0m🚪 Прервано по KeyboardInterrupt")
            return 0
        except Exception as e:
            logger.error(f"Программа прервана, ошибка - {e}")
            print("\033[91m🚨 Произошла ошибка, извините!\033[0m\n")


def main():

    print(
        "\033[91mJ\033[0m-\033[93mA\033[0m-\033[92mR\033[0m-\033[96mV\033[0m-\033[94mI\033[0m-\033[95mS\033[0m"
    )
    try:
        selected_mode = int(
            prompt(
                "ИИ-помощник для общения, ответов на вопросы и выполнения задач.\n"
                "Для выхода - введите stop, exit или сочетание клавиш Ctrl+C.\n\n"
                f"🧠 Текущая модель: {MODEL}\n"
                f"📊 Лимит токенов для нее: {TOKEN_LIMIT}\n"
                f"📋 Токенов в системном промпте для режима Chat: {len(tokenizer.encode(system_prompt_chat))}\n"
                f"📋 Токенов в системном промпте для режима Generate: {len(tokenizer.encode(system_prompt_generate))}\n"
                f"🔄 Лимит вызовов функций за один запрос: {MAX_TOOL_ITERATIONS}\n"
                f"🌐 Установленные прокси: {', '.join(PROXIES.values()) if PROXIES else 'нет'}\n"
                f"🌍 Дефолтная таймзона: {DEFAULT_TIMEZONE}\n"
                f"🏠 Дефолтный город для расчета погоды: {DEFAULT_CITY.capitalize()}\n\n"
                "🚀 Доступные инструменты:\n"
                "⏰ get_current_time — текущее время в любом часовом поясе.\n"
                "🧭 get_weather — текущая погода и прогноз на сегодня.\n\n"
                "📌 Enter — перенос строки.\n"
                "📌 Esc, затем Enter — отправить запрос.\n\n"
                "✅ Выберите режим взаимодействия с моделью.\n"
                "1) Chat - бесконечный цикл с сохранением истории (поддерживает инструменты)\n"
                "2) Generate - один запрос, один ответ, выход (без использования инструментов!)\n"
                "Введите цифру: ",
                key_bindings=bindings,
            )
        )
    except KeyboardInterrupt:
        print("\033[0m🚪 Прервано по KeyboardInterrupt")
        return 0
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
    main()
