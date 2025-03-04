import os
import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget,
                             QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

# Constants
ENV_FILE = ".env"
MIC_DATA_FILE = "Mic.data"
STATUS_DATA_FILE = "Status.data"
RESPONSES_DATA_FILE = "Responses.data"
JARVIS_GIF = "Jarvis.gif"
HOME_PNG = "Home.png"
CHATS_PNG = "Chats.png"
MINIMIZE_PNG = "Minimize2.png"
MAXIMIZE_PNG = "Maximize.png"
CLOSE_PNG = "Close.png"
MIC_ON_PNG = "Mic_on.png"
MIC_OFF_PNG = "Mic_off.png"

# Load environment variables
env_vars = dotenv_values(ENV_FILE)
ASSISTANT_NAME = env_vars.get("Assistantname", "Assistant")  # Default to "Assistant" if not found
CURRENT_DIR = os.getcwd()
TEMP_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Files")
GRAPHICS_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Graphics")

OLD_CHAT_MESSAGE = "" # Moved global variable inside the script.

def answer_modifier(answer):
    """Removes empty lines from the given answer."""
    return "\n".join(line for line in answer.splitlines() if line.strip())

def query_modifier(query):
    """Capitalizes the query and adds a question mark if it's a question."""
    query = query.lower().strip()
    if re.search(r"^(how|what|when|where|why|who|which|whom|whose|can you|what's|where's|how's)\b", query):
        query = query + "?" if query[-1] not in [".", "?", "!"] else query
    else:
        query = query + "." if query[-1] not in [".", "?", "!"] else query
    return query.capitalize()

def set_microphone_status(command):
    """Sets the microphone status."""
    file_path = os.path.join(TEMP_DIR_PATH, MIC_DATA_FILE)
    try:
        with open(file_path, "w", encoding="utf-8") as file:  # Corrected to "w"
            file.write(command)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

def get_microphone_status():
    """Gets the microphone status."""
    file_path = os.path.join(TEMP_DIR_PATH, MIC_DATA_FILE)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return "False"  # Or some default value
    except Exception as e:
        print(f"Error reading from {file_path}: {e}")
        return "False"

def set_assistant_status(status):
    """Sets the assistant status."""
    file_path = os.path.join(TEMP_DIR_PATH, STATUS_DATA_FILE)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(status)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

def get_assistant_status():
    """Gets the assistant status."""
    file_path = os.path.join(TEMP_DIR_PATH, STATUS_DATA_FILE)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading from {file_path}: {e}")
        return ""

def mic_button_initialized():
    """Sets the microphone status to initialized (False)."""
    set_microphone_status("False")

def mic_button_closed():
    """Sets the microphone status to closed (True)."""
    set_microphone_status("True") # Modified to correct the error.

def graphics_directory_path(filename):
    """Returns the full path to a graphics file."""
    return os.path.join(GRAPHICS_DIR_PATH, filename)

def temp_directory_path(filename):
    """Returns the full path to a temporary file."""
    return os.path.join(TEMP_DIR_PATH, filename)

def show_text_to_screen(text):
    """Writes text to the Responses.data file."""
    file_path = os.path.join(TEMP_DIR_PATH, RESPONSES_DATA_FILE)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        self.chat_timer = None  # Correct way to initialize.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(graphics_directory_path(JARVIS_GIF))
        max_gif_size_w = 480
        max_gif_size_h = 270
        movie.setScaledSize(QSize(max_gif_size_w, max_gif_size_h))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.chat_timer = QTimer(self)
        self.chat_timer.timeout.connect(self.load_messages)
        self.chat_timer.timeout.connect(self.speech_recog_text)
        self.chat_timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet('''QScrollBar:vertical{
                border:none;
                background: black;
                width:10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical{
                background:white;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical{
                background:black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px
            }

            QScrollBar::sub-line:vertical{
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
                border:none;
                background:none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBAr::sub-page:vertical{
                background:none;
            }
        ''')

    def load_messages(self):
        """Loads messages from the Responses.data file."""
        global OLD_CHAT_MESSAGE
        try:
            with open(temp_directory_path(RESPONSES_DATA_FILE), "r", encoding="utf-8") as file:
                messages = file.read().strip()
            if messages and messages != OLD_CHAT_MESSAGE:
                self.add_message(message=messages, color="White")
                OLD_CHAT_MESSAGE = messages
        except FileNotFoundError:
            print(f"File not found: {temp_directory_path(RESPONSES_DATA_FILE)}")
        except Exception as e:
            print(f"Error reading from {temp_directory_path(RESPONSES_DATA_FILE)}: {e}")

    def speech_recog_text(self):
        """Updates the label with the current speech recognition status."""
        status = get_assistant_status()
        self.label.setText(status)

    def load_icon(self, path, width=60, height=60):
        """Loads and sets an icon to the icon label."""
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        """Toggles the microphone icon and status."""
        if not hasattr(self, 'toggled'):
            self.toggled = True  # Initialize toggled if it doesn't exist

        if self.toggled:
            self.load_icon(graphics_directory_path(MIC_ON_PNG), 60, 60)  # Corrected image name.
            mic_button_initialized()
        else:
            self.load_icon(graphics_directory_path(MIC_OFF_PNG), 60, 60)  # Corrected image name.
            mic_button_closed()

        self.toggled = not self.toggled

    def add_message(self, message, color):
        """Adds a message to the chat text edit."""
        cursor = self.chat_text_edit.textCursor()
        format_ = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format_.setForeground(QColor(color))
        cursor.setCharFormat(format_)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout() # Changed name to a more meaningful name
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        movie = QMovie(graphics_directory_path(JARVIS_GIF))
        gif_label.setMovie(movie)
        max_gif_size_h = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_h))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        pixmap = QPixmap(graphics_directory_path(MIC_ON_PNG))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        if not hasattr(self, 'toggled'):
            self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.speech_recog_text)
        self.timer.start(5)

    def speech_recog_text(self):
        """Updates the label with the current speech recognition status."""
        status = get_assistant_status()
        self.label.setText(status)

    def load_icon(self, path, width=60, height=60):
        """Loads and sets an icon to the icon label."""
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None): # Toggle_icon will be called when it's mouse pressed.
        """Toggles the microphone icon and status."""
        if not hasattr(self, 'toggled'):
            self.toggled = True
        if self.toggled:
            self.load_icon(graphics_directory_path(MIC_ON_PNG), 60, 60)  # Corrected image name.
            mic_button_initialized()
        else:
            self.load_icon(graphics_directory_path(MIC_OFF_PNG), 60, 60)  # Corrected image name.
            mic_button_closed()

        self.toggled = not self.toggled

class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(graphics_directory_path(HOME_PNG))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; background-color:white; color: black")
        message_button = QPushButton()
        message_icon = QIcon(graphics_directory_path(CHATS_PNG))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; background-color:white; color: black")
        minimize_button = QPushButton()
        minimize_icon = QIcon(graphics_directory_path(MINIMIZE_PNG))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(graphics_directory_path(MAXIMIZE_PNG))
        self.restore_icon = QIcon(graphics_directory_path(MINIMIZE_PNG))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(graphics_directory_path(CLOSE_PNG))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {str(ASSISTANT_NAME).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(line_frame) # Added lineframe to the first element of the layout.
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def graphical_user_interface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    graphical_user_interface()