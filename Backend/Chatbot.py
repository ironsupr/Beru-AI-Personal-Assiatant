from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file.")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

CHAT_LOG_PATH = r"Data\ChatLog.json"

try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f)
except Exception as e:
    print(f"Error loading ChatLog.json: {e}")
    messages = []  # Initialize to empty list to avoid errors later


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\n Date: {date}\n Month: {month}\n Year: {year}\n Time: {hour} hours :{minute} minutes: {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def Chatbot(Query):
    global messages  # Access the global messages list

    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": f"{Query}"})

        # Construct the messages list correctly
        all_messages = SystemChatBot + messages
        all_messages.insert(1, {"role": "user", "content": RealtimeInformation()})  # Realtime info after system message

        completion = client.chat.completions.create(
            model = "llama3-70b-8192",
            messages=all_messages,  # Use the constructed list
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer = Answer)
    except Exception as e:
        print(f"Error in Chatbot function: {e}")
        # Reset messages list to avoid accumulating errors
        messages = []
        with open(CHAT_LOG_PATH, "w") as f:
            dump([], f, indent=4)
        return "An error occurred. Please try again."


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Questions: ")
        if user_input.lower() == "exit":
            break
        print(Chatbot(user_input))