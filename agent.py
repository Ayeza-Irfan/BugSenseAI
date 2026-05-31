import os
import streamlit as st
from google import genai
from google.genai import types
from prompt_engine import PromptEngine
from dotenv import load_dotenv

load_dotenv()


class BugSenseAgent:
    def __init__(self):

        # Try local .env first
        api_key = os.getenv("GEMINI_API_KEY")

        # If not found, try Streamlit Cloud Secrets
        if not api_key:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                raise ValueError(
                    "Gemini API key not found. Set GEMINI_API_KEY in your .env file "
                    "or add it to Streamlit Cloud Secrets."
                )

        self.client = genai.Client(api_key=api_key)

        self.engine = PromptEngine()
        self.model_id = "gemini-3-flash-preview"
        self.retries = 3

    def start_chat_and_run(self, prompt_list: list):
        user_text = prompt_list[0]["content"]

        config = types.GenerateContentConfig(
            system_instruction=self.engine.system_prompt(),
            temperature=0.2
        )

        chat_session = self.client.chats.create(
            model=self.model_id,
            config=config
        )

        for attempt in range(self.retries):
            try:
                response = chat_session.send_message(user_text)
                return response.text, chat_session

            except Exception as e:
                print(f"[retry {attempt + 1}] API error: {e}")

        return "Error: could not reach the Gemini API after 3 attempts.", None

    def send_followup(
        self,
        chat_session,
        message: str,
        context_code: str = "",
        chat_history: list = None
    ) -> tuple:
        """
        Sends a follow-up message.
        If no session exists (e.g., loaded from history),
        it reconstructs context and starts a new session.
        """

        # Scenario A: Session lost (loaded from history)
        if chat_session is None:

            config = types.GenerateContentConfig(
                system_instruction=self.engine.system_prompt(),
                temperature=0.2
            )

            chat_session = self.client.chats.create(
                model=self.model_id,
                config=config
            )

            history_text = "\n".join(
                [
                    f"{m['role'].capitalize()}: {m['content']}"
                    for m in (chat_history or [])
                ]
            )

            override_instruction = (
                f"We are resuming an old debugging session.\n\n"
                f"Original Code:\n{context_code}\n\n"
                f"Past Conversation:\n{history_text}\n\n"
                f"New User Question:\n{message}\n\n"
                "---\n"
                "System Reminder: Answer the above question "
                "conversationally based on the context. "
                "Do NOT use the [Bug Type], [Root Cause], "
                "or [Corrected Code] format."
            )

        # Scenario B: Active session
        else:

            override_instruction = (
                f"{message}\n\n"
                "---\n"
                "System Reminder: Answer the above question conversationally. "
                "Do NOT use the [Bug Type], [Root Cause], "
                "or [Corrected Code] format."
            )

        try:
            response = chat_session.send_message(override_instruction)

            return response.text, chat_session

        except Exception as e:
            return f"Error sending message: {e}", None