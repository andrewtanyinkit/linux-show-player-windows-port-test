# PyInstaller runtime hook — Windows build WITH bundled GStreamer audio.
# Runs before any application code when launched from the bundled directory.
# Must configure GStreamer environment BEFORE gi / Gst are imported.

import os
import sys
import tempfile
import types


def _stub(name, **attrs):
    mod = types.ModuleType(name)
    mod.__spec__ = None
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# ── GStreamer / GI path setup ─────────────────────────────────────────────────
# sys._MEIPASS is the directory where PyInstaller extracts bundled files.
_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# GStreamer plugin DLLs bundled into gstreamer-1.0/ inside the distribution
_gst_plugins = os.path.join(_base, "gstreamer-1.0")

# GI typelib files bundled into gi/repository/ (matches the datas path)
_gi_typelibs = os.path.join(_base, "gi", "repository")

# Point GStreamer to the bundled plugins — clear system path so it never
# tries to scan a system-installed GStreamer that may not exist.
os.environ["GST_PLUGIN_PATH_1_0"]    = _gst_plugins
os.environ["GST_PLUGIN_PATH"]        = _gst_plugins
os.environ["GST_PLUGIN_SYSTEM_PATH_1_0"] = ""
os.environ["GST_PLUGIN_SYSTEM_PATH"] = ""

# Use a per-session registry in the user's temp dir so the first-run
# plugin scan result is cached and startup is fast from the second launch on.
_registry = os.path.join(
    tempfile.gettempdir(), "lisp_gst_registry_1_0.bin"
)
os.environ["GST_REGISTRY_1_0"] = _registry
os.environ["GST_REGISTRY"]     = _registry

# Tell GI where the typelib files live inside the bundle.
os.environ["GI_TYPELIB_PATH"] = _gi_typelibs

# Add the bundle root to PATH so Windows can resolve all bundled DLLs.
os.environ["PATH"] = _base + os.pathsep + os.environ.get("PATH", "")

# ── Stub Linux-only packages (same as the non-GStreamer hook) ─────────────────
for _name in ("pyalsa", "pyalsa.alsaseq"):
    if _name not in sys.modules:
        _stub(_name, SequencerError=Exception)

for _name in ("jack",):
    if _name not in sys.modules:
        _stub(_name)

for _name in ("liblo", "pyliblo3"):
    if _name not in sys.modules:
        _stub(_name, ServerThread=None, ServerError=Exception,
              Address=None, send=None)

for _name in ("ola", "ola.OlaClient"):
    if _name not in sys.modules:
        _s = _stub(_name, OlaClient=None, OLADNotRunningException=Exception)
