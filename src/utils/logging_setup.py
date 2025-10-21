"""Logging configuration with Rich console support"""
from rich.console import Console
from rich.traceback import install
import logging

console = Console()
install(show_locals=False)

def setup_logging(level=logging.INFO):
    """Setup logging with rich formatting"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    return logging.getLogger("orchestrator")
