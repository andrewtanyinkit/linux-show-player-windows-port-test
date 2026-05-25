# PyInstaller runtime hook for Windows
# Runs before any application code when launched from the bundled exe.
# Stubs out Linux-only dependencies so the plugin loader's existing
# graceful-degradation (try/except) continues to work on Windows.

import sys
import types


def _stub(name, **attrs):
    """Create and register a stub module with optional attributes."""
    mod = types.ModuleType(name)
    mod.__spec__ = None
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ── GObject Introspection (gst_backend / replay_gain) ────────────────────────
# gi.require_version raises ValueError on missing namespace — stub the whole
# tree so the check raises ImportError instead, letting plugin_loader skip it.
if "gi" not in sys.modules:
    _stub("gi")
    _stub("gi.repository")
    _stub("gi.repository.Gst")
    _stub("gi.repository.GLib")
    _stub("gi.repository.GObject")
    _stub("gi.repository.GstPbutils")
    _stub("gi.repository.GstApp")
    _stub("gi.repository.GstController")

# ── ALSA (port_monitor.py already does try/except ImportError) ───────────────
if "pyalsa" not in sys.modules:
    _stub("pyalsa")
    _stub("pyalsa.alsaseq", SequencerError=Exception)

# ── JACK client ───────────────────────────────────────────────────────────────
if "jack" not in sys.modules:
    _stub("jack")

# ── liblo / OSC ───────────────────────────────────────────────────────────────
# Provide stub classes so "from liblo import ServerThread, ServerError"
# gives an ImportError-compatible failure that plugin_loader catches.
if "liblo" not in sys.modules:
    _stub("liblo",
          ServerThread=None,
          ServerError=Exception,
          Address=None,
          send=None)
if "pyliblo3" not in sys.modules:
    _stub("pyliblo3",
          ServerThread=None,
          ServerError=Exception,
          Address=None,
          send=None)

# ── OLA / ArtNet ──────────────────────────────────────────────────────────────
if "ola" not in sys.modules:
    ola_mod = _stub("ola")
    client_mod = _stub("ola.OlaClient",
                       OlaClient=None,
                       OLADNotRunningException=Exception)
    ola_mod.OlaClient = client_mod
