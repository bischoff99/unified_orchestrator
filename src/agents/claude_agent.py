"""Claude Desktop Agent - UI automation for Claude Desktop app"""
import time
import pyperclip
from config import CLAUDE_RESPONSE_DELAY
from src.utils.ui_control import focus_app, paste_and_send, select_all_and_copy

class ClaudeDesktopAgent:
    def __init__(self, name="Claude Desktop"):
        self.name = name

    def ask(self, prompt: str) -> str:
        """Send prompt to Claude Desktop and get response"""
        focus_app("Claude")
        paste_and_send(prompt)
        # Wait for Claude to compose the answer
        time.sleep(CLAUDE_RESPONSE_DELAY)
        select_all_and_copy()
        return pyperclip.paste().strip()
