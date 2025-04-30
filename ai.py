import threading
import speech_recognition as sr
import pyttsx3
import os
import pyautogui
import subprocess
import webbrowser
import requests
from datetime import datetime
import wikipedia
import cv2
from deepface import DeepFace
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import pytesseract
import numpy as np

# Paths and API Keys
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
APP_FOLDER = r"E:\hanija\ai\app"
MISTRAL_API_KEY = "3irsvpMiDD0j2HxaXmOb8yuiWebL9kfz"
WEATHER_API_KEY = "bfe06b765fff06cb2e8e4c8570a5e38f"

# Initialize Engines
client = MistralClient(api_key=MISTRAL_API_KEY)
engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

# OCR Click
def click_text_on_screen(target_text):
    try:
        screenshot = pyautogui.screenshot()
        screenshot_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        data = pytesseract.image_to_data(screenshot_rgb, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            if target_text.lower() in text.lower():
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                pyautogui.click(x, y)
                return f"✅ Clicked on '{text}'."
        return f"❌ Couldn't find '{target_text}' on the screen."
    except Exception as e:
        return f"❌ OCR click error: {str(e)}"

# Listen Thread
def listen():
    def listen_thread():
        while True:
            try:
                with sr.Microphone() as source:
                    output_label.configure(text="🎤 Listening...")
                    window.update()
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)
                    output_label.configure(text="🧠 Processing...")
                    window.update()
                    try:
                        query = recognizer.recognize_google(audio)
                        input_text.delete(0, ctk.END)
                        input_text.insert(0, f"You said: {query}")
                        if query.lower() in ["exit", "stop"]:
                            speak("Shutting down. Goodbye!")
                            window.quit()
                            break
                        else:
                            response = process_command(query.lower())
                            output_label.configure(text=f"Response: {response}")
                            speak(response)
                    except sr.UnknownValueError:
                        output_label.configure(text="❌ Sorry, I didn't catch that.")
                    except sr.RequestError:
                        output_label.configure(text="🌐 Network error.")
            except Exception as e:
                output_label.configure(text="🎙️ Input error: " + str(e))
                break
    threading.Thread(target=listen_thread, daemon=True).start()

# Chat with Mistral
def chat_with_mistral(prompt):
    try:
        messages = [ChatMessage(role="user", content=prompt)]
        response = client.chat(model="mistral-tiny", messages=messages)
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        return "Error contacting Mistral: " + str(e)

# Features
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        if res.get("main"):
            temp = res['main']['temp']
            desc = res['weather'][0]['description']
            return f"The temperature in {city} is {temp}°C with {desc}."
        else:
            return "Couldn't find the weather for that city."
    except:
        return "Weather API failed."

def get_time():
    return datetime.now().strftime("It's %I:%M %p.")

def detect_emotion():
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            return "Camera error."
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return f"You look {result[0]['dominant_emotion']}."
    except Exception as e:
        return f"Emotion detection failed: {str(e)}"

# App Shortcuts
APP_SHORTCUTS = {
    "access": "Access.lnk",
    "angry ip scanner": "Angry IP Scanner.lnk",
    "anydesk": "AnyDesk.exe",
    "chatgpt": "ChatGPT.lnk",
    "cmd": "Command Prompt.lnk",
    "command prompt": "Command Prompt.lnk",
    "control panel": "Control Panel.lnk",
    "db browser": "DB Browser (SQLite).lnk",
    "excel": "Excel.lnk",
    "chrome": "Google Chrome.lnk",
    "edge": "Microsoft Edge.lnk",
    "onenote": "OneNote.lnk",
    "outlook": "Outlook (classic).lnk",
    "powerpoint": "PowerPoint.lnk",
    "run": "Run.lnk",
    "word": "Word.lnk",
}

