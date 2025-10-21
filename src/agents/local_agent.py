"""Local Agent - Ollama-based local LLM agent"""
import subprocess

class LocalAgent:
    def __init__(self, model: str):
        self.model = model

    def ask(self, prompt: str) -> str:
        """Query local Ollama model"""
        cmd = ["ollama", "run", self.model, prompt]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.stdout.strip()
