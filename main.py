import customtkinter as ctk
import threading
import os
import time
from src.audio_recorder import AudioRecorder
from src.transcriber import Transcriber
from src.summarizer import Summarizer
from src.utils import ensure_dirs, get_timestamp, load_device_aliases, save_device_aliases

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
        self.device_test_running = False
        self.device_aliases = load_device_aliases()
        
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
        self.combo_mic = ctk.CTkComboBox(
            self.tab_record, width=500,
            command=lambda _value: self.load_alias_for_selection("mic")
        )
        self.combo_mic.pack(pady=5)

        self.mic_alias_frame = ctk.CTkFrame(self.tab_record, fg_color="transparent")
        self.mic_alias_frame.pack(pady=(0, 6))
        self.entry_mic_alias = ctk.CTkEntry(
            self.mic_alias_frame, width=340, placeholder_text="Device suffix, e.g. headset"
        )
        self.entry_mic_alias.pack(side="left", padx=(0, 10))
        self.btn_save_mic_alias = ctk.CTkButton(
            self.mic_alias_frame, text="Save suffix", width=150,
            command=lambda: self.save_alias_for_selection("mic")
        )
        self.btn_save_mic_alias.pack(side="left")

        self.mic_test_frame = ctk.CTkFrame(self.tab_record, fg_color="transparent")
        self.mic_test_frame.pack(pady=(0, 8))
        self.btn_test_mic = ctk.CTkButton(
            self.mic_test_frame, text="Test microphone", width=140,
            command=lambda: self.test_selected_device("mic")
        )
        self.btn_test_mic.pack(side="left", padx=(0, 10))
        self.mic_meter = ctk.CTkProgressBar(self.mic_test_frame, width=180)
        self.mic_meter.set(0)
        self.mic_meter.pack(side="left", padx=(0, 10))
        self.lbl_mic_test = ctk.CTkLabel(self.mic_test_frame, text="Ready", width=160, anchor="w")
        self.lbl_mic_test.pack(side="left")
        
        self.lbl_sys = ctk.CTkLabel(self.tab_record, text="System Audio (Meeting Audio/Monitor):")
        self.lbl_sys.pack()
        self.combo_sys = ctk.CTkComboBox(
            self.tab_record, width=500,
            command=lambda _value: self.load_alias_for_selection("sys")
        )
        self.combo_sys.pack(pady=5)

        self.sys_alias_frame = ctk.CTkFrame(self.tab_record, fg_color="transparent")
        self.sys_alias_frame.pack(pady=(0, 6))
        self.entry_sys_alias = ctk.CTkEntry(
            self.sys_alias_frame, width=340, placeholder_text="Device suffix, e.g. meeting monitor"
        )
        self.entry_sys_alias.pack(side="left", padx=(0, 10))
        self.btn_save_sys_alias = ctk.CTkButton(
            self.sys_alias_frame, text="Save suffix", width=150,
            command=lambda: self.save_alias_for_selection("sys")
        )
        self.btn_save_sys_alias.pack(side="left")

        self.sys_test_frame = ctk.CTkFrame(self.tab_record, fg_color="transparent")
        self.sys_test_frame.pack(pady=(0, 8))
        self.btn_test_sys = ctk.CTkButton(
            self.sys_test_frame, text="Play test sound", width=160,
            command=lambda: self.test_selected_device("sys")
        )
        self.btn_test_sys.pack(side="left", padx=(0, 10))
        self.lbl_sys_test = ctk.CTkLabel(self.sys_test_frame, text="Ready", width=330, anchor="w")
        self.lbl_sys_test.pack(side="left")

        self.btn_refresh = ctk.CTkButton(self.tab_record, text="Refresh Devices", command=self.refresh_devices)
        self.btn_refresh.pack(pady=8)
        
        self.lbl_timer = ctk.CTkLabel(self.tab_record, text="00:00:00", font=("Arial", 40, "bold"))
        self.lbl_timer.pack(pady=18)
        
        self.btn_start = ctk.CTkButton(self.tab_record, text="Start Recording", command=self.start_recording, fg_color="green", height=50, width=200)
        self.btn_start.pack(pady=10)
        
        self.btn_stop = ctk.CTkButton(self.tab_record, text="Stop Recording", command=self.stop_recording, fg_color="red", state="disabled", height=50, width=200)
        self.btn_stop.pack(pady=10)
        
        # --- History Tab ---
        self.model_status_frame = ctk.CTkFrame(self.tab_history)
        self.model_status_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.lbl_model_status_title = ctk.CTkLabel(
            self.model_status_frame, text="Model readiness", font=("Arial", 14, "bold")
        )
        self.lbl_model_status_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 5))

        self.lbl_whisper_status = ctk.CTkLabel(
            self.model_status_frame, text="Whisper transcription: checking...",
            anchor="w", justify="left", wraplength=610
        )
        self.lbl_whisper_status.grid(row=1, column=0, sticky="w", padx=12, pady=3)

        self.lbl_summary_status = ctk.CTkLabel(
            self.model_status_frame, text="LM Studio summary: checking...",
            anchor="w", justify="left", wraplength=610
        )
        self.lbl_summary_status.grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))

        self.btn_check_models = ctk.CTkButton(
            self.model_status_frame, text="Check again", width=120,
            command=self.refresh_model_status
        )
        self.btn_check_models.grid(row=1, column=1, rowspan=2, padx=12, pady=10)
        self.model_status_frame.grid_columnconfigure(0, weight=1)

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
        self.after(250, self.refresh_model_status)

    def refresh_model_status(self):
        self.btn_check_models.configure(state="disabled", text="Checking...")
        checking_color = ("gray35", "gray70")
        self.lbl_whisper_status.configure(text="Whisper transcription: checking...", text_color=checking_color)
        self.lbl_summary_status.configure(text="LM Studio summary: checking...", text_color=checking_color)

        def check():
            whisper_ready, whisper_message = Transcriber.check_model_ready()
            summary_ready, summary_message = Summarizer.check_model_ready()

            def update_ui():
                self.set_model_status(self.lbl_whisper_status, "Whisper transcription", whisper_ready, whisper_message)
                self.set_model_status(self.lbl_summary_status, "LM Studio summary", summary_ready, summary_message)
                self.btn_check_models.configure(state="normal", text="Check again")

            self.after(0, update_ui)

        threading.Thread(target=check, daemon=True).start()

    @staticmethod
    def set_model_status(label, title, ready, message):
        state = "READY" if ready else "NOT READY"
        color = "#4CAF50" if ready else "#F0A000"
        label.configure(text=f"{title}: {state} — {message}", text_color=color)
        
    def refresh_devices(self):
        try:
            selected_mic_id = self.mic_device_map.get(self.combo_mic.get()) if hasattr(self, "mic_device_map") else None
            selected_sys = self.sys_device_map.get(self.combo_sys.get()) if hasattr(self, "sys_device_map") else None
            selected_speaker_id = selected_sys["speaker_id"] if selected_sys else None
            self.mic_device_map = {}
            self.sys_device_map = {}
            self.mic_names_by_id = {}
            self.sys_names_by_id = {}

            for d in self.recorder.get_input_devices():
                name = f"{d.name} ({d.id})"
                alias = self.device_aliases.get(f"input:{d.id}", self.device_aliases.get(str(d.id), ""))
                if alias:
                    name = f"{name} — {alias}"
                self.mic_device_map[name] = d.id
                self.mic_names_by_id[str(d.id)] = name

            for speaker, monitor_id in self.recorder.get_system_devices():
                name = f"{speaker.name} ({speaker.id})"
                alias = self.device_aliases.get(f"output:{speaker.id}", self.device_aliases.get(str(monitor_id), ""))
                if alias:
                    name = f"{name} — {alias}"
                self.sys_device_map[name] = {
                    "speaker_id": speaker.id,
                    "monitor_id": monitor_id,
                }
                self.sys_names_by_id[str(speaker.id)] = name
            
            mic_names = list(self.mic_device_map.keys())
            sys_names = list(self.sys_device_map.keys())
            self.combo_mic.configure(values=mic_names)
            self.combo_sys.configure(values=sys_names)
            
            if mic_names:
                self.combo_mic.set(self.mic_names_by_id.get(str(selected_mic_id), mic_names[0]))
                self.load_alias_for_selection("mic")
            if sys_names:
                self.combo_sys.set(self.sys_names_by_id.get(str(selected_speaker_id), sys_names[0]))
                self.load_alias_for_selection("sys")
        except Exception as e:
            print(f"Error refreshing devices: {e}")

    def load_alias_for_selection(self, source):
        combo = self.combo_mic if source == "mic" else self.combo_sys
        entry = self.entry_mic_alias if source == "mic" else self.entry_sys_alias
        if source == "mic":
            device_id = self.mic_device_map.get(combo.get())
            key = f"input:{device_id}" if device_id is not None else None
        else:
            device = self.sys_device_map.get(combo.get())
            device_id = device["speaker_id"] if device else None
            key = f"output:{device_id}" if device_id is not None else None
        entry.delete(0, "end")
        if key:
            entry.insert(0, self.device_aliases.get(key, ""))

    def save_alias_for_selection(self, source):
        combo = self.combo_mic if source == "mic" else self.combo_sys
        entry = self.entry_mic_alias if source == "mic" else self.entry_sys_alias
        if source == "mic":
            device_id = self.mic_device_map.get(combo.get())
            key = f"input:{device_id}" if device_id is not None else None
        else:
            device = self.sys_device_map.get(combo.get())
            device_id = device["speaker_id"] if device else None
            key = f"output:{device_id}" if device_id is not None else None
        if device_id is None:
            return

        alias = " ".join(entry.get().strip().split())[:60]
        if alias:
            self.device_aliases[key] = alias
        else:
            self.device_aliases.pop(key, None)
        save_device_aliases(self.device_aliases)
        self.refresh_devices()

    def test_selected_device(self, source):
        if self.device_test_running or self.is_recording:
            return

        combo = self.combo_mic if source == "mic" else self.combo_sys
        status_label = self.lbl_mic_test if source == "mic" else self.lbl_sys_test
        if source == "mic":
            device_id = self.mic_device_map.get(combo.get())
        else:
            device = self.sys_device_map.get(combo.get())
            device_id = device["speaker_id"] if device else None
        if device_id is None:
            status_label.configure(text="Select a device", text_color="#F0A000")
            return

        self.device_test_running = True
        self.set_device_controls_state("disabled")
        if source == "sys":
            status_label.configure(text="Playing through this output...", text_color=("gray20", "gray80"))

            def output_complete(error):
                def update_ui():
                    self.device_test_running = False
                    self.set_device_controls_state("normal")
                    if error:
                        status_label.configure(text="Error — retry", text_color="#E05A5A")
                        print(f"Output test error: {error}")
                    else:
                        status_label.configure(text="Did you hear the test sound?", text_color="#4CAF50")
                self.after(0, update_ui)

            self.recorder.play_test_tone(device_id, on_complete=output_complete)
            return

        meter = self.mic_meter
        meter.set(0)
        status_label.configure(text="Listening (5 s)...", text_color=("gray20", "gray80"))

        def update_level(level):
            self.after(0, lambda: meter.set(level))

        def complete(detected, error):
            def update_ui():
                self.device_test_running = False
                self.set_device_controls_state("normal")
                meter.set(0)
                if error:
                    status_label.configure(text="Error — retry", text_color="#E05A5A")
                    print(f"Device test error: {error}")
                elif detected:
                    status_label.configure(text="Signal detected", text_color="#4CAF50")
                else:
                    status_label.configure(text="No signal — check source", text_color="#F0A000")
            self.after(0, update_ui)

        self.recorder.test_device(device_id, on_level=update_level, on_complete=complete)

    def set_device_controls_state(self, state):
        for widget in (
            self.combo_mic, self.combo_sys, self.btn_test_mic,
            self.btn_test_sys, self.btn_refresh, self.entry_mic_alias,
            self.entry_sys_alias, self.btn_save_mic_alias,
            self.btn_save_sys_alias, self.btn_start
        ):
            widget.configure(state=state)

    def start_recording(self):
        mic_name = self.combo_mic.get()
        sys_name = self.combo_sys.get()
        
        mic_id = self.mic_device_map.get(mic_name)
        system_device = self.sys_device_map.get(sys_name)
        sys_id = system_device["monitor_id"] if system_device else None
        
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
        self.set_device_controls_state("disabled")
        
    def stop_recording(self):
        self.recorder.stop_recording()
        self.is_recording = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.set_device_controls_state("normal")
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
                    self.txt_output.insert("end", "[...] Connecting to LM Studio...\n")
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
