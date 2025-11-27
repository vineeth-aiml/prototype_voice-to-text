import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import vosk
import queue
import json
import threading
import os
# --------------------------
MODEL_PATH = r"D:\BEL_Projects_AIML\proto_voice_text\model\vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Vosk model folder not found.")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()

# Audio callback
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# --------------------------
def record_and_transcribe(duration):
    text_output.delete(1.0, tk.END)
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, 16000)
            import time
            start_time = time.time()
            while time.time() - start_time < duration:
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text_output.insert(tk.END, result.get("text", "") + "\n")
            final_result = json.loads(rec.FinalResult())
            text_output.insert(tk.END, final_result.get("text", "") + "\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    status_label.config(text="Idle")

def start_recording():
    try:
        duration = float(duration_var.get())
    except:
        duration = 5
    status_label.config(text="Recording... Speak now!")
    threading.Thread(target=record_and_transcribe, args=(duration,), daemon=True).start()

# --------------------------
root = tk.Tk()
root.title("Voice to Text (Vosk)")

tk.Label(root, text="Recording Duration (seconds):").pack(pady=5)
duration_var = tk.StringVar(value="5")
tk.Entry(root, textvariable=duration_var, width=5).pack(pady=5)

tk.Button(root, text="Start Recording", command=start_recording).pack(pady=10)

status_label = tk.Label(root, text="Idle")
status_label.pack(pady=5)

tk.Label(root, text="Transcribed Text:").pack(pady=5)
text_output = tk.Text(root, height=15, width=60, wrap='word')
text_output.pack(padx=10, pady=5)

root.mainloop()
