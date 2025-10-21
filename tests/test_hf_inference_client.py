"""Tests for HuggingFace Pro inference client."""

import json
import os
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, settings

from src.utils.hf_inference_client import HFProClient


@pytest.fixture
def mock_hf_token(monkeypatch):
    """Set mock HF token in environment."""
    monkeypatch.setenv("HF_TOKEN", "hf_test_token_12345")


@pytest.fixture
def client(mock_hf_token, tmp_path):
    """Create HF Pro client with disabled MCP components for testing."""
    return HFProClient(
        model_id="test-model/llama",
        enable_cost_tracking=False,  # Disable for isolated testing
        enable_safety_checks=False,
    )


class TestHFProClient:
    """Test suite for HF Pro inference client."""

    def test_initialization_with_token(self, mock_hf_token):
        """Test client initializes with HF token."""
        client = HFProClient(
            model_id="test-model",
            enable_cost_tracking=False,
            enable_safety_checks=False,
        )
        
        assert client.model_id == "test-model"
        assert client.hf_token == "hf_test_token_12345"
        assert "Authorization" in client.headers

    def test_initialization_without_token(self, monkeypatch):
        """Test initialization fails without HF token."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        
        with pytest.raises(ValueError, match="HF_TOKEN must be provided"):
            HFProClient(model_id="test-model", hf_token=None)

    @patch('httpx.post')
    def test_generate_success(self, mock_post, client):
        """Test successful generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Test output"}]
        mock_post.return_value = mock_response
        
        result = client.generate(
            prompt="Test prompt",
            max_tokens=50,
            check_budget=False,
        )
        
        assert result["status"] == "success"
        assert result["text"] == "Test output"
        assert "latency_ms" in result
        assert "tokens_used" in result
        assert result["tokens_used"] > 0

    @patch('httpx.post')
    def test_generate_http_error(self, mock_post, client):
        """Test handling of HTTP errors."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        result = client.generate(prompt="Test", check_budget=False)
        
        assert result["status"] == "error"
        assert "error" in result
        assert "500" in result["error"]

    @patch('httpx.post')
    def test_generate_rate_limit_retry(self, mock_post, client):
        """Test retry on rate limiting."""
        # Mock rate limit then success
        mock_response_limit = Mock()
        mock_response_limit.status_code = 429
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = [{"generated_text": "Success"}]
        
        mock_post.side_effect = [mock_response_limit, mock_response_success]
        
        result = client.generate(prompt="Test", check_budget=False)
        
        assert result["status"] == "success"
        assert result["attempt"] == 2  # Took 2 attempts

    @patch('httpx.post')
    def test_generate_model_loading_retry(self, mock_post, client):
        """Test retry when model is loading."""
        # Mock 503 then success
        mock_response_loading = Mock()
        mock_response_loading.status_code = 503
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = [{"generated_text": "Loaded"}]
        
        mock_post.side_effect = [mock_response_loading, mock_response_success]
        
        result = client.generate(prompt="Test", check_budget=False)
        
        assert result["status"] == "success"
        assert result["attempt"] == 2

    @patch('httpx.post')
    def test_generate_max_retries_exceeded(self, mock_post, client):
        """Test max retries behavior."""
        # Always return 503
        mock_response = Mock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response
        
        result = client.generate(prompt="Test", check_budget=False)
        
        assert result["status"] == "error"
        assert "retries" in result["error"].lower() or result["status"] == "error"

    def test_extract_text_from_list(self, client):
        """Test text extraction from list response."""
        response = [{"generated_text": "Test output"}]
        text = client._extract_text(response)
        
        assert text == "Test output"

    def test_extract_text_from_dict(self, client):
        """Test text extraction from dict response."""
        response = {"generated_text": "Test output"}
        text = client._extract_text(response)
        
        assert text == "Test output"

    def test_extract_text_fallback(self, client):
        """Test text extraction fallback."""
        response = {"unknown_field": "value"}
        text = client._extract_text(response)
        
        assert isinstance(text, str)

    def test_estimate_tokens(self, client):
        """Test token estimation."""
        text = "This is a test sentence."
        tokens = client._estimate_tokens(text)
        
        assert tokens > 0
        assert tokens == len(text) // 4

    def test_format_chat_prompt(self, client):
        """Test chat prompt formatting."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        
        prompt = client._format_chat_prompt(messages)
        
        assert "System:" in prompt
        assert "User:" in prompt
        assert "Assistant:" in prompt
        assert prompt.count("User:") == 2

    def test_chat_wrapper(self, client):
        """Test chat method wraps generate correctly."""
        with patch.object(client, 'generate') as mock_generate:
            mock_generate.return_value = {"status": "success"}
            
            messages = [{"role": "user", "content": "Test"}]
            result = client.chat(messages, max_tokens=50)
            
            assert mock_generate.called
            assert result["status"] == "success"

    def test_repr(self, client):
        """Test string representation."""
        repr_str = repr(client)
        
        assert "HFProClient" in repr_str
        assert "test-model" in repr_str


