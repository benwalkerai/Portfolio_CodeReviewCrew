"""Tests for custom CrewAI tools."""

import os
import tempfile
from pathlib import Path

from src.tools.file_reader import FileReaderTool
from src.tools.ast_analyser import ASTAnalyserTool


class TestFileReader:

    def test_reads_python_files(self, tmp_path):
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("x = 1")

        tool = FileReaderTool(repo_path=str(tmp_path))
        result = tool._run()

        assert len(result) == 2
        assert "app.py" in result
        assert "print('hello')" in result["app.py"]

    def test_ignores_unsupported_extensions(self, tmp_path):
        (tmp_path / "app.py").write_text("code")
        (tmp_path / "image.png").write_bytes(b"\x89PNG")

        tool = FileReaderTool(repo_path=str(tmp_path))
        result = tool._run()

        assert len(result) == 1
        assert "image.png" not in result

    def test_ignores_pycache(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-312.pyc").write_bytes(b"bytecode")
        (tmp_path / "app.py").write_text("code")

        tool = FileReaderTool(repo_path=str(tmp_path))
        result = tool._run()

        assert len(result) == 1

    def test_skips_large_files(self, tmp_path):
        (tmp_path / "big.py").write_text("x" * 200_000)
        (tmp_path / "small.py").write_text("y = 1")

        tool = FileReaderTool(repo_path=str(tmp_path))
        result = tool._run()

        assert result["big.py"] == "[FILE TOO LARGE - SKIPPED]"
        assert result["small.py"] == "y = 1"

    def test_empty_directory(self, tmp_path):
        tool = FileReaderTool(repo_path=str(tmp_path))
        result = tool._run()
        assert result == {}


class TestASTAnalyser:

    def test_basic_function(self):
        code = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello {name}"
'''
        tool = ASTAnalyserTool(source_code=code, filename="test.py")
        result = tool._run()
        assert result is not None
        assert result["function_count"] == 1
        assert result["functions"][0]["name"] == "hello"
        assert result["functions"][0]["has_docstring"] is True
        assert result["functions"][0]["arg_count"] == 1

    def test_missing_docstring(self):
        code = '''
def add(a, b):
    return a + b
'''
        tool = ASTAnalyserTool(source_code=code, filename="test.py")
        result = tool._run()
        assert result is not None
        assert result["functions"][0]["has_docstring"] is False
        assert len(result["warnings"]["missing_docstrings"]) == 1
        

    def test_class_detection(self):
        code = '''
class MyClass:
    """A class."""
    def method_one(self):
        pass
    def method_two(self):
        pass
'''
        tool = ASTAnalyserTool(source_code=code, filename="test.py")
        result = tool._run()
        assert result is not None
        assert result["class_count"] == 1
        assert result["classes"][0]["method_count"] == 2
        assert result["classes"][0]["has_docstring"] is True
        

    def test_syntax_error(self):
        tool = ASTAnalyserTool(source_code="def broken(", filename="bad.py")
        result = tool._run()

        assert result is not None

    def test_nesting_depth(self):
        code = '''
def deep():
    if True:
        for i in range(10):
            if i > 5:
                while True:
                    break
'''
        tool = ASTAnalyserTool(source_code=code, filename="test.py")
        result = tool._run()
        assert result is not None
        assert result["functions"][0]["nesting_depth"] >= 3
        assert len(result["warnings"]["deeply_nested"]) == 1
        

    def test_long_function_warning(self):
        lines = ["def long_func():"] + ["    x = 1"] * 55
        code = "\n".join(lines)

        tool = ASTAnalyserTool(source_code=code, filename="test.py")
        result = tool._run()
        assert result is not None
        assert len(result["warnings"]["long_functions"]) == 1
        
