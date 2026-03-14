from faster_whisper import WhisperModel
import os

class Transcriber:
    def __init__(self, model_size="base"):
        # Run on CPU by default to be safe, or "cuda" if available
        # faster-whisper handles this auto logic well usually, but explicit is better
        device = "cpu" 
        # You can add logic to check for CUDA
        
        print(f"Loading Whisper model: {model_size} on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, file_path):
        """Transcribes audio, returns (text, language_code), and caches result."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Check cache
        base_name = os.path.basename(file_path).replace(".wav", ".txt")
        cache_path = os.path.join("output/transcripts", base_name)
        
        # Simple cache check - if we wanted allow re-reading language we'd need metadata
        # For now, let's just re-run if we need language or implement a meta file.
        # To keep it simple and robust: we won't rely on cache for language detection 
        # unless we save it. Let's save a .meta file.
        
        meta_path = cache_path + ".meta"
        
        if os.path.exists(cache_path) and os.path.exists(meta_path):
            print(f"Loading cached transcript: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                text = f.read()
            with open(meta_path, "r", encoding="utf-8") as f:
                lang = f.read().strip()
            return text, lang

        print(f"Transcribing {file_path}...")
        segments, info = self.model.transcribe(file_path, beam_size=5)
        
        detected_lang = info.language
        print(f"Detected language: {detected_lang}")
        
        full_transcript = []
        for segment in segments:
            # Format: [00:12] Hello world
            start_time = self._format_time(segment.start)
            line = f"[{start_time}] {segment.text}"
            full_transcript.append(line)
            
        result_text = "\n".join(full_transcript)
        
        # Save to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(detected_lang)
            
        return result_text, detected_lang

    def _format_time(self, seconds):
        """Converts seconds to MM:SS format."""
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"
