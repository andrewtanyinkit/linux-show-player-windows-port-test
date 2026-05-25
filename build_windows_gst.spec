# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec — Windows build WITH bundled GStreamer audio support
#
# Prerequisites (must be installed BEFORE running this):
#   1.  GStreamer MSVC runtime + devel packages (via chocolatey or the
#       official Windows installer from https://gstreamer.freedesktop.org/)
#         choco install gstreamer gstreamer-devel
#   2.  Python packages:
#         pip install -r requirements-windows.txt PyGObject
#
# Build command (run from repo root on Windows):
#   pyinstaller build_windows_gst.spec --noconfirm --clean
#
# Output: dist/LinuxShowPlayer-audio/  (directory — zip before distributing)

import glob
import os
import sys
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH)

# ── Locate GStreamer installation ─────────────────────────────────────────────
# Try well-known locations in priority order.
_GST_CANDIDATES = [
    os.environ.get("GSTREAMER_1_0_ROOT_MSVC_X86_64", ""),
    os.environ.get("GSTREAMER_1_0_ROOT_X86_64", ""),
    r"C:\gstreamer\1.0\msvc_x86_64",
    r"C:\gstreamer\1.0\x86_64",
    r"C:\Program Files\gstreamer\1.0\msvc_x86_64",
]
GST_ROOT = next(
    (p for p in _GST_CANDIDATES if p and os.path.isdir(p)), None
)
if GST_ROOT is None:
    raise RuntimeError(
        "GStreamer not found. Install it first:\n"
        "  choco install gstreamer gstreamer-devel\n"
        "or set GSTREAMER_1_0_ROOT_MSVC_X86_64 environment variable."
    )

GST_BIN     = os.path.join(GST_ROOT, "bin")
GST_PLUGINS = os.path.join(GST_ROOT, "lib", "gstreamer-1.0")
GST_TYPELIB = os.path.join(GST_ROOT, "lib", "girepository-1.0")

print(f"[build_windows_gst.spec] Using GStreamer root: {GST_ROOT}")


def _collect(src_glob, dest_dir):
    """Return (src, dest) tuples for all files matching a glob."""
    return [(f, dest_dir) for f in glob.glob(src_glob, recursive=True)
            if os.path.isfile(f)]


# ── Static data files (same as the non-GStreamer build) ──────────────────────
def _d(src_rel, dest_rel):
    src = ROOT / src_rel
    return (str(src), dest_rel) if src.exists() else None


_static_datas = [
    _d("lisp/default.json",                        "lisp"),
    _d("lisp/ui/themes/dark",                       "lisp/ui/themes/dark"),
    _d("lisp/ui/themes/light",                      "lisp/ui/themes/light"),
    _d("lisp/ui/icons/lisp",                        "lisp/ui/icons/lisp"),
    _d("lisp/ui/icons/Numix",                       "lisp/ui/icons/Numix"),
    _d("lisp/i18n/qm",                              "lisp/i18n/qm"),
    _d("lisp/plugins/cache_manager/default.json",   "lisp/plugins/cache_manager"),
    _d("lisp/plugins/cart_layout/default.json",     "lisp/plugins/cart_layout"),
    _d("lisp/plugins/controller/default.json",      "lisp/plugins/controller"),
    _d("lisp/plugins/gst_backend/default.json",     "lisp/plugins/gst_backend"),
    _d("lisp/plugins/list_layout/default.json",     "lisp/plugins/list_layout"),
    _d("lisp/plugins/midi/default.json",            "lisp/plugins/midi"),
    _d("lisp/plugins/network/default.json",         "lisp/plugins/network"),
    _d("lisp/plugins/osc/default.json",             "lisp/plugins/osc"),
    _d("lisp/plugins/synchronizer/default.json",    "lisp/plugins/synchronizer"),
    _d("lisp/plugins/timecode/default.json",        "lisp/plugins/timecode"),
]

# ── GStreamer data: typelibs, registry helpers ────────────────────────────────
# Core typelibs needed for gi.repository.Gst etc.
_REQUIRED_TYPELIBS = [
    "GLib-2.0.typelib",
    "GModule-2.0.typelib",
    "GObject-2.0.typelib",
    "Gio-2.0.typelib",
    "Gst-1.0.typelib",
    "GstBase-1.0.typelib",
    "GstController-1.0.typelib",
    "GstNet-1.0.typelib",
    "GstPbutils-1.0.typelib",
    "GstApp-1.0.typelib",
    "GstAudio-1.0.typelib",
    "GstVideo-1.0.typelib",
    "GstTag-1.0.typelib",
    "GstCheck-1.0.typelib",
]
_typelib_datas = []
for _tl in _REQUIRED_TYPELIBS:
    _path = os.path.join(GST_TYPELIB, _tl)
    if os.path.isfile(_path):
        _typelib_datas.append((_path, "gi/repository"))

