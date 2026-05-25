# Linux Show Player (LiSP)

A free, open-source cue player primarily intended for sound-playback during stage productions (theatre, musicals, etc.).

## Project Overview

Linux Show Player (LiSP) is a PyQt5 desktop GUI application with a plugin-based architecture. It allows operators to manage and trigger various "cues" (audio, MIDI, OSC, etc.) during a live performance.

## Tech Stack

- **Language:** Python 3.12
- **GUI Framework:** PyQt5 (Qt5)
- **Multimedia:** GStreamer (via PyGObject)
- **Audio:** JACK, ALSA, PulseAudio
- **Protocols:** MIDI (mido, python-rtmidi), OSC (pyliblo3)
- **Networking:** Falcon

## Running the App

The app runs as a VNC desktop application. The workflow command is:

```
QT_QPA_PLATFORM_PLUGIN_PATH=/nix/store/ddql3f7bssigizb2rnm1y0yldq81iqg9-qtbase-5.15.17-bin/lib/qt-5.15.17/plugins python3 -m lisp.main
```

The `QT_QPA_PLATFORM_PLUGIN_PATH` environment variable is required to point Qt to the correct platform plugin directory in the Nix store.

## Expected Plugin Warnings

When running in the Replit environment, these plugin warnings are **expected** and harmless:
- **gst_backend** — GStreamer namespace not available without full GStreamer introspection setup
- **MIDI** — No ALSA sequencer device in cloud environment
- **OSC** — `pyliblo3` requires liblo native library
- **ArtNet** — `ola` module not available
- **replay_gain** — Depends on GStreamer

These are hardware/platform-specific features that require physical audio/MIDI devices.

## Project Structure

- `lisp/` — Main source package
  - `core/` — Core system (plugin manager, session, signals)
  - `ui/` — PyQt5 UI components and main window
  - `plugins/` — Modular plugin extensions
  - `cues/` — Cue base classes
  - `command/` — Command pattern (undo/redo)
  - `i18n/` — Internationalization files
- `pyproject.toml` — Poetry-managed dependencies
- `lisp/default.json` — Default application configuration

## User Preferences

- This is a desktop GUI application, not a web app
- Runs in VNC mode in Replit
