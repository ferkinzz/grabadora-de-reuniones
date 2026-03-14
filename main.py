import customtkinter as ctk
import threading
import os
import time
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.summarizer import Summarizer
from src.utils import ensure_dirs, get_timestamp

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MeetingRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Local Meeting Recorder")
        self.geometry("900x700")
        
        ensure_dirs()
        self.recorder = AudioRecorder()
        self.transcriber = None 
        self.summarizer = None
        self.is_recording = False
        
        self.create_widgets()
        
        # Safe device loading (might fail if dependencies aren't installed yet)
        try:
            self.refresh_devices()
        except:
            print("Could not load devices. Dependencies might be missing.")

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_record = self.tabview.add("Record")
        self.tab_history = self.tabview.add("History")
        
        # --- Record Tab ---
        self.lbl_devices = ctk.CTkLabel(self.tab_record, text="Select Audio Devices", font=("Arial", 16, "bold"))
        self.lbl_devices.pack(pady=10)
        
        self.lbl_mic = ctk.CTkLabel(self.tab_record, text="Microphone (Your Voice):")
        self.lbl_mic.pack()
        self.combo_mic = ctk.CTkComboBox(self.tab_record, width=400)
        self.combo_mic.pack(pady=5)
        
        self.lbl_sys = ctk.CTkLabel(self.tab_record, text="System Audio (Meeting Audio/Monitor):")
        self.lbl_sys.pack()
        self.combo_sys = ctk.CTkComboBox(self.tab_record, width=400)
        self.combo_sys.pack(pady=5)
        
        self.btn_refresh = ctk.CTkButton(self.tab_record, text="Refresh Devices", command=self.refresh_devices)
        self.btn_refresh.pack(pady=10)
        
        self.lbl_timer = ctk.CTkLabel(self.tab_record, text="00:00:00", font=("Arial", 40, "bold"))
        self.lbl_timer.pack(pady=30)
        
        self.btn_start = ctk.CTkButton(self.tab_record, text="Start Recording", command=self.start_recording, fg_color="green", height=50, width=200)
        self.btn_start.pack(pady=10)
        
        self.btn_stop = ctk.CTkButton(self.tab_record, text="Stop Recording", command=self.stop_recording, fg_color="red", state="disabled", height=50, width=200)
        self.btn_stop.pack(pady=10)
        
        # --- History Tab ---
        self.lbl_history = ctk.CTkLabel(self.tab_history, text="Recordings", font=("Arial", 16, "bold"))
        self.lbl_history.pack(pady=5)
        
        self.list_files = ctk.CTkScrollableFrame(self.tab_history, height=200)
        self.list_files.pack(fill="x", padx=10, pady=5)
        
        self.btn_refresh_files = ctk.CTkButton(self.tab_history, text="Refresh List", command=self.refresh_file_list)
        self.btn_refresh_files.pack(pady=5)
        
        self.btn_process = ctk.CTkButton(self.tab_history, text="Transcribe & Summarize Selected", command=self.process_selected, fg_color="#E58E00")
        self.btn_process.pack(pady=5)
        
        self.btn_chat = ctk.CTkButton(self.tab_history, text="Chat with Meeting", command=self.open_chat_window, state="disabled", fg_color="#0066CC")
        self.btn_chat.pack(pady=5)
        
        self.txt_output = ctk.CTkTextbox(self.tab_history, font=("Consolas", 12))
        self.txt_output.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.selected_file = ctk.StringVar(value="")
        self.refresh_file_list()
        
    def refresh_devices(self):
        try:
            devices = self.recorder.get_devices()
            self.device_map = {}
            for i, d in enumerate(devices):
                # Creating a unique name for the dropdown
                name = f"{d.name} ({d.id})"
                self.device_map[name] = d.id
            
            device_names = list(self.device_map.keys())
            self.combo_mic.configure(values=device_names)
            self.combo_sys.configure(values=device_names)
            
            if device_names:
                self.combo_mic.set(device_names[0])
                self.combo_sys.set(device_names[0])
        except Exception as e:
            print(f"Error refreshing devices: {e}")

    def start_recording(self):
        mic_name = self.combo_mic.get()
        sys_name = self.combo_sys.get()
        
        mic_id = self.device_map.get(mic_name)
        sys_id = self.device_map.get(sys_name)
        
        timestamp = get_timestamp()
        # Create separate files for now, could mix later
        self.current_mic_file = f"output/recordings/meeting_{timestamp}_mic.wav"
        self.current_sys_file = f"output/recordings/meeting_{timestamp}_sys.wav"
        
        self.recorder.start_recording(mic_id, sys_id, self.current_mic_file, self.current_sys_file)
        
        self.is_recording = True
        self.start_time = time.time()
        self.update_timer()
        
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_refresh.configure(state="disabled")
        
    def stop_recording(self):
        self.recorder.stop_recording()
        self.is_recording = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_refresh.configure(state="normal")
        self.lbl_timer.configure(text="00:00:00")
        self.refresh_file_list()

    def update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.start_time)
            h, r = divmod(elapsed, 3600)
            m, s = divmod(r, 60)
            self.lbl_timer.configure(text=f"{h:02}:{m:02}:{s:02}")
            self.after(1000, self.update_timer)

    def refresh_file_list(self):
        for widget in self.list_files.winfo_children():
            widget.destroy()
            
        if not os.path.exists("output/recordings"):
            return

        # Filter for combined files first, or fallback to others
        all_files = sorted(os.listdir("output/recordings"), reverse=True)
        display_files = [f for f in all_files if f.endswith("_combined.wav")]
        
        # If no combined files found, show all .wav (fallback)
        if not display_files:
            display_files = [f for f in all_files if f.endswith(".wav")]
        
        for f in display_files:
            rb = ctk.CTkRadioButton(self.list_files, text=f, variable=self.selected_file, value=f)
            rb.pack(anchor="w", pady=2)

    def process_selected(self):
        filename = self.selected_file.get()
        if not filename:
            self.txt_output.insert("end", "\n[!] Please select a file to process.\n")
            return
            
        file_path = os.path.join("output/recordings", filename)
        
        self.txt_output.insert("end", f"\n[=] Processing {filename}...\n")
        self.btn_process.configure(state="disabled")
        
        def run_process():
            try:
                if not self.transcriber:
                    self.txt_output.insert("end", "[...] Loading Whisper model (this may take a moment)...\n")
                    self.transcriber = Transcriber(model_size="base")
                
                self.txt_output.insert("end", "[...] Transcribing...\n")
                # Store absolute path for caching logic to work best
                abs_path = os.path.abspath(file_path)
                text, lang = self.transcriber.transcribe(abs_path)
                
                # Store for chat
                self.current_transcript = text
                
                # Show transcript
                self.txt_output.insert("end", f"\n--- Transcript (Language: {lang}) ---\n{text}\n")
                
                if not self.summarizer:
                    self.txt_output.insert("end", "[...] Connecting to Ollama...\n")
                    self.summarizer = Summarizer()
                    
                self.txt_output.insert("end", f"[...] Summarizing (in {lang})...\n")
                summary = self.summarizer.summarize(text, language_code=lang)
                
                # Show summary
                self.txt_output.insert("end", f"\n--- Summary ---\n{summary}\n")
                self.txt_output.insert("end", "\n[Done]\n")
                
                # Enable chat button
                self.btn_chat.configure(state="normal")
                
            except Exception as e:
                self.txt_output.insert("end", f"\n[!] Error: {e}\n")
            finally:
                self.btn_process.configure(state="normal")
                
        threading.Thread(target=run_process).start()

    def open_chat_window(self):
        if not hasattr(self, 'current_transcript'):
            return

        chat_window = ctk.CTkToplevel(self)
        chat_window.title("Chat with Meeting")
        chat_window.geometry("600x500")
        
        chat_history = ctk.CTkTextbox(chat_window, font=("Arial", 12))
        chat_history.pack(fill="both", expand=True, padx=10, pady=10)
        
        input_frame = ctk.CTkFrame(chat_window)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        entry_query = ctk.CTkEntry(input_frame, placeholder_text="Ask about the meeting...")
        entry_query.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def send_query():
            query = entry_query.get()
            if not query: return
            
            chat_history.insert("end", f"\nYou: {query}\n")
            entry_query.delete(0, "end")
            
            def get_answer():
                answer = self.summarizer.chat(self.current_transcript, query)
                chat_history.insert("end", f"AI: {answer}\n")
                
            threading.Thread(target=get_answer).start()

        btn_send = ctk.CTkButton(input_frame, text="Send", command=send_query)
        btn_send.pack(side="right")

if __name__ == "__main__":
    app = MeetingRecorderApp()
    app.mainloop()