# Also grab any remaining typelibs (harmless extras)
for _path in glob.glob(os.path.join(GST_TYPELIB, "*.typelib")):
    _entry = (_path, "gi/repository")
    if _entry not in _typelib_datas:
        _typelib_datas.append(_entry)

# ── GStreamer plugin DLLs — include audio-relevant plugins ───────────────────
# We collect all plugins to avoid a massive exclusion list; storage is cheap.
_gst_plugin_datas = _collect(os.path.join(GST_PLUGINS, "*.dll"),
                              "gstreamer-1.0")

# ── GStreamer runtime DLLs from bin/ ─────────────────────────────────────────
# Collect all DLLs — PyInstaller's binary dependency analysis won't find them
# automatically because they are loaded at runtime by GStreamer's plugin scanner.
_gst_bin_binaries = []
for _dll in glob.glob(os.path.join(GST_BIN, "*.dll")):
    _gst_bin_binaries.append((_dll, "."))

datas = (
    [d for d in _static_datas if d is not None]
    + _typelib_datas
    + _gst_plugin_datas
)

binaries = _gst_bin_binaries

# ── Hidden imports ────────────────────────────────────────────────────────────
hidden_imports = [
    # ── Core lisp ────────────────────────────────────────────────────────────
    "lisp", "lisp.application",
    "lisp.backend", "lisp.backend.audio_utils", "lisp.backend.backend",
    "lisp.backend.media", "lisp.backend.media_element", "lisp.backend.waveform",
    "lisp.command", "lisp.command.command", "lisp.command.cue",
    "lisp.command.layout", "lisp.command.model", "lisp.command.stack",
    "lisp.core", "lisp.core.class_based_registry", "lisp.core.clock",
    "lisp.core.configuration", "lisp.core.decorators", "lisp.core.dicttree",
    "lisp.core.fade_functions", "lisp.core.fader", "lisp.core.has_properties",
    "lisp.core.loading", "lisp.core.model", "lisp.core.model_adapter",
    "lisp.core.plugin", "lisp.core.plugin_loader", "lisp.core.properties",
    "lisp.core.proxy_model", "lisp.core.qmeta", "lisp.core.rwait",
    "lisp.core.session", "lisp.core.session_uri", "lisp.core.signal",
    "lisp.core.singleton", "lisp.core.util",
    "lisp.cues", "lisp.cues.cue", "lisp.cues.cue_factory",
    "lisp.cues.cue_model", "lisp.cues.cue_time", "lisp.cues.media_cue",
    "lisp.layout", "lisp.layout.cue_layout", "lisp.layout.cue_menu",
    # ── UI ───────────────────────────────────────────────────────────────────
    "lisp.ui", "lisp.ui.about", "lisp.ui.cuelistdialog", "lisp.ui.icons",
    "lisp.ui.layoutselect",
    "lisp.ui.logging", "lisp.ui.logging.common", "lisp.ui.logging.details",
    "lisp.ui.logging.dialog", "lisp.ui.logging.handler",
    "lisp.ui.logging.models", "lisp.ui.logging.status", "lisp.ui.logging.viewer",
    "lisp.ui.mainwindow", "lisp.ui.qdelegates", "lisp.ui.qmodels",
    "lisp.ui.settings", "lisp.ui.settings.app_configuration",
    "lisp.ui.settings.app_pages", "lisp.ui.settings.app_pages.cue",
    "lisp.ui.settings.app_pages.general", "lisp.ui.settings.app_pages.layouts",
    "lisp.ui.settings.cue_pages", "lisp.ui.settings.cue_pages.cue_appearance",
    "lisp.ui.settings.cue_pages.cue_general",
    "lisp.ui.settings.cue_pages.media_cue",
    "lisp.ui.settings.cue_settings", "lisp.ui.settings.pages",
    "lisp.ui.themes", "lisp.ui.themes.dark", "lisp.ui.themes.dark.dark",
    "lisp.ui.themes.dark.assets", "lisp.ui.themes.light",
    "lisp.ui.themes.light.light", "lisp.ui.ui_utils",
    "lisp.ui.widgets", "lisp.ui.widgets.colorbutton",
    "lisp.ui.widgets.cue_actions", "lisp.ui.widgets.cue_next_actions",
    "lisp.ui.widgets.digitalclock", "lisp.ui.widgets.dynamicfontsize",
    "lisp.ui.widgets.elidedlabel", "lisp.ui.widgets.fades",
    "lisp.ui.widgets.hotkeyedit", "lisp.ui.widgets.locales",
    "lisp.ui.widgets.pagestreewidget", "lisp.ui.widgets.qclicklabel",
    "lisp.ui.widgets.qclickslider", "lisp.ui.widgets.qeditabletabbar",
    "lisp.ui.widgets.qenumcombobox", "lisp.ui.widgets.qiconpushbutton",
    "lisp.ui.widgets.qmutebutton", "lisp.ui.widgets.qsteptimeedit",
    "lisp.ui.widgets.qstyledslider", "lisp.ui.widgets.qvertiacallabel",
    "lisp.ui.widgets.qwaitingspinner", "lisp.ui.widgets.waveform",
    # ── Plugins ──────────────────────────────────────────────────────────────
    "lisp.plugins",
    "lisp.plugins.action_cues", "lisp.plugins.action_cues.collection_cue",
    "lisp.plugins.action_cues.command_cue",
    "lisp.plugins.action_cues.index_action_cue",
    "lisp.plugins.action_cues.seek_cue", "lisp.plugins.action_cues.stop_all",
    "lisp.plugins.action_cues.volume_control",
    "lisp.plugins.cache_manager", "lisp.plugins.cache_manager.cache_manager",
    "lisp.plugins.cart_layout", "lisp.plugins.cart_layout.cue_widget",
    "lisp.plugins.cart_layout.layout", "lisp.plugins.cart_layout.model",
    "lisp.plugins.cart_layout.page_widget", "lisp.plugins.cart_layout.settings",
    "lisp.plugins.cart_layout.tab_widget",
    "lisp.plugins.controller", "lisp.plugins.controller.common",
    "lisp.plugins.controller.controller",
    "lisp.plugins.controller.controller_settings",
    "lisp.plugins.controller.protocol", "lisp.plugins.controller.protocols",
    "lisp.plugins.controller.protocols.keyboard",
    "lisp.plugins.controller.protocols.midi",
    "lisp.plugins.controller.protocols.osc",
    # GStreamer audio backend — fully included in this build
    "lisp.plugins.gst_backend",
    "lisp.plugins.gst_backend.gi_repository",
    "lisp.plugins.gst_backend.gst_backend",
    "lisp.plugins.gst_backend.gst_element",
    "lisp.plugins.gst_backend.gst_fader",
    "lisp.plugins.gst_backend.gst_media",
    "lisp.plugins.gst_backend.gst_media_cue",
    "lisp.plugins.gst_backend.gst_media_settings",
    "lisp.plugins.gst_backend.gst_pipe_edit",
    "lisp.plugins.gst_backend.gst_properties",
    "lisp.plugins.gst_backend.gst_settings",
    "lisp.plugins.gst_backend.gst_utils",
    "lisp.plugins.gst_backend.gst_waveform",
    "lisp.plugins.gst_backend.elements",
    "lisp.plugins.gst_backend.elements.audio_dynamic",
    "lisp.plugins.gst_backend.elements.audio_pan",
    "lisp.plugins.gst_backend.elements.auto_sink",
    "lisp.plugins.gst_backend.elements.auto_src",
    "lisp.plugins.gst_backend.elements.db_meter",
    "lisp.plugins.gst_backend.elements.equalizer10",
    "lisp.plugins.gst_backend.elements.pitch",
    "lisp.plugins.gst_backend.elements.preset_src",
    "lisp.plugins.gst_backend.elements.speed",
    "lisp.plugins.gst_backend.elements.uri_input",
    "lisp.plugins.gst_backend.elements.user_element",
    "lisp.plugins.gst_backend.elements.volume",
    "lisp.plugins.gst_backend.config",
    "lisp.plugins.gst_backend.settings",
    "lisp.plugins.gst_backend.settings.audio_dynamic",
    "lisp.plugins.gst_backend.settings.audio_pan",
    "lisp.plugins.gst_backend.settings.db_meter",
    "lisp.plugins.gst_backend.settings.equalizer10",
    "lisp.plugins.gst_backend.settings.pitch",
    "lisp.plugins.gst_backend.settings.preset_src",
    "lisp.plugins.gst_backend.settings.speed",
    "lisp.plugins.gst_backend.settings.uri_input",
    "lisp.plugins.gst_backend.settings.user_element",
    "lisp.plugins.gst_backend.settings.volume",
    # Replay gain also needs GStreamer
    "lisp.plugins.replay_gain",
    "lisp.plugins.replay_gain.replay_gain",
    "lisp.plugins.replay_gain.gain_ui",
    "lisp.plugins.list_layout", "lisp.plugins.list_layout.control_buttons",
    "lisp.plugins.list_layout.info_panel", "lisp.plugins.list_layout.layout",
    "lisp.plugins.list_layout.list_view", "lisp.plugins.list_layout.list_widgets",
    "lisp.plugins.list_layout.models", "lisp.plugins.list_layout.playing_view",
    "lisp.plugins.list_layout.playing_widgets", "lisp.plugins.list_layout.settings",
    "lisp.plugins.list_layout.view",
    "lisp.plugins.media_info", "lisp.plugins.media_info.media_info",
    "lisp.plugins.midi", "lisp.plugins.midi.midi", "lisp.plugins.midi.midi_cue",
    "lisp.plugins.midi.midi_io", "lisp.plugins.midi.midi_settings",
    "lisp.plugins.midi.midi_utils", "lisp.plugins.midi.port_monitor",
    "lisp.plugins.midi.widgets",
    "lisp.plugins.network", "lisp.plugins.network.api.cues",
    "lisp.plugins.network.api.layout", "lisp.plugins.network.discovery",
    "lisp.plugins.network.discovery_dialogs", "lisp.plugins.network.endpoint",
    "lisp.plugins.network.network", "lisp.plugins.network.server",
    "lisp.plugins.osc", "lisp.plugins.osc.osc", "lisp.plugins.osc.osc_cue",
    "lisp.plugins.osc.osc_delegate", "lisp.plugins.osc.osc_server",
    "lisp.plugins.osc.osc_settings",
    "lisp.plugins.presets", "lisp.plugins.presets.lib",
    "lisp.plugins.presets.presets", "lisp.plugins.presets.presets_ui",
    "lisp.plugins.rename_cues", "lisp.plugins.rename_cues.command",
    "lisp.plugins.rename_cues.rename_cues", "lisp.plugins.rename_cues.rename_ui",
    "lisp.plugins.synchronizer", "lisp.plugins.synchronizer.synchronizer",
    "lisp.plugins.timecode", "lisp.plugins.timecode.cue_tracker",
    "lisp.plugins.timecode.protocol", "lisp.plugins.timecode.protocols.midi",
    "lisp.plugins.timecode.settings", "lisp.plugins.timecode.timecode",
    "lisp.plugins.triggers", "lisp.plugins.triggers.triggers",
    "lisp.plugins.triggers.triggers_handler",
    "lisp.plugins.triggers.triggers_settings",
    # ── GI / GStreamer Python bindings (real gi from PyGObject) ─────────────
    "gi", "gi.repository", "gi.repository.GLib", "gi.repository.GObject",
    "gi.repository.Gio", "gi.repository.Gst", "gi.repository.GstBase",
    "gi.repository.GstController", "gi.repository.GstPbutils",
    "gi.repository.GstApp", "gi.repository.GstAudio",
    "gi._gi",
    # ── Third-party ──────────────────────────────────────────────────────────
    "mido", "mido.backends.rtmidi", "mido.backends.backend",
    "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
    "PyQt5.QtNetwork", "PyQt5.QtXml", "PyQt5.QtSvg",
    "PyQt5.QtPrintSupport", "PyQt5.sip",
    "pkg_resources", "appdirs", "sortedcontainers",
    "sortedcontainers.sortedlist", "sortedcontainers.sorteddict",
    "qdigitalmeter", "falcon", "falcon.app", "falcon.request", "falcon.response",
    "requests", "humanize", "numpy", "logging.handlers",
    "importlib.metadata", "importlib.resources",
]

