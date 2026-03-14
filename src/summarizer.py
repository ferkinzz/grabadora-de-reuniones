import ollama

class Summarizer:
    def __init__(self, model_name="mistral:7b-instruct"):
        self.model_name = model_name

    def summarize(self, text, language_code="en"):
        """Generates a summary, instructing LLM to use the detected language."""
        if not text:
            return "No text to summarize."
            
        prompt = f"""
        You are a meeting assistant.
        Below is a meeting transcript with timestamps (e.g., [00:12]).
        
        b]IMPORTANT INSTRUCTION[/b]: 
        The language of the transcript is '{language_code}'.
        You MUST provide the summary IN THE SAME LANGUAGE ({language_code}).
        
        Please IGNORE the timestamps and focus on the content.
        Provide a concise summary highlighting key decisions and action items.
        
        Transcript:
        {text}
        """
        
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error generating summary: {e}"

    def chat(self, transcript, user_query):
        """Answers a user question based on the provided transcript."""
        if not transcript:
            return "No transcript context available."

        # Create a system prompt with the transcript context
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
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error in chat: {e}"