def open_app(app_name):
    app_name = app_name.lower()
    if app_name in APP_SHORTCUTS:
        file_name = APP_SHORTCUTS[app_name]
        file_path = os.path.join(APP_FOLDER, file_name)
        if os.path.exists(file_path):
            subprocess.Popen(file_path, shell=True)
            print(f"Opening {app_name.title()}...")
            return True
    return False

def open_application(command):
    apps = {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "vs code": "C:\\Users\\YourUser\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe"
    }
    for key in apps:
        if key in command:
            subprocess.Popen(apps[key])
            speak(f"Opening {key}")
            return True
    return False

def search_web(query):
    if "youtube" in query:
        search = query.replace("search youtube for", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={search}")
    elif "google" in query or "search" in query:
        search = query.replace("search", "").replace("google", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search}")
    else:
        webbrowser.open("https://www.google.com")

def get_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except:
        return "Couldn't find info on that topic."

def show_help():
    return """
🗣 Try saying:
• "What’s the weather in [city]?"
• "Tell me about [topic]"
• "Open Chrome / Notepad"
• "Click [text on screen]"
• "How do I look?" (emotion detection)
• "What's the time?"
• "exit" or "stop" to quit
"""

# Command Processor
def process_command(command):
    if "open" in command:
        app_name = command.replace("open", "").strip()
        if open_app(app_name):
            return f"Opening {app_name.title()}..."
        elif open_application(command):
            return f"Opening {app_name.title()}..."
        else:
            return f"❌ App '{app_name}' not recognized."
    elif "weather" in command:
        return get_weather("Your City")  # Replace with your city or make dynamic
    elif "emotion" in command or "how do i look" in command:
        return detect_emotion()
    elif "time" in command:
        return get_time()
    elif "search" in command or "google" in command or "youtube" in command:
        search_web(command)
        return "Searching..."
    elif "wikipedia" in command:
        return get_summary(command.replace("wikipedia", "").strip())
    elif "help" in command:
        return show_help()
    elif "click" in command:
        target = command.replace("click", "").strip()
        return click_text_on_screen(target)
    elif command in ["exit", "quit", "stop"]:
        speak("Shutting down. Goodbye!")
        window.quit()
        return "Goodbye!"
    else:
        return chat_with_mistral(command)

# GUI Setup
window = ctk.CTk()
window.geometry("700x600")
window.title("JARVIS Assistant")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

gif_label = ctk.CTkLabel(window, text="")
gif_label.pack(pady=10)
gif_image = Image.open("giphy.gif")
frames = [ImageTk.PhotoImage(frame.copy().resize((300, 200))) for frame in ImageSequence.Iterator(gif_image)]

def animate(counter=0):
    gif_label.configure(image=frames[counter])
    window.after(100, animate, (counter + 1) % len(frames))

animate()

input_label = ctk.CTkLabel(window, text="Enter command or ask JARVIS:", font=("Arial", 14))
input_label.pack(pady=5)

input_text = ctk.CTkEntry(window, width=500, font=("Arial", 14))
input_text.pack(pady=5)

output_label = ctk.CTkLabel(window, text="", wraplength=600, justify="center", font=("Arial", 13))
output_label.pack(pady=10)

response_label = ctk.CTkLabel(window, text="", wraplength=600, justify="center", font=("Arial", 13))
response_label.pack(pady=10)

def update_response(resp):
    response_label.configure(text=f"Response: {resp}")

def on_submit():
    user_input = input_text.get().strip()
    if user_input:
        response = process_command(user_input)
        update_response(response)
        speak(response)

def start_voice_input():
    input_text.delete(0, ctk.END)
    listen()

submit_button = ctk.CTkButton(window, text="Submit", command=on_submit, font=("Arial", 14))
submit_button.pack(pady=10)

voice_button = ctk.CTkButton(window, text="Voice Input", command=start_voice_input, font=("Arial", 14))
voice_button.pack(pady=5)

def auto_start():
    speak("Hello, Sir! How can I help you today?")
    listen()

threading.Thread(target=auto_start).start()

window.mainloop()
