# Mimi AI Assistant (Local, Offline-Friendly)

A local VTuber assistant that:
- Sees your screen (screen capture)
- Detects UI elements (YOLOv8)
- Describes scenes (CLIP)
- Thinks and talks like a cute VTuber (Ollama Llama 3.2 3B)
- Controls mouse and keyboard (PyAutoGUI)
- Chats with you in a GUI (Tkinter)
- Automates tasks like searching YouTube (smart click & type)

This README covers setup, running, features, and troubleshooting.

---

## ✨ Features

- Live screen capture at 10 FPS (MSS)
- YOLOv8 real-time detection for UI elements (trained on your dataset)
- CLIP-based scene captioning
- VTuber personality via Ollama (Llama 3.2:3B) with cute persona
- Text-to-speech with robust pyttsx3 controller
- GUI chat window to talk with Mimi
- Smart YouTube search:
  - If YouTube is open → focus search → type → press Enter
  - If browser open → Ctrl+L → navigate → search
  - If nothing open → open Chrome/default browser with search URL
- Safe automation: PyAutoGUI failsafe, confirm flags optional

---





---

## ✅ Requirements

- Windows 10/11
- Python 3.10 or 3.11
- NVIDIA GPU (RTX 2060 recommended) with CUDA 11.8 drivers
- Chrome installed (recommended)
- Ollama installed and running (for LLM)

---



