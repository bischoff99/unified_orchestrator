"""UI control utilities for macOS automation"""
import time
import subprocess
import pyautogui
import pyperclip
from config import CLAUDE_PASTE_DELAY, CLAUDE_COPY_DELAY

def focus_app(app_name="Claude"):
    """Focus application using AppleScript"""
    script = f'tell application "{app_name}" to activate'
    subprocess.run(["osascript", "-e", script], check=False)

def paste_and_send(text: str):
    """Paste text and send (press Enter)"""
    pyperclip.copy(text)
    time.sleep(CLAUDE_PASTE_DELAY)
    pyautogui.hotkey("command", "v")
    pyautogui.press("enter")

def select_all_and_copy():
    """Select all text and copy to clipboard"""
    time.sleep(CLAUDE_COPY_DELAY)
    pyautogui.hotkey("command", "a")
    pyautogui.hotkey("command", "c")
