# Grabadora de Reuniones

> 🇲🇽 [Versión en Español](#español) · 🇺🇸 [English Version](#english)

---

<a name="español"></a>
# 🇲🇽 Español

Aplicación de escritorio para grabar reuniones **100% local**. Graba el micrófono y el audio del sistema simultáneamente, transcribe con Whisper y genera un resumen con un modelo de IA local vía Ollama — sin enviar ningún dato a la nube.

## Características

### 🎙 Grabación dual
Captura tu micrófono y el audio de la reunión (audio del sistema) al mismo tiempo. Al terminar, las pistas se mezclan automáticamente en un solo archivo.

### 📝 Transcripción automática
Usa [faster-whisper](https://github.com/SYSTRAN/faster-whisper) para transcribir el audio localmente. Detecta el idioma automáticamente y guarda en caché los resultados para no reprocesar.

### 🤖 Resumen con IA
Genera un resumen con decisiones clave y puntos de acción usando Ollama (por defecto `mistral:7b-instruct`). El resumen se entrega en el mismo idioma detectado en la transcripción.

### 💬 Chat con la reunión
Una vez procesada, abre una ventana de chat para hacer preguntas sobre el contenido de la reunión.

### 📂 Historial de grabaciones
Navega y reprocesa grabaciones anteriores desde la pestaña de historial.

## Requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado y corriendo localmente
- El modelo `mistral:7b-instruct` descargado en Ollama:
  ```bash
  ollama pull mistral:7b-instruct
  ```
- En Linux: PulseAudio o PipeWire (para captura de audio del sistema)

## Instalación

```bash
# Clona el repositorio
git clone https://github.com/YOUR_USERNAME/grabadora-de-reuniones.git
cd grabadora-de-reuniones

# Crea el entorno virtual e instala dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Con el entorno activo
source venv/bin/activate
python3 main.py
```

O con el script incluido:
```bash
bash run.sh
```

### Acceso directo en Linux (opcional)

Crea un archivo `~/.local/share/applications/grabadora-reuniones.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=Grabadora de Reuniones
Exec=bash -c 'cd "/ruta/al/proyecto" && source venv/bin/activate && python3 main.py'
Icon=audio-input-microphone
Terminal=false
```

## Flujo de trabajo

1. **Selecciona dispositivos** — elige tu micrófono y el monitor de audio del sistema.
2. **Graba** — pulsa "Start Recording"; el temporizador corre en tiempo real.
3. **Detén** — las pistas se mezclan automáticamente en `output/recordings/`.
4. **Procesa** — ve a la pestaña "History", selecciona el archivo y pulsa "Transcribe & Summarize".
5. **Revisa** — lee la transcripción y el resumen directamente en la app.
6. **Chatea** — usa el botón "Chat with Meeting" para hacer preguntas.

## Privacidad

- Todo el procesamiento ocurre **en tu máquina**.
- No se envía audio, transcripciones ni resúmenes a ningún servidor externo.
- Las grabaciones se guardan en `output/recordings/` (excluido del repositorio por `.gitignore`).

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| GUI | CustomTkinter |
| Grabación de audio | soundcard + soundfile + numpy |
| Transcripción | faster-whisper (OpenAI Whisper) |
| IA / Resumen | Ollama (`mistral:7b-instruct`) |

## Notas de versión

### 0.1.0 — Beta
Versión inicial funcional. Grabación dual (micrófono + sistema), mezcla automática, transcripción con Whisper, resumen y chat vía Ollama, historial de grabaciones, caché de transcripciones.

## Soporte

¿Encontraste un bug o tienes una sugerencia? Abre un issue en GitHub.

Hecho con ♥ por [RTSI](https://rtsi.mx)

---
---

<a name="english"></a>
# 🇺🇸 English

A **100% local** desktop application for recording meetings. It captures your microphone and system audio simultaneously, transcribes with Whisper, and generates an AI summary via Ollama — no data ever leaves your machine.

## Features

### 🎙 Dual recording
Captures your microphone and meeting audio (system audio) at the same time. When you stop, both tracks are automatically mixed into a single file.

### 📝 Automatic transcription
Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) to transcribe audio locally. Detects language automatically and caches results to avoid reprocessing.

### 🤖 AI summary
Generates a summary with key decisions and action items using Ollama (default: `mistral:7b-instruct`). The summary is delivered in the same language detected in the transcript.

### 💬 Chat with the meeting
Once processed, open a chat window to ask questions about the meeting content.

### 📂 Recordings history
Browse and reprocess past recordings from the history tab.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- The `mistral:7b-instruct` model pulled in Ollama:
  ```bash
  ollama pull mistral:7b-instruct
  ```
- On Linux: PulseAudio or PipeWire (for system audio capture)

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/grabadora-de-reuniones.git
cd grabadora-de-reuniones

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# With the virtual environment active
source venv/bin/activate
python3 main.py
```

Or with the included script:
```bash
bash run.sh
```

### Linux desktop shortcut (optional)

Create a file at `~/.local/share/applications/grabadora-reuniones.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=Grabadora de Reuniones
Exec=bash -c 'cd "/path/to/project" && source venv/bin/activate && python3 main.py'
Icon=audio-input-microphone
Terminal=false
```

## Workflow

1. **Select devices** — choose your microphone and system audio monitor.
2. **Record** — click "Start Recording"; a live timer runs.
3. **Stop** — both tracks are automatically mixed into `output/recordings/`.
4. **Process** — go to the "History" tab, select the file and click "Transcribe & Summarize".
5. **Review** — read the transcript and summary directly in the app.
6. **Chat** — use the "Chat with Meeting" button to ask questions.

## Privacy

- All processing happens **on your machine**.
- No audio, transcripts, or summaries are sent to any external server.
- Recordings are saved to `output/recordings/` (excluded from the repository via `.gitignore`).

## Tech Stack

| Component | Technology |
|---|---|
| GUI | CustomTkinter |
| Audio recording | soundcard + soundfile + numpy |
| Transcription | faster-whisper (OpenAI Whisper) |
| AI / Summary | Ollama (`mistral:7b-instruct`) |

## Release Notes

### 0.1.0 — Beta
Initial working release. Dual recording (microphone + system), automatic mixing, Whisper transcription, Ollama summary and chat, recordings history, transcript caching.

## Support

Found a bug or have a suggestion? Open an issue on GitHub.

Made with ♥ by [RTSI](https://rtsi.mx)
