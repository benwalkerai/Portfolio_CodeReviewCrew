"""Tests for crew parsing logic."""

import json
from src.crew import _extract_json, _build_context


class TestExtractJson:

    def test_plain_json(self):
        text = '{"agent_name": "Test", "score": 85}'
        result = _extract_json(text)
        assert result is not None
        assert result["score"] == 85

    def test_json_in_code_fence(self):
        text = 'Here is my analysis:\n```json\n{"agent_name": "Test", "score": 90}\n```'
        result = _extract_json(text)
        assert result is not None
        assert result["score"] == 90

    def test_json_with_surrounding_text(self):
        text = 'My review:\n{"agent_name": "Test", "score": 70}\nEnd of review.'
        result = _extract_json(text)
        assert result is not None
        assert result["score"] == 70

    def test_invalid_text(self):
        result = _extract_json("No JSON here at all")
        assert result is None

    def test_empty_string(self):
        result = _extract_json("")
        assert result is None


class TestBuildContext:

    def test_basic_context(self):
        files = {
            "app.py": "print('hello')",
            "utils.py": "x = 1",
        }
        result = _build_context(files)
        assert "app.py" in result
        assert "utils.py" in result
        assert "print('hello')" in result

    def test_truncation(self):
        files = {
            f"file_{i}.py": "x" * 1000
            for i in range(100)
        }
        result = _build_context(files, max_chars=5000)
        assert "TRUNCATED" in result

    def test_empty_files(self):
        result = _build_context({})
        assert result == ""
