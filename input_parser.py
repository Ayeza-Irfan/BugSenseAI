import re
import os

class InputParser:
    LANG_HINTS = {
        "python": [r"def ", r"import ", r"print\("],
        "java":   [r"public class", r"System\.out"],
        # Check C++ before C, looking for specific C++ markers
        "cpp":    [r"#include <iostream>", r"std::cout", r"std::vector", r"namespace "],
        # If it didn't match C++, but has standard C markers, call it C
        "c":      [r"#include <stdio\.h>", r"printf\("],
    }
    
    EXTENSIONS = {
        ".py": "python",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
    }
    
    MAX_LINES = 2000  # Increased scope limit for modern LLM context windows

    def detect_language(self, code: str, filename: str = "") -> str:
        # 1. Check file extension first (much more reliable)
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in self.EXTENSIONS:
                return self.EXTENSIONS[ext]
                
        # 2. Fall back to regex if no filename/extension is provided
        for lang, patterns in self.LANG_HINTS.items():
            if any(re.search(p, code) for p in patterns):
                return lang
        return "unknown"

    def parse_single(self, code: str, error: str = "", filename: str = "") -> dict:
        lines = code.strip().splitlines()
        if len(lines) > self.MAX_LINES:
            print(f"[warn] Truncated {filename or 'snippet'} to {self.MAX_LINES} lines.")
            lines = lines[:self.MAX_LINES]
            lines.append(f"\n... [{filename or 'Code'} truncated for length] ...")
            
        clean_code = "\n".join(lines)
        return {
            "filename": filename or "snippet",
            "code": clean_code,
            "error": error,
            "language": self.detect_language(clean_code, filename),
            "lines": len(lines),
        }

    def parse_multiple(self, files_data: list[dict], error: str = "") -> dict:
        """Combines multiple files into a single context payload."""
        combined_code = ""
        languages = set()
        
        for f in files_data:
            parsed = self.parse_single(f["code"], filename=f["filename"])
            combined_code += f"--- File: {parsed['filename']} ---\n```{parsed['language']}\n{parsed['code']}\n```\n\n"
            languages.add(parsed["language"])
            
        # Determine main language or mark as multiple
        primary_lang = list(languages)[0] if len(languages) == 1 else "multiple"
        
        return {
            "code": combined_code.strip(),
            "error": error,
            "language": primary_lang,
        }