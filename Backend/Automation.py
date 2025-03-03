from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from typing import List, Coroutine, Any

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

client = Groq(api_key = GroqAPIKey)

professional_responses = ["Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.", "I'm at your service for any additional questions or support you may need- don't hesitate to ask."]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello! I'm a {os.environ.get('Username', 'System')}, You're a content writer. You have to write content like letter."}]

def GoogleSearch(topic: str) -> bool:
    """Searches Google for the given topic."""
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"Error during Google search: {e}")
        return False

def Content(topic: str) -> bool:
    """Writes content based on the given topic using AI and opens it in Notepad."""

    def OpenNotepad(file: str) -> None:
        """Opens the given file in Notepad."""
        default_text_editor = 'notepad.exe'
        try:
            subprocess.Popen([default_text_editor, file])
        except Exception as e:
            print(f"Error opening Notepad: {e}")

    def ContentWriterAI(prompt: str) -> str:
        """Generates content using the Groq AI model."""
        messages.append({"role": "user", "content": prompt})

        try:
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages = SystemChatBot + messages,
                max_tokens=2048, # Corrected to max_tokens
                temperature=0.7,
                top_p=1,
                stream=False,  # Streaming can cause issues in this setup
                stop=None
            )
        except Exception as e:
            print(f"Error during Groq completion: {e}")
            return ""

        Answer = completion.choices[0].message.content if completion.choices else ""
            
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    topic = topic.replace("Content ", "")
    content_by_ai = ContentWriterAI(topic)

    filename = rf"Data\{topic.lower().replace(' ', '')}.txt"
    try:
        os.makedirs("Data", exist_ok=True) # Ensure Data dir exists
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content_by_ai)
        OpenNotepad(filename)
        return True
    except Exception as e:
        print(f"Error creating/writing file: {e}")
        return False

def YoutubeSearch(topic: str) -> bool:
    """Searches YouTube for the given topic."""
    try:
        url4search = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url4search)
        return True
    except Exception as e:
        print(f"Error opening YouTube in browser: {e}")
        return False

def PlayYoutube(query: str) -> bool:
    """Plays the given query on YouTube."""
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return False

def OpenApp(app: str, sess: requests.Session = None) -> bool:
    """Opens the specified application."""
    if sess is None:
        sess = requests.Session()  # Create session if it doesn't exist

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"Error opening application: {app}, trying Google Search App Links... Error: {e}")
        def extract_links(html: str) -> List[str]:
            """Extracts Google Search App Links."""
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link['href'] for link in links]
        
        def search_google(query: str) -> str:
            """Searches Google to find the link."""
            url = f"https://www.google.com/search?q={query}"
            headers = {
                'User-Agent': useragent
            }
            try:
                response = sess.get(url, headers=headers)

                if response.status_code == 200:
                    return response.text
                else:
                    print("Failed to retrieve search results.")
            except requests.exceptions.RequestException as e:
                 print(f"Error during Google search request: {e}")
                 return None
            return None

        html = search_google(app)

        if html:
            links = extract_links(html)  # Get all links
            if links:  # Check if the list is not empty
                link = links[0]
                webopen(link)
                return True
            else:
                #print("No Google Search App Links found.")
                return False
        else:
            return False


def CloseApp(app: str) -> bool:
    """Closes the specified application."""
    if "chrome" in app:
        print("Skipping closing Chrome via this method.")
        return False # Avoid closing chrome with this method.
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception as e:
            print(f"Error closing app {app}: {e}")
            return False
        
def System(command: str) -> bool:
    """Executes system commands related to volume control."""
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")
    
    command = command.lower() # Standardize command to lowercase

    try:
        if command == "mute":
            mute()
        elif command == "unmute":
            unmute()
        elif command == "volume up":
            volume_up()
        elif command == "volume down":
            volume_down()
        else:
            print(f"Unknown system command: {command}") # Handling unknown commands
            return False
        
        return True
    except Exception as e:
        print(f"Error executing system command {command}: {e}")
        return False

async def TranslateAndExecute(commands: List[str]) -> None:
    """Translates commands to function calls and executes them concurrently."""
    coroutines: List[Coroutine[Any, Any, bool]] = []

    for command in commands:
        command = command.lower() # Standardize command to lowercase

        if command.startswith("open "):
            app_name = command.removeprefix("open ").strip()
            if "it" in app_name or "file" in app_name:
                print(f"Skipping potentially ambiguous command: {command}")
                continue  # Skip "open it" or "open file"

            coroutines.append(asyncio.to_thread(OpenApp, app_name))

        elif command.startswith("general "):
            print(f"Skipping general command (not implemented): {command}")
            pass  # Placeholder for general commands

        elif command.startswith("realtime "):
            print(f"Skipping realtime command (not implemented): {command}")
            pass  # Placeholder for realtime commands

        elif command.startswith("close "):
            app_name = command.removeprefix("close ").strip()
            coroutines.append(asyncio.to_thread(CloseApp, app_name))

        elif command.startswith("play "):
            query = command.removeprefix("play ").strip()
            coroutines.append(asyncio.to_thread(PlayYoutube, query))

        elif command.startswith("content "):
            topic = command.removeprefix("content ").strip()
            coroutines.append(asyncio.to_thread(Content, topic))

        elif command.startswith("google search "):
            topic = command.removeprefix("google search ").strip()
            coroutines.append(asyncio.to_thread(GoogleSearch, topic))

        elif command.startswith("youtube search "):
            topic = command.removeprefix("youtube search ").strip()
            coroutines.append(asyncio.to_thread(YoutubeSearch, topic))

        elif command.startswith("system "):
            system_command = command.removeprefix("system ").strip()
            coroutines.append(asyncio.to_thread(System, system_command))

        else:
            print(f"No function Found. For {command}")

    if coroutines:
        results = await asyncio.gather(*coroutines, return_exceptions=True)  # Gather results and handle exceptions

        for result in results:
            if isinstance(result, Exception): # Handling the exception
                print(f"An error occurred during command execution: {result}")
            # Optionally, you could log the result to a file or database
            # if you want to track successes as well.

async def Automation(commands: List[str]) -> bool:
    """Executes a list of commands using TranslateAndExecute."""
    try:
        await TranslateAndExecute(commands)
        return True  # Indicate success, assuming no unhandled exceptions
    except Exception as e:
        print(f"Error during automation: {e}")
        return False  # Indicate failure


if __name__ == "__main__":
    # Example usage:
    command_list = [
        "open notepad",
        "content Write a short story about a cat",
        "close notepad",
        "play despacito",
        "system volume up",
        "system mute",
        "google search what is the weather today"
    ]
    asyncio.run(Automation(command_list))