from openai import OpenAI
import os

LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")

class Summarizer:
    DEFAULT_MODEL_NAME = "google/gemma-4-e4b"

    def __init__(self, model_name="google/gemma-4-e4b"):
        self.model_name = model_name
        self.client = OpenAI(base_url=LMSTUDIO_BASE_URL, api_key="not-needed")

    @classmethod
    def check_model_ready(cls, model_name=None):
        """Check that LM Studio is reachable and exposes the configured model."""
        model_name = model_name or cls.DEFAULT_MODEL_NAME
        client = OpenAI(base_url=LMSTUDIO_BASE_URL, api_key="not-needed", timeout=3.0)
        try:
            available_models = [model.id for model in client.models.list().data]
        except Exception:
            return False, "LM Studio is not running or its server is unavailable"

        if model_name in available_models:
            return True, f"{model_name} is loaded and ready"
        if available_models:
            return False, f"Required: {model_name}. Loaded: {', '.join(available_models)}"
        return False, f"LM Studio is running, but {model_name} is not loaded"

    def summarize(self, text, language_code="en"):
        if not text:
            return "No text to summarize."

        prompt = f"""
        You are a meeting assistant.
        Below is a meeting transcript with timestamps (e.g., [00:12]).
        
        IMPORTANT INSTRUCTION:
        The language of the transcript is '{language_code}'.
        You MUST provide the summary IN THE SAME LANGUAGE ({language_code}).
        
        Please IGNORE the timestamps and focus on the content.
        Provide a concise summary highlighting key decisions and action items.
        
        Transcript:
        {text}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {e}"

    def chat(self, transcript, user_query):
        if not transcript:
            return "No transcript context available."

        messages = [
            {
                'role': 'system',
                'content': f"You are a helpful assistant. Answer the user's question based strictly on the following meeting transcript. Ignore timestamps like [MM:SS].\n\nTranscript:\n{transcript}"
            },
            {
                'role': 'user',
                'content': user_query
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in chat: {e}"
