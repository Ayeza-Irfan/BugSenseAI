# prompt_engine.py

# 1. The System Prompt now ONLY defines the personality for the whole chat
SYSTEM_PROMPT = """You are a senior software engineer and patient educator. 
You are helping a junior developer understand their code. Be conversational, encouraging, and highly technical but accessible."""

class PromptEngine:
    def build(self, parsed: dict) -> list[dict]:
        lang    = parsed["language"]
        code    = parsed["code"]
        error   = parsed["error"]

        user_msg = f"Language Context: {lang}\n\nCode/Project Files:\n{code}\n\n"
        
        if error:
            user_msg += f"Error message:\n{error}\n\n"

        # 2. We move the strict formatting rules into the specific user request
        user_msg += (
            "Please analyze the code above. For this specific analysis, you MUST follow these strict formatting rules:\n\n"
            "IF THE CODE CONTAINS BUGS:\n"
            "You MUST respond in exactly three labeled sections:\n"
            "[Bug Type]       — the category of bug (e.g. off-by-one, null dereference)\n"
            "[Root Cause]     — a clear, step-by-step explanation of WHY this fails\n"
            "[Corrected Code] — the fixed code with inline comments on every change\n\n"
            "IF THE CODE IS COMPLETELY CORRECT (NO BUGS):\n"
            "You MUST respond in exactly two labeled sections:\n"
            "[Bug Type]       — None\n"
            "[Root Cause]     — Explain briefly why the code is structurally and logically sound, and adheres to best practices.\n"
            "Do NOT generate a [Corrected Code] section.\n\n"
            "Do not skip sections unless instructed above. Do not add anything outside these sections for this initial report."
        )
        return [
            {"role": "user", "content": user_msg}
        ]

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT