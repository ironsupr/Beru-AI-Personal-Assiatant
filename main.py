from Frontend.GUI import (
    graphical_user_interface,
    set_assistant_status,
    show_text_to_screen,
    temp_directory_path,  # Assuming this is defined in Frontend.GUI
    set_microphone_status,
    answer_modifier,
    query_modifier,
    get_assistant_status,
    get_microphone_status
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
import asyncio
import time
import subprocess
import threading
import os
import json
import shlex
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f''' {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    chatlog_path = r"Data\ChatLog.json"
    if not os.path.exists(chatlog_path) or os.stat(chatlog_path).st_size < 5:
        logging.info("No Chatlog.json or empty file, initializing default chat.")
        try:
            with open(temp_directory_path("Database.data"), "w", encoding="utf-8") as db_file:
                db_file.write("")

            with open(temp_directory_path("Responses.data"), "w", encoding="utf-8") as resp_file:
                resp_file.write(DefaultMessage)
        except Exception as e:
            logging.error(f"Error in ShowDefaultChatIfNoChats: {e}", exc_info=True)


def ReadChatLogJson():
    chatlog_path = r"Data\ChatLog.json"
    try:
        with open(chatlog_path, "r", encoding="utf-8") as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        logging.warning(f"Chatlog file not found at {chatlog_path}")
        return []
    except json.JSONDecodeError:
        logging.warning("Invalid JSON in Chatlog.json, skipping.")
        return []
    except Exception as e:
        logging.exception(f"An unexpected error occurred while reading Chatlog.json: {e}")
        return []


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

    try:
        with open(temp_directory_path("Database.data"), "w", encoding="utf-8") as file:
            file.write(answer_modifier(formatted_chatlog))
    except Exception as e:
        logging.error(f"Error in ChatLogIntegration: {e}", exc_info=True)

def ShowChatsOnGUI():
    try:
        with open(temp_directory_path("Database.data"), "r", encoding="utf-8") as file:
            Data = file.read()
            if len(str(Data)) > 0:
                lines = Data.split("\n")
                result = "\n".join(lines)
            else:
                result = ""

        with open(temp_directory_path("Responses.data"), "w", encoding="utf-8") as file:
            file.write(result)

    except FileNotFoundError:
        logging.error("Database.data not found.", exc_info=True)
    except Exception as e:
        logging.exception(f"Error in ShowChatsOnGUI: {e}")


def IntialExecution():
    set_microphone_status("False")
    show_text_to_screen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

IntialExecution()

async def execute_automation(Decision): #Make it async
    await Automation(list(Decision))

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    set_assistant_status("Listening...")
    Query = SpeechRecognition()
    show_text_to_screen(f"{Username}: {Query}")
    set_assistant_status("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    R = any([i for i in Decision if i.startswith("realtime")])
    G = any([i for i in Decision if i.startswith("general")]) #Order matters
    mearged_guery = " and ".join(
        ["".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageExecution = True
            ImageGenerationQuery = str(queries)

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                asyncio.create_task(execute_automation(Decision))
                TaskExecution = True

    if ImageExecution == True:
        try:
            with open(r"Frontend\Files\ImageGenerationQuery.data", "w") as File:
                File.write(ImageGenerationQuery) # write the query
                logging.info(f"Wrote ImageGenerationQuery: {ImageGenerationQuery}")

            command = f'python "Backend\ImageGeneration.py"'
            args = shlex.split(command)
            p1 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocesses.append(p1)
            logging.info(f"Started ImageGeneration.py process with PID {p1.pid}")

        except FileNotFoundError:
            logging.error("ImageGeneration.py not found.", exc_info=True)
        except Exception as e:
            logging.exception("Error starting ImageGeneration.py: %s", e)

    if R or G:
        set_assistant_status("Searching...")
        Answer = RealtimeSearchEngine(query_modifier(mearged_guery))
        show_text_to_screen(f"{Assistantname}: {Answer}")
        set_assistant_status("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                set_assistant_status("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = Chatbot(query_modifier(QueryFinal))
                show_text_to_screen(f"{Assistantname}: {Answer}")
                set_assistant_status("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                set_assistant_status("Searching...")
                QueryFinal = Queries.replace("realtime", "")
                Answer = RealtimeSearchEngine(query_modifier(QueryFinal))
                show_text_to_screen(f"{Assistantname}: {Answer}")
                set_assistant_status("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = Chatbot(query_modifier(QueryFinal))
                show_text_to_screen(f"{Assistantname}: {Answer}")
                set_assistant_status("Answering...")
                TextToSpeech(Answer)
                set_assistant_status("Answering...")
                sys.exit(0)


def FirstThread():
    while True:
        CurrentStatus = get_microphone_status()
        if CurrentStatus == "True":
            MainExecution()
        else:
            set_assistant_status("Available...")
        time.sleep(0.1)

def SecondThread():
    graphical_user_interface()

if __name__ == "__main__":
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()