excludes = [
    # Pure Linux audio APIs — not on Windows
    "pyalsa", "alsaseq",
    "jack",
    "pyliblo3", "liblo",
    "ola",
    # Linux-only GStreamer elements (Windows has directsound/wasapi instead)
    "lisp.plugins.gst_backend.elements.alsa_sink",
    "lisp.plugins.gst_backend.elements.pulse_sink",
    "lisp.plugins.gst_backend.elements.jack_sink",
    "lisp.plugins.gst_backend.config.alsa_sink",
    "lisp.plugins.gst_backend.settings.alsa_sink",
    "lisp.plugins.gst_backend.settings.jack_sink",
    "lisp.plugins.timecode.protocols.artnet",
    # Unused stdlib
    "tkinter", "matplotlib", "scipy", "PIL",
    "test", "unittest", "xmlrpc",
    # NOTE: do NOT exclude 'distutils' — PyInstaller has its own hook that
    # aliases it; excluding it causes a ValueError during analysis.
]

a = Analysis(
    [str(ROOT / "lisp" / "main.py")],
    pathex=[str(ROOT), GST_BIN],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "windows_runtime_hook_gst.py")],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Build as a directory (--onedir) ──────────────────────────────────────────
# GStreamer bundles hundreds of DLLs — single-file would be very slow to start
# because it has to extract everything on each launch. A directory is fast and
# can be zipped for distribution.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LinuxShowPlayer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LinuxShowPlayer-audio",
)
