"""LLM tool management for different backends"""
import os
from config import MODEL_BACKEND

def get_llm_tools():
    """Get appropriate LLM tools based on backend configuration"""
    # For now, return empty list as agents don't need custom tools
    # Tools can be added later as needed per agent
    return []
