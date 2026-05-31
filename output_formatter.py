import re

class OutputFormatter:
    SECTIONS = ["Bug Type", "Root Cause", "Corrected Code"]
    COLORS = {
        "Bug Type":       "\033[91m",  
        "Root Cause":     "\033[93m",  
        "Corrected Code": "\033[92m",  
    }
    RESET = "\033[0m"

    def parse_sections(self, raw: str) -> dict:
        result = {}
        pattern = r"\[(Bug Type|Root Cause|Corrected Code)\](.*?)(?=\[(?:Bug Type|Root Cause|Corrected Code)\]|\Z)"
        
        for match in re.finditer(pattern, raw, re.DOTALL):
            key = match.group(1).strip()
            val = match.group(2).strip()
            result[key] = val
            
        return result

    def clean_code_block(self, raw_code: str) -> str:
        """Removes markdown backticks (e.g. ```python) for the diff viewer."""
        match = re.search(r"```[a-zA-Z]*\n(.*?)```", raw_code, re.DOTALL)
        if match:
            return match.group(1).strip()
        return raw_code.strip()

    def display(self, raw: str):
        sections = self.parse_sections(raw)
        print("\n" + "─"*52)
        for name in self.SECTIONS:
            color = self.COLORS.get(name, "")
            content = sections.get(name, "(not found)")
            print(f"\n{color}▶ {name}{self.RESET}")
            print(f"{content}")
        print("\n" + "─"*52 + "\n")