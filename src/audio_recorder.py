import soundcard as sc
import soundfile as sf
import threading
import numpy as np
import time

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.mic_thread = None
        self.sys_thread = None
        
    def get_devices(self):
        """Returns a list of available microphones (including loopback)."""
        # On Linux, loopback/monitors are often listed in all_microphones(include_loopback=True)
        return sc.all_microphones(include_loopback=True)

    def _record_stream(self, device_id, output_path, stop_event):
        """Records from a specific device to a file."""
        try:
            mic = sc.get_microphone(device_id, include_loopback=True)
            samplerate = 44100
            # Open file for writing
            with sf.SoundFile(output_path, mode='w', samplerate=samplerate, channels=2) as file:
                with mic.recorder(samplerate=samplerate) as recorder:
                    while not stop_event.is_set():
                        data = recorder.record(numframes=1024)
                        file.write(data)
        except Exception as e:
            print(f"Error recording from device {device_id}: {e}")

    def start_recording(self, mic_id, sys_id, output_path_mic, output_path_sys):
        self.stop_event = threading.Event()
        self.recording = True
        self.output_path_mic = output_path_mic
        self.output_path_sys = output_path_sys
        
        # Start microphone thread
        if mic_id is not None:
            self.mic_thread = threading.Thread(
                target=self._record_stream, 
                args=(mic_id, output_path_mic, self.stop_event)
            )
            self.mic_thread.start()
            
        # Start system audio thread
        if sys_id is not None:
            self.sys_thread = threading.Thread(
                target=self._record_stream, 
                args=(sys_id, output_path_sys, self.stop_event)
            )
            self.sys_thread.start()
            
    def stop_recording(self):
        self.recording = False
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
        
        if self.mic_thread:
            self.mic_thread.join()
        if self.sys_thread:
            self.sys_thread.join()
            
        # Mix audio files if both exist
        self.mix_audio()

    def mix_audio(self):
        """Mixes the microphone and system audio into a single file."""
        import os
        if not hasattr(self, 'output_path_mic') or not hasattr(self, 'output_path_sys'):
            return

        path_mic = self.output_path_mic
        path_sys = self.output_path_sys
        
        # Determine combined path (replace _mic.wav or _sys.wav with _combined.wav)
        base_path = path_mic.replace("_mic.wav", "")
        if base_path == path_mic: # fallback
             base_path = path_sys.replace("_sys.wav", "")
        
        output_combined = f"{base_path}_combined.wav"
        
        try:
            # Read files (handle if one doesn't exist)
            data_mic, sr_mic = sf.read(path_mic) if os.path.exists(path_mic) else (None, 0)
            data_sys, sr_sys = sf.read(path_sys) if os.path.exists(path_sys) else (None, 0)
            
            if data_mic is None and data_sys is None:
                return
                
            sample_rate = sr_mic if sr_mic else sr_sys
            
            # Ensure same length
            len_mic = len(data_mic) if data_mic is not None else 0
            len_sys = len(data_sys) if data_sys is not None else 0
            max_len = max(len_mic, len_sys)
            
            # Create empty arrays with max length
            # Assuming stereo (2 channels)
            final_audio = np.zeros((max_len, 2))
            
            if data_mic is not None:
                # If mic is mono, make it stereo
                if len(data_mic.shape) == 1:
                    data_mic = np.column_stack((data_mic, data_mic))
                final_audio[:len_mic] += data_mic

            if data_sys is not None:
                if len(data_sys.shape) == 1:
                    data_sys = np.column_stack((data_sys, data_sys))
                final_audio[:len_sys] += data_sys

            # Save combined
            sf.write(output_combined, final_audio, sample_rate)
            print(f"Created combined audio: {output_combined}")
            
        except Exception as e:
            print(f"Error mixing audio: {e}")
