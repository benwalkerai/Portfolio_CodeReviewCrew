import ast
from dataclasses import dataclass
from crewai.tools import BaseTool
from pydantic import Field

@dataclass
class FucntionMetrics:
    name: str
    line: int
    length: int
    arg_count: int
    nesting_depth: int
    has_docstring: bool

class ASTAnalyserTool(BaseTool):
    name: str = "ast_analyser"
    description: str = (
        "Analyses Python source code and returns complexity metrics:"
        "function lengths, argument counts, nesting depth and docstring coverage"
    )
    source_code: str = Field(description="Python source code to analyse")
    filename: str = Field(default="<unknown>", description="Filename for reporting")

    def _run(self) -> dict | None:
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError as e:
            return {"error": f"Syntax error in {self.filename}: {e}"}
        
        functions = []
        classes = []
        total_lines = len(self.source_code.splitlines())

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._analyse_function(node))
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "method_count": sum(1 for child in node.body
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ),"has_docstring": self._has_docstring(node),
                })

        long_functions = [f for f in functions if f["length"] > 50]
        missing_docstrings = [f for f in functions if not f["has_docstring"]]
        deeply_nested = [f for f in functions if f["nesting_depth"] >3]
        return {
            "filename": self.filename,
            "total_lines": total_lines,
            "function_count": len(functions),
            "class_count": len(classes),
            "functions": functions,
            "classes": classes,
            "warnings": {
                "long_functions": long_functions,
                "missing_docstrings": missing_docstrings,
                "deep_nested": deeply_nested,
            },
        }

    def _analyse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
        end_line = getattr(node, "end_lineno", node.lineno)
        return {
            "name": node.name, 
            "line": node.lineno,
            "length": end_line - node.lineno +1,
            "arg-count": len(node.args.args),
            "nesting_depth": self._max_nesting(node),
            "has_docstring": self._has_docstring(node),
        }
    
    def _has_docstring(self, node:ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> bool:
        if not node.body:
            return False
        first = node.body[0]
        return (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        )
    
    def _max_nesting(self, node: ast.AST, depth: int = 0) -> int:
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                max_depth = max(max_depth, self._max_nesting(child, depth + 1))
            else:
                max_depth = max(max_depth, self._max_nesting(child, depth))
        return max_depth