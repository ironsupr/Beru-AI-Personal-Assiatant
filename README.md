# 🤖 Beru AI Assistant

An advanced AI personal assistant featuring voice interaction, real-time search, and automation capabilities, built with Python.

## ✨ Features

- Voice Recognition & Text-to-Speech
- Natural Language Processing
- Real-time Web Search
- Task Automation
- Image Generation
- Multi-language Support
- Modern GUI Interface

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Windows OS

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ironsupr/Beru-AI-Personal-Assiatant.git
cd Beru-AI-Personal-Assiatant
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and configure your settings:
```bash
copy .env.example .env
```

## 🔑 Environment Variables

Required variables in `.env`:

```env
Username=YourName
Assistantname=Beru
GroqAPIKey=your-groq-api-key
CohereAPIKey=your-cohere-api-key
HuggingFaceAPIKey=your-huggingface-api-key
ASSISTANT_VOICE=en-US-EricNeural
input_language=en-US
```

## 🎯 Usage

Run the main script:
```bash
python main.py
```

### Voice Commands

- `"Open [app_name]"` - Launch applications
- `"Close [app_name]"` - Close applications
- `"Play [song_name]"` - Play music on YouTube
- `"System [command]"` - Execute system commands
- `"Content [topic]"` - Generate written content
- `"Google search [query]"` - Search Google
- `"Youtube search [query]"` - Search YouTube
- `"Generate image [prompt]"` - Create AI images

## 📁 Project Structure

```
Beru/
├── Backend/
│   ├── Automation.py
│   ├── Chatbot.py
│   ├── ImageGeneration.py
│   ├── Model.py
│   ├── RealtimeSearchEngine.py
│   ├── SpeechToText.py
│   └── TextToSpeech.py
├── Frontend/
│   ├── GUI.py
│   ├── Files/
│   └── Graphics/
├── Data/
├── main.py
└── requirements.txt
```

## 🔧 Dependencies

```text
python-dotenv
groq
AppOpener
pywhatkit
bs4
pillow
rich
requests
keyboard
cohere
googlesearch-python
selenium
mtranslate
pygame
edge-tts
PyQt5
webdriver-manager
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

- Keep your API keys secure and never commit them to version control
- Ensure your microphone permissions are enabled for voice commands
- Some features may require internet connectivity