class TestHFProClientIntegration:
    """Integration tests with MCP components enabled."""

    @patch('httpx.post')
    def test_with_cost_tracking(self, mock_post, mock_hf_token, tmp_path):
        """Test client with cost tracking enabled."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Output"}]
        mock_post.return_value = mock_response
        
        client = HFProClient(
            model_id="test-model",
            enable_cost_tracking=True,
            enable_safety_checks=False,
        )
        client.cost_monitor.cache_dir = tmp_path  # Use temp cache
        
        result = client.generate("Test", check_budget=False)
        
        assert result["status"] == "success"
        # Cost monitor should have recorded this
        assert len(client.cost_monitor.usage_log) > 0

    @patch('httpx.post')
    def test_budget_check_prevents_request(self, mock_post, mock_hf_token, tmp_path):
        """Test budget check prevents request when exceeded."""
        client = HFProClient(
            model_id="test-model",
            enable_cost_tracking=True,
            enable_safety_checks=False,
        )
        client.cost_monitor.cache_dir = tmp_path
        client.cost_monitor.budget_daily = 1.0  # Low budget
        
        # Exceed budget
        client.cost_monitor.record_inference("test", 100000, 50.0, True)
        
        # Should prevent request
        result = client.generate("Test", check_budget=True)
        
        assert result["status"] == "budget_exceeded"
        assert result["fallback_recommended"] is True
        assert not mock_post.called  # Should not make HTTP request


class TestPropertyBased:
    """Property-based tests using hypothesis."""

    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=50, deadline=None)
    def test_format_chat_various_inputs(self, text):
        """Property test: Chat formatting handles any text."""
        client = HFProClient(
            model_id="test",
            hf_token="test_token",
            enable_cost_tracking=False,
            enable_safety_checks=False,
        )
        
        messages = [{"role": "user", "content": text}]
        prompt = client._format_chat_prompt(messages)
        
        # Should always return string
        assert isinstance(prompt, str)
        # Should contain user message
        assert "User:" in prompt

    @given(st.integers(min_value=1, max_value=100000))
    def test_estimate_tokens_various_counts(self, token_count):
        """Property test: Token estimation handles any count."""
        client = HFProClient(
            model_id="test",
            hf_token="test_token",
            enable_cost_tracking=False,
            enable_safety_checks=False,
        )
        
        # Create text of approximate token length
        text = "test " * token_count
        estimated = client._estimate_tokens(text)
        
        # Should always return positive integer
        assert estimated > 0
        assert isinstance(estimated, int)

    @given(st.floats(min_value=0.1, max_value=2.0))
    def test_temperature_parameter(self, temperature):
        """Property test: Temperature parameter handled correctly."""
        # Just verify it doesn't crash with various temperatures
        client = HFProClient(
            model_id="test",
            hf_token="test_token",
            enable_cost_tracking=False,
            enable_safety_checks=False,
        )
        
        # Mock the actual HTTP call
        with patch('httpx.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "OK"}]
            mock_post.return_value = mock_response
            
            result = client.generate(
                "Test",
                temperature=temperature,
                check_budget=False,
            )
            
            # Should succeed with any valid temperature
            assert result["status"] == "success"

