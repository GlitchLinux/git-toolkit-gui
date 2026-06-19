#!/usr/bin/env python3
"""
Glitch-Toolkit GUI - PyQt5 launcher for the Glitch-Toolkit repo.
Browse, search, run, copy, and export scripts with a compact dark UI.
"""

import sys
import os
import json
import subprocess
import threading
import shutil
import time
import signal
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QFileDialog, QMessageBox, QStatusBar, QMenu, QAction,
    QAbstractItemView, QDialog, QFormLayout, QComboBox, QCheckBox,
    QSpinBox, QDialogButtonBox, QGroupBox, QColorDialog, QGridLayout
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QKeySequence

# ---------------------------------------------------------------------------
#  Embedded app icon (base64-encoded PNG)
#  Paste raw base64 data between the quotes - no line breaks
# ---------------------------------------------------------------------------
APP_ICON_128 = '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'
APP_ICON_64  = 'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAHYAAAB2AH6XKZyAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAACq9JREFUeJztm11MlFcax3/vOx8MzMDwVRRmEAvqbGorH1uxTdyikJm4YSWxdxXa7IU3mzS9Mr3qxprUZJNuYuhHlOyFuxrIxguxKa2BqlVjXVkJ1AyLIiyE0YFqAWGcdz7fmXcvcN4ygJouLzObrf8rOGfOOf/nmec85znPcwae4zme45cMYdHfr4qieFCn021XFCUzbYzWEIIgBGOx2D/j8fjHQD/8pIAWQRD+VlxcHN+wYYPeYDCkj+UaIhqN4vF45KmpKUFRlHeADgEoEwRhZPv27Yaqqqp0c0wJBgYG6OvriyiKskkE9pvNZqWysjLdvFKGqqoqzGYzwH49UF5UVGQQhJ/cQTwex+/3A2CxWBBFMWmCQCCALMsYjUZMJlNSXzQaJRgMIooiZrOZxfMqioIkScTj8bWS7YlYLIcgCBQVFRn8fv8mPaDX6/UqS6/Xy/meHsLRKAAZBgMNTid2ux1Zluk+14V36oE68a8cm3mjbjcAQ0NDfHftO5S4AoDZksXvGvditVrx+/18/fXXzM3NpUrmJGRkZOB0OikpKQHgscx6/dIP3vrXIHsqbPzxN9UA/OnqTfrcbux2O1NTU0zPzHCzczeWLB23x/w0/uE6Nb/ejsVi4ab7exre2UqNqwwlDh2H/8Hw8DC1tbWMjo5SWFjIxYsX0S9fds1x6NAhbt68qSoggWVMYrJMRW4BZdZsACryc+iduw8smHemSc+2LTkAWLL0ajuAHJVZtzGH/GILALnrspDn5IU+WWb9+vVs2rRpLeR7JjZv3kx/f/+ydnFpgyAIRGIx9f+wHEMQF3aIKIrIsTjxxyYejsTV9sRYOfrT/pYjcdUHCIJAJBLRSp6fjVAolOSPElhmAcX2Uo719tJ5xwPAfb/Eq69uB6CoqIhYTGB9XQ8mo45HUpSCfCvZ2QvWYreXcubPffT8ZRBFUZifCfDbPQtHq81mo6urC4fDscyppgL379+ntrZ2WbsAnNiyZcvvd+3apTZOTk4yPz8PgNVqTdo3fr+fyclJYrEYBoOB0tJSMjIygIXTw+PxEAwGEQSBwsJCCgsL1bGzs7M8ePAARVHWRsqnYKkcly5d4s6dO39d0RuVlJQscxYJWCwWtmzZsmKfKIps3LjxiSTy8/PJz8//GbTXHqm3xf8x6GHBi/t8vnRzSSkSJ5ceYHx8nPHx8bQSShf0AI2NjXzwwQfp5pJSfPTRR3z11VcLCrBYLJSVlaWbU0phsSwEa794J/iLV0DqbyUsXKfv3bvHw4cPAcjLy8Nut5OVlZVyLilXQDgcpqGhgYmJiaT2srIyLl26pEaVqULKFdDW1sbMzAzNzc2JrAySJPHFF1/Q1tbGe++9l1I+a+YDHj16xOnTp7l165Ya+w8ODtLa2kpNTY0qPIDZbKampobW1lYGBweBhezRrVu3OH36NI8ePVormmtjAV6vl/379+PxeAiHwxQUFFBSUoLb7ebFF1/E4XAsG+NwOLh79y4ul4tXXnmFyclJZmZmyMjI4PPPP6ejowObzaY5V80VMDU1RWNjIyaTibfeeotIJILX62V+fp4333wz6Xa4GIIg4HQ6mZ6eZmxsjJdffhmbzYbRaOTChQs0NjZy7tw5iouLNeWrqQIkSaK5uZmMjAxcLheiKGI0Glf8xp+EpVdoAJfLRXd3N83NzXz55ZdJ22e10NQHuN1ubt++TV1d3VOTHoqiEIlECIVCBINBIpHIU3MEOp2OXbt2cfv2bdxut5aUtbWAyspKDAYDs7OzK57psVgMSZKeKLDJZCIrKwudTresb3Z2Fr1ez7Zt27SkrK0FZGZmUl1djdfrXdYXiUSYm5sjHA6jKAqyLOPz+fD5fMQe5yBDoRAPHz4kHA4vG+/1eqmurtY8WNLcCVqtVjweT1JbOBxW8w2SJDE8PIzX60WWFzLGer0em82Gw+HAbDbj8/mwWq0YjUZ1jlAoxAsvvKA1XW0tYHh4mIsXL1JRUaG2xeNx9Ryfnp7m8uXLrF+/nhMnTuB2u3G73Zw4cYJ169Zx5coVpqenAfD5fEkVpIqKCr799luGh4e1pKyNAvx+P0eOHMHlclFaWordblf7AoEAiqIQDAa5ceMGb7/9NmfOnKGhoYGCggIKCgpoaGigs7OT5uZm+vr6CIVCKIpCIBBQ57Hb7ZSWluJyuThy5IhaulstNFGA0+mkvb2duro6XC5XUl9iP4+MjFBRUcGHH364Yn5eEAQOHz5MeXk5d+7cARbMfjFcLhd1dXW0t7fjdDq1oL56BQQCASYmJqivr6e8vDypT5Zl1YynpqY4cODAU49HURQ5cOAAP/zwA4DqLBejvLyc+vp6JiYmkCRptfRXr4DElXalW1xCeFmWCQQCbN269ZnzvfTSS0iSpAq+0nGZWEuLQuuqFZAodD4tkEmY/ErH21JEIhEEQVhxmySQWEuLIuuqFZCXlwes/G0kAhqdTkdubi69vb3PnO/69evk5uYmjV2KxFqJtVeDVSvAaDSyd+9eenp6uHbtWpLj0ul0qgA2m43jx4+rJbeVMDc3x/Hjx9Vbn06nS/IZoVCIa9eu0dPTw969e5PihP8WmpwCbW1tnDp1CkmSOHv2bJLjysxceHBWUVFBLBajpaWFmZmZZXPMzMzQ0tKCoiiqM02MhQU/cvbsWSRJ4tSpU7S1tWlBXbtIcPfu3XR3d1NVVcXY2JhaP8zMzCQYDAKwY8cObty4weuvv05LSwvV1QuPMPr7+2lvb8dkMlFbW6tazuLnN2NjY8RiMbq7u9WUthbQNBS2WCy4XC4GBweTCqg5OTnMz8+TmZnJzp078Xg8dHZ2cvLkSQCys7PZvHkzGzZsQBRFRFHEarUmOcJ79+7hdDo1FR7W4C4wNDS0rAKs1+vJzc3F5/MhyzIbN258YhVZr9eTk5OzzPnl5eUxNDSkNV1t7wI//vgjIyMjK6auEidBdnY2Kz3ENBgMZGdnk5eXt6Lnt9vtjIyM8ODBg2V9q4GmFjA2NoaiKE+M9gRBwGQyYTKZUBRFDZREUXzquZ/4jKIojI+PU1RUpBlnTS2gtraWffv2cf78+WdeVgRBUJ3ds4T3+/1888037Nu3b8VnLquBphYgCAJHjx6lubmZrq4u3njjDSRJwuv1IkkSpaWlOByOJxY/wuEww8PD3L17F7PZjM1mw2w2c/nyZSorKzl69OgzlfVzoXldwGg00tHRgcvloquri/7+fhwOB01NTYyOjtLZ2ak+TliMaDRKZ2cno6OjNDU14XA4GBgYoKuriz179tDe3q5J4LMUa1IXMBgMfPLJJ7z//vuUlJSoPuHgwYPs3LmTgYGBZaY8MDCA2Wzm6tWragAUj8eZnJxMyi9ojTUtjS0lnpmZyaFDh3j33XfJz89X83uBQIDBwUE+++yzpOhPFMU1FR7SUBtsamri3LlzXLlyRc0T5uTk0NjYSFNTU6rppKc8fuzYsXQsuyJEQA4EAql/uZhmPJZZFoF/DwwMRNPxhj9diMfj9Pf3R4EREeiYnJzk008/TTevlKG1tZWpqSl4/JshgP2iKJ587bXX4vX19YacnJw00ls7+Hw+Lly4IPf29grxeLwF+PvisKrGYDAc1Ov1O4D/y5/NAUFZlq9Ho9GPge/TTeY5nuM50o//ADuRJPAdGXJHAAAAAElFTkSuQmCC'

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
REPO_URL  = "https://github.com/GlitchLinux/gLiTcH-ToolKit.git"
REPO_DIR  = Path("/tmp/gLiTcH-ToolKit")
ICON_DIR  = Path("/tmp/toolkit-icons")
ICON_URL  = "https://glitchlinux.wtf/FILES/toolkit-icons"
ICON_LIST = [
    "txt.png", "terminal-w.png", "sh.png", "py.png", "pf2.png",
    "iso_file.png", "file.png", "exe.png", "cfg.png", "c.png", "bin.png",
]
CONFIG_FILE = Path.home() / ".config" / "glitch-toolkit-gui.json"

EXT_ICON_MAP = {
    ".sh": "sh.png", ".py": "py.png", ".txt": "txt.png", ".c": "c.png",
    ".cfg": "cfg.png", ".conf": "cfg.png", ".bin": "bin.png",
    ".exe": "exe.png", ".iso": "iso_file.png", ".pf2": "pf2.png",
    ".deb": "file.png", ".desktop": "file.png",
}
DEFAULT_ICON = "terminal-w.png"

# Available terminals (display name -> binary)
TERMINALS = {
    "xfce4-terminal": "xfce4-terminal",
    "gnome-terminal": "gnome-terminal",
    "konsole":        "konsole",
    "mate-terminal":  "mate-terminal",
    "lxterminal":     "lxterminal",
    "alacritty":      "alacritty",
    "kitty":          "kitty",
    "xterm":          "xterm",
}

# Preset color themes: name -> (bg, bg_alt, search_bg, border, hover, accent_normal, accent_sudo, sel_normal, sel_sudo)
COLOR_PRESETS = {
    "Default Dark": {
        "bg": "#0e0e18", "bg_alt": "#141424", "search_bg": "#16162a",
        "border": "#2a2a3a", "hover": "#1a1a30", "fg": "#c8c8d4",
        "accent": "#00ff0b", "accent_sudo": "#db00b9",
        "sel": "#1e3a1e", "sel_sudo": "#3a1e36",
    },
    "Charcoal": {
        "bg": "#1a1a1a", "bg_alt": "#222222", "search_bg": "#1e1e1e",
        "border": "#3a3a3a", "hover": "#2a2a2a", "fg": "#d0d0d0",
        "accent": "#4fc3f7", "accent_sudo": "#ff5252",
        "sel": "#1a2e3e", "sel_sudo": "#3e1a1a",
    },
    "Midnight Blue": {
        "bg": "#0a0e1a", "bg_alt": "#101828", "search_bg": "#0e1424",
        "border": "#1e2e4a", "hover": "#141e34", "fg": "#b8c4d8",
        "accent": "#64ffda", "accent_sudo": "#ff6ec7",
        "sel": "#0e2e2e", "sel_sudo": "#2e0e28",
    },
    "Forest": {
        "bg": "#0a120a", "bg_alt": "#101a10", "search_bg": "#0e160e",
        "border": "#1e3a1e", "hover": "#142414", "fg": "#b8d4b8",
        "accent": "#a0ff60", "accent_sudo": "#ffa040",
        "sel": "#1a3a1a", "sel_sudo": "#3a2a1a",
    },
    "Crimson": {
        "bg": "#140a0a", "bg_alt": "#1c1010", "search_bg": "#180e0e",
        "border": "#3a1e1e", "hover": "#241414", "fg": "#d4b8b8",
        "accent": "#ff4060", "accent_sudo": "#40c0ff",
        "sel": "#3a1a1a", "sel_sudo": "#1a2a3a",
    },
}


# ---------------------------------------------------------------------------
#  Settings manager
# ---------------------------------------------------------------------------
class Settings:
    DEFAULTS = {
        "terminal":    "auto",
        "term_launch": "minimized",   # minimized | small | fullscreen
        "font_size":   15,
        "show_icons":  True,
        "color_theme": "Default Dark",
        "custom_accent": "",
        "custom_accent_sudo": "",
    }

    def __init__(self):
        self.data = dict(self.DEFAULTS)
        self.load()

    def load(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    saved = json.load(f)
                self.data.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def __getitem__(self, key):
        return self.data.get(key, self.DEFAULTS.get(key))

    def __setitem__(self, key, val):
        self.data[key] = val

    def theme(self):
        """Return the active color dict."""
        name = self.data.get("color_theme", "Default Dark")
        t = COLOR_PRESETS.get(name, COLOR_PRESETS["Default Dark"]).copy()
        # Apply custom accent overrides if set
        if self.data.get("custom_accent"):
            t["accent"] = self.data["custom_accent"]
        if self.data.get("custom_accent_sudo"):
            t["accent_sudo"] = self.data["custom_accent_sudo"]
        return t


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
def build_app_icon():
    """Build a QIcon from embedded base64 PNG data."""
    import base64
    icon = QIcon()
    for b64, size in [(APP_ICON_128, 128), (APP_ICON_64, 64)]:
        if b64 and not b64.startswith("PASTE_"):
            raw = base64.b64decode(b64)
            px = QPixmap()
            px.loadFromData(QByteArray(raw), "PNG")
            icon.addPixmap(px)
    return icon


def detect_terminal():
    for term in TERMINALS.values():
        if subprocess.run(["which", term], capture_output=True).returncode == 0:
            return term
    return "xterm"


def resolve_terminal(settings):
    t = settings["terminal"]
    if t == "auto":
        return detect_terminal()
    # Verify it exists
    if subprocess.run(["which", t], capture_output=True).returncode == 0:
        return t
    return detect_terminal()


def icon_for_file(filename):
    ext = Path(filename).suffix.lower()
    icon_name = EXT_ICON_MAP.get(ext, DEFAULT_ICON)
    icon_path = ICON_DIR / icon_name
    if icon_path.exists():
        return str(icon_path)
    return None


# ---------------------------------------------------------------------------
#  Settings Dialog
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(360)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # -- Terminal
        grp_term = QGroupBox("Terminal")
        gl = QFormLayout(grp_term)
        self.term_combo = QComboBox()
        self.term_combo.addItem("Auto-detect", "auto")
        for name, binary in TERMINALS.items():
            self.term_combo.addItem(name, binary)
        # Set current
        cur = self.settings["terminal"]
        idx = self.term_combo.findData(cur)
        if idx >= 0:
            self.term_combo.setCurrentIndex(idx)
        gl.addRow("Preferred:", self.term_combo)

        self.launch_combo = QComboBox()
        self.launch_combo.addItem("Minimized", "minimized")
        self.launch_combo.addItem("Small window", "small")
        self.launch_combo.addItem("Fullscreen", "fullscreen")
        cur_launch = self.settings["term_launch"]
        idx2 = self.launch_combo.findData(cur_launch)
        if idx2 >= 0:
            self.launch_combo.setCurrentIndex(idx2)
        gl.addRow("Launch mode:", self.launch_combo)

        layout.addWidget(grp_term)

        # -- Appearance
        grp_look = QGroupBox("Appearance")
        al = QFormLayout(grp_look)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 28)
        self.font_spin.setValue(self.settings["font_size"])
        self.font_spin.setSuffix(" px")
        al.addRow("Font size:", self.font_spin)

        self.icons_chk = QCheckBox("Show file-type icons")
        self.icons_chk.setChecked(self.settings["show_icons"])
        al.addRow(self.icons_chk)

        layout.addWidget(grp_look)

        # -- Colors
        grp_color = QGroupBox("Color Theme")
        cl = QVBoxLayout(grp_color)

        self.theme_combo = QComboBox()
        for name in COLOR_PRESETS:
            self.theme_combo.addItem(name)
        cur_theme = self.settings["color_theme"]
        idx = self.theme_combo.findText(cur_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        cl.addWidget(self.theme_combo)

        # Custom accent overrides
        accent_row = QHBoxLayout()
        accent_row.setSpacing(6)

        self.accent_btn = QPushButton("Normal accent")
        self.accent_btn.setToolTip("Override normal-mode highlight color")
        self.accent_btn.clicked.connect(self._pick_accent)
        self._accent_color = self.settings["custom_accent"] or ""
        self._update_accent_preview()
        accent_row.addWidget(self.accent_btn)

        self.accent_sudo_btn = QPushButton("Sudo accent")
        self.accent_sudo_btn.setToolTip("Override sudo-mode highlight color")
        self.accent_sudo_btn.clicked.connect(self._pick_accent_sudo)
        self._accent_sudo_color = self.settings["custom_accent_sudo"] or ""
        self._update_accent_sudo_preview()
        accent_row.addWidget(self.accent_sudo_btn)

        self.reset_accent_btn = QPushButton("Reset")
        self.reset_accent_btn.setFixedWidth(60)
        self.reset_accent_btn.clicked.connect(self._reset_accents)
        accent_row.addWidget(self.reset_accent_btn)

        cl.addLayout(accent_row)
        layout.addWidget(grp_color)

        # -- Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save_and_close)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _pick_accent(self):
        c = QColorDialog.getColor(
            QColor(self._accent_color) if self._accent_color else QColor("#00ff0b"),
            self, "Normal mode accent"
        )
        if c.isValid():
            self._accent_color = c.name()
            self._update_accent_preview()

    def _pick_accent_sudo(self):
        c = QColorDialog.getColor(
            QColor(self._accent_sudo_color) if self._accent_sudo_color else QColor("#db00b9"),
            self, "Sudo mode accent"
        )
        if c.isValid():
            self._accent_sudo_color = c.name()
            self._update_accent_sudo_preview()

    def _reset_accents(self):
        self._accent_color = ""
        self._accent_sudo_color = ""
        self._update_accent_preview()
        self._update_accent_sudo_preview()

    def _update_accent_preview(self):
        if self._accent_color:
            self.accent_btn.setStyleSheet(
                f"QPushButton {{ border-left: 4px solid {self._accent_color}; }}"
            )
        else:
            self.accent_btn.setStyleSheet("")

    def _update_accent_sudo_preview(self):
        if self._accent_sudo_color:
            self.accent_sudo_btn.setStyleSheet(
                f"QPushButton {{ border-left: 4px solid {self._accent_sudo_color}; }}"
            )
        else:
            self.accent_sudo_btn.setStyleSheet("")

    def _save_and_close(self):
        self.settings["terminal"] = self.term_combo.currentData()
        self.settings["term_launch"] = self.launch_combo.currentData()
        self.settings["font_size"] = self.font_spin.value()
        self.settings["show_icons"] = self.icons_chk.isChecked()
        self.settings["color_theme"] = self.theme_combo.currentText()
        self.settings["custom_accent"] = self._accent_color
        self.settings["custom_accent_sudo"] = self._accent_sudo_color
        self.settings.save()
        self.accept()


# ---------------------------------------------------------------------------
#  Main Window
# ---------------------------------------------------------------------------
class ToolKitWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.tools = []
        self.sudo_mode = False
        self.spawned = []  # list of (Popen, script_name, timestamp)

        self.setWindowTitle("Glitch-Toolkit")
        self.resize(520, 420)
        self.setMinimumSize(340, 260)

        # Set embedded app icon (window + taskbar)
        app_icon = build_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

        self._build_ui()
        self._apply_theme()

        # Poll child processes every 2 seconds
        self._proc_timer = QTimer(self)
        self._proc_timer.timeout.connect(self._poll_processes)
        self._proc_timer.start(2000)
        self._setup_shortcuts()
        self._ensure_icons()
        self._sync_repo_bg()

    # ----- UI Build --------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 2)
        layout.setSpacing(6)

        # -- Top bar: search + buttons
        top = QHBoxLayout()
        top.setSpacing(4)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search or enter number...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        self.search.returnPressed.connect(self._on_enter)
        top.addWidget(self.search, 1)

        self.sudo_btn = QPushButton("USER")
        self.sudo_btn.setFixedWidth(68)
        self.sudo_btn.setCheckable(True)
        self.sudo_btn.setToolTip("Toggle sudo mode  [Ctrl+S]")
        self.sudo_btn.clicked.connect(self._toggle_sudo)
        top.addWidget(self.sudo_btn)

        # Launch mode cycle: minimized -> small -> fullscreen
        self.launch_btn = QPushButton()
        self.launch_btn.setFixedWidth(36)
        self.launch_btn.setToolTip("Terminal launch mode  [Ctrl+L]")
        self.launch_btn.clicked.connect(self._cycle_launch_mode)
        self._update_launch_btn()
        top.addWidget(self.launch_btn)

        self.settings_btn = QPushButton("\u2699")
        self.settings_btn.setFixedWidth(36)
        self.settings_btn.setToolTip("Settings  [Ctrl+,]")
        self.settings_btn.clicked.connect(self._open_settings)
        top.addWidget(self.settings_btn)

        self.refresh_btn = QPushButton("\u21bb")
        self.refresh_btn.setFixedWidth(36)
        self.refresh_btn.setToolTip("Refresh repo  [Ctrl+R]")
        self.refresh_btn.clicked.connect(self._sync_repo_bg)
        top.addWidget(self.refresh_btn)

        self.proc_btn = QPushButton("\u25cf 0")
        self.proc_btn.setFixedWidth(52)
        self.proc_btn.setToolTip("Running processes - click to manage")
        self.proc_btn.clicked.connect(self._show_proc_menu)
        self.proc_btn.setVisible(False)  # hidden when 0 processes
        top.addWidget(self.proc_btn)

        layout.addLayout(top)

        # -- Tool list
        self.tool_list = QListWidget()
        self.tool_list.setIconSize(QSize(24, 24))
        self.tool_list.setSpacing(2)
        self.tool_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tool_list.itemDoubleClicked.connect(self._run_selected)
        self.tool_list.itemActivated.connect(self._run_selected)
        self.tool_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tool_list.customContextMenuRequested.connect(self._context_menu)
        self.tool_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tool_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.tool_list, 1)

        # -- Status bar
        self.status = QStatusBar()
        self.status.setFixedHeight(26)
        self.setStatusBar(self.status)
        self.status_label = QLabel("Starting...")
        self.status.addWidget(self.status_label, 1)

        # Font size +/- in status bar
        self.font_down_btn = QPushButton("A-")
        self.font_down_btn.setFixedSize(32, 22)
        self.font_down_btn.setToolTip("Decrease font  [Ctrl+-]")
        self.font_down_btn.clicked.connect(lambda: self._adjust_font(-1))
        self.status.addPermanentWidget(self.font_down_btn)

        self.font_up_btn = QPushButton("A+")
        self.font_up_btn.setFixedSize(32, 22)
        self.font_up_btn.setToolTip("Increase font  [Ctrl++]")
        self.font_up_btn.clicked.connect(lambda: self._adjust_font(1))
        self.status.addPermanentWidget(self.font_up_btn)

        self.count_label = QLabel("")
        self.status.addPermanentWidget(self.count_label)

    # ----- Theme -----------------------------------------------------------
    def _apply_theme(self):
        t = self.settings.theme()
        fs = self.settings["font_size"]
        fs_search = fs + 1
        fs_status = max(fs - 2, 10)

        accent = t["accent"] if not self.sudo_mode else t["accent_sudo"]
        sel_bg = t["sel"] if not self.sudo_mode else t["sel_sudo"]

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {t['bg']};
            }}
            QWidget {{
                background: {t['bg']};
                color: {t['fg']};
                font-family: "Sans", "Noto Sans", "DejaVu Sans", sans-serif;
                font-size: {fs}px;
                font-weight: bold;
            }}
            QLineEdit {{
                background: {t['search_bg']};
                color: {t['fg']};
                border: 2px solid {t['border']};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: {fs_search}px;
                font-weight: bold;
                selection-background-color: {accent};
            }}
            QLineEdit:focus {{
                border-color: {accent};
            }}
            QListWidget {{
                background: {t['bg_alt']};
                border: 2px solid {t['border']};
                border-radius: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 4px 6px;
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background: {sel_bg};
                color: {accent};
            }}
            QListWidget::item:hover:!selected {{
                background: {t['hover']};
            }}
            QPushButton {{
                background: {t['border']};
                color: {t['fg']};
                border: 2px solid {t['border']};
                border-radius: 4px;
                padding: 5px 8px;
                font-size: {max(fs - 1, 10)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {t['hover']};
                border-color: {accent};
            }}
            QPushButton:checked {{
                background: {t['sel_sudo']};
                color: {t['accent_sudo']};
                border-color: {t['accent_sudo']};
            }}
            QStatusBar {{
                background: {t['bg']};
                color: #666680;
                font-size: {fs_status}px;
                font-weight: bold;
            }}
            QStatusBar QLabel {{
                color: #666680;
                font-size: {fs_status}px;
                font-weight: bold;
            }}
            QStatusBar QPushButton {{
                font-size: {max(fs_status, 10)}px;
                padding: 1px 4px;
                min-height: 0;
            }}
            QMenu {{
                background: {t['bg_alt']};
                color: {t['fg']};
                border: 2px solid {t['border']};
                padding: 4px;
                font-size: {max(fs - 1, 10)}px;
                font-weight: bold;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 10px;
            }}
            QMenu::item:selected {{
                background: {sel_bg};
                color: {accent};
            }}
            QScrollBar:vertical {{
                background: {t['bg_alt']};
                width: 8px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        self._update_sudo_visuals()

    def _update_sudo_visuals(self):
        t = self.settings.theme()
        if self.sudo_mode:
            self.sudo_btn.setText("ROOT")
            self.sudo_btn.setChecked(True)
        else:
            self.sudo_btn.setText("USER")
            self.sudo_btn.setChecked(False)
        self._update_status()

    # ----- Shortcuts -------------------------------------------------------
    def _setup_shortcuts(self):
        for key, fn in [
            ("Ctrl+S",     self._toggle_sudo),
            ("Ctrl+R",     self._sync_repo_bg),
            ("Ctrl+E",     self._export_selected),
            ("F11",        self._toggle_fullscreen),
            ("Escape",     self._escape_handler),
            ("Ctrl+,",     self._open_settings),
            ("Ctrl+L",     self._cycle_launch_mode),
            ("Ctrl++",     lambda: self._adjust_font(1)),
            ("Ctrl+=",     lambda: self._adjust_font(1)),
            ("Ctrl+-",     lambda: self._adjust_font(-1)),
        ]:
            act = QAction(self)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(fn)
            self.addAction(act)

    # ----- Icons -----------------------------------------------------------
    def _ensure_icons(self):
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        missing = [f for f in ICON_LIST if not (ICON_DIR / f).exists()]
        if missing:
            def dl():
                for f in missing:
                    try:
                        subprocess.run(
                            ["wget", "-q", "-O", str(ICON_DIR / f),
                             f"{ICON_URL}/{f}"],
                            timeout=10, capture_output=True
                        )
                    except Exception:
                        pass
            threading.Thread(target=dl, daemon=True).start()

    # ----- Repo sync -------------------------------------------------------
    def _sync_repo_bg(self):
        self.status_label.setText("Syncing repo...")
        self.refresh_btn.setEnabled(False)

        def worker():
            try:
                if (REPO_DIR / ".git").is_dir():
                    r = subprocess.run(
                        ["git", "-C", str(REPO_DIR), "pull", "--quiet", "--ff-only"],
                        capture_output=True, timeout=30
                    )
                    if r.returncode != 0:
                        subprocess.run(["rm", "-rf", str(REPO_DIR)],
                                       capture_output=True)
                        subprocess.run(
                            ["git", "clone", "--quiet", REPO_URL, str(REPO_DIR)],
                            capture_output=True, timeout=60
                        )
                else:
                    subprocess.run(["rm", "-rf", str(REPO_DIR)],
                                   capture_output=True)
                    subprocess.run(
                        ["git", "clone", "--quiet", REPO_URL, str(REPO_DIR)],
                        capture_output=True, timeout=60
                    )
                QTimer.singleShot(0, self._load_tools)
            except Exception as e:
                QTimer.singleShot(0, lambda: self._sync_fail(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _sync_fail(self, msg):
        self.refresh_btn.setEnabled(True)
        self.status_label.setText(f"Sync failed: {msg}")

    def _load_tools(self):
        self.refresh_btn.setEnabled(True)
        if not REPO_DIR.is_dir():
            self.status_label.setText("Repo not found")
            return

        self.tools = sorted(
            [f.name for f in REPO_DIR.iterdir()
             if f.is_file() and not f.name.startswith(".")
             and ".git" not in str(f)],
            key=lambda x: x.lower()
        )
        self._filter()
        self._update_status()
        self.status_label.setText("Ready")
        self.search.setFocus()

    # ----- Filtering -------------------------------------------------------
    def _filter(self):
        query = self.search.text().strip().lower()
        self.tool_list.clear()
        show_icons = self.settings["show_icons"]

        for idx, name in enumerate(self.tools, 1):
            if query:
                if query.isdigit():
                    if str(idx) != query and query not in name.lower():
                        continue
                elif query not in name.lower():
                    continue

            item = QListWidgetItem()
            display = f" {idx:>3}.  {name}"
            item.setText(display)
            item.setData(Qt.UserRole, name)
            item.setData(Qt.UserRole + 1, idx)

            if show_icons:
                icon_path = icon_for_file(name)
                if icon_path:
                    item.setIcon(QIcon(icon_path))

            self.tool_list.addItem(item)

        if self.tool_list.count() > 0:
            self.tool_list.setCurrentRow(0)

        self._update_count()

    def _update_count(self):
        shown = self.tool_list.count()
        total = len(self.tools)
        self.count_label.setText(f"{shown}/{total}")

    def _update_status(self):
        mode = "ROOT" if self.sudo_mode else "USER"
        term = resolve_terminal(self.settings)
        launch = self.settings["term_launch"]
        self.status_label.setText(f"[{mode}]  {term}  [{launch}]")

    # ----- Run scripts -----------------------------------------------------
    def _on_enter(self):
        if self.tool_list.count() > 0:
            current = self.tool_list.currentItem()
            if current is None:
                current = self.tool_list.item(0)
            self._run_item(current)

    def _run_selected(self, item):
        self._run_item(item)

    def _run_item(self, item):
        if item is None:
            return
        name = item.data(Qt.UserRole)
        script_path = REPO_DIR / name
        if not script_path.exists():
            return

        self.status_label.setText(f"Running: {name}")
        term = resolve_terminal(self.settings)
        launch = self.settings["term_launch"]  # minimized | small | fullscreen

        # Build the command
        cmd_parts = []
        if self.sudo_mode:
            cmd_parts.append("sudo")

        if os.access(str(script_path), os.X_OK):
            cmd_parts.append(str(script_path))
        else:
            cmd_parts.append("bash")
            cmd_parts.append(str(script_path))

        shell_cmd = " ".join(cmd_parts)
        wrapped = (f'{shell_cmd}; echo ""; '
                   f'echo -e "\\033[0;36mPress Enter to close...\\033[0m"; read')

        proc = None
        try:
            env = os.environ.copy()

            if term == "xfce4-terminal":
                args = [term, "--hold"]
                if launch == "minimized":
                    args.append("--minimize")
                elif launch == "fullscreen":
                    args.append("--fullscreen")
                elif launch == "small":
                    args.extend(["--geometry", "80x24"])
                args.extend(["-e", f"bash -c '{wrapped}'"])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            elif term == "gnome-terminal":
                args = [term]
                if launch == "fullscreen":
                    args.append("--full-screen")
                elif launch == "small":
                    args.extend(["--geometry", "80x24"])
                elif launch == "minimized":
                    args.extend(["--geometry", "80x24"])
                args.extend(["--", "bash", "-c", wrapped])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            elif term == "konsole":
                args = [term, "--hold"]
                if launch == "fullscreen":
                    args.append("--fullscreen")
                elif launch == "small":
                    args.extend(["--geometry", "80x24"])
                args.extend(["-e", "bash", "-c", wrapped])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            elif term == "alacritty":
                args = [term]
                if launch == "small":
                    args.extend(["-o", "window.dimensions.columns=80",
                                 "-o", "window.dimensions.lines=24"])
                args.extend(["-e", "bash", "-c", wrapped])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            elif term == "kitty":
                args = [term]
                if launch == "fullscreen":
                    args.extend(["--start-as", "fullscreen"])
                elif launch == "minimized":
                    args.extend(["--start-as", "minimized"])
                args.extend(["-e", "bash", "-c", wrapped])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            else:
                # xterm and others
                args = [term]
                if launch == "minimized":
                    args.append("-iconic")
                elif launch == "fullscreen":
                    args.extend(["-fullscreen"])
                elif launch == "small":
                    args.extend(["-geometry", "80x24"])
                args.extend(["-e", f"bash -c '{wrapped}'"])
                proc = subprocess.Popen(args, env=env, start_new_session=True)

            if proc:
                self.spawned.append((proc, name, time.time()))
                self._update_proc_btn()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to launch:\n{e}")

    # ----- Process tracking ------------------------------------------------
    def _poll_processes(self):
        """Check for exited processes and update the indicator."""
        if not self.spawned:
            return
        # poll() returns None if still running, exit code if done
        for proc, name, ts in self.spawned:
            proc.poll()
        self._update_proc_btn()

    def _update_proc_btn(self):
        """Update the process button label and visibility."""
        alive = sum(1 for p, n, t in self.spawned if p.poll() is None)
        dead  = sum(1 for p, n, t in self.spawned if p.poll() is not None)
        total = len(self.spawned)

        if total == 0:
            self.proc_btn.setVisible(False)
            return

        self.proc_btn.setVisible(True)

        if alive > 0 and dead > 0:
            self.proc_btn.setText(f"\u25cf {alive}  \u2717 {dead}")
            self.proc_btn.setToolTip(
                f"{alive} running, {dead} finished - click to manage")
        elif alive > 0:
            self.proc_btn.setText(f"\u25cf {alive}")
            self.proc_btn.setToolTip(f"{alive} running - click to manage")
        else:
            self.proc_btn.setText(f"\u2717 {dead}")
            self.proc_btn.setToolTip(f"{dead} finished - click to clean up")

        # Color the button: green if all alive, red if any dead, yellow if mixed
        if dead > 0 and alive > 0:
            self.proc_btn.setStyleSheet(
                "QPushButton { color: #ffcc00; border-color: #ffcc00; }")
        elif dead > 0:
            self.proc_btn.setStyleSheet(
                "QPushButton { color: #ff4444; border-color: #ff4444; }")
        else:
            self.proc_btn.setStyleSheet(
                "QPushButton { color: #00ff0b; border-color: #00ff0b; }")

    def _show_proc_menu(self):
        """Show a menu listing all tracked processes with kill/clean options."""
        menu = QMenu(self)

        alive_items = []
        dead_items = []

        for i, (proc, name, ts) in enumerate(self.spawned):
            elapsed = int(time.time() - ts)
            mins, secs = divmod(elapsed, 60)
            time_str = f"{mins}m{secs:02d}s" if mins else f"{secs}s"

            if proc.poll() is None:
                # Still running
                act = menu.addAction(f"\u25cf  {name}  [{time_str}]  -  Kill")
                act.triggered.connect(lambda checked, idx=i: self._kill_proc(idx))
                alive_items.append(i)
            else:
                act = menu.addAction(f"\u2717  {name}  [{time_str}]  -  exited")
                act.setEnabled(False)
                dead_items.append(i)

        if alive_items or dead_items:
            menu.addSeparator()

        if alive_items:
            act_kill_all = menu.addAction(
                f"\u2620  Kill all running  ({len(alive_items)})")
            act_kill_all.triggered.connect(self._kill_all_procs)

        if dead_items:
            act_clean = menu.addAction(
                f"\u2702  Clean finished  ({len(dead_items)})")
            act_clean.triggered.connect(self._clean_dead_procs)

        if alive_items or dead_items:
            act_nuke = menu.addAction("\u26a0  Kill all + Clean")
            act_nuke.triggered.connect(self._nuke_all_procs)

        menu.exec_(self.proc_btn.mapToGlobal(
            self.proc_btn.rect().bottomLeft()))

    def _kill_proc(self, idx):
        """Kill a single process and its children."""
        if idx < len(self.spawned):
            proc, name, ts = self.spawned[idx]
            if proc.poll() is None:
                pid = proc.pid
                # Kill process group first
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                try:
                    proc.terminate()
                except Exception:
                    pass
                # Sudo kill for elevated child processes
                try:
                    subprocess.run(
                        ["sudo", "kill", "-9", str(pid)],
                        capture_output=True, timeout=3
                    )
                except Exception:
                    pass
                # Kill any orphaned child processes by PPID
                self._kill_children(pid)
                self.status_label.setText(f"Killed: {name}")
            self._poll_processes()

    def _kill_children(self, ppid):
        """Find and kill child processes by parent PID."""
        try:
            result = subprocess.run(
                ["pgrep", "-P", str(ppid)],
                capture_output=True, text=True, timeout=3
            )
            for child_pid in result.stdout.strip().split("\n"):
                if child_pid.strip():
                    try:
                        os.kill(int(child_pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        subprocess.run(
                            ["sudo", "kill", "-9", child_pid.strip()],
                            capture_output=True, timeout=3
                        )
        except Exception:
            pass

    def _kill_all_procs(self):
        """Kill all running processes."""
        killed = 0
        for proc, name, ts in self.spawned:
            if proc.poll() is None:
                pid = proc.pid
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                try:
                    proc.terminate()
                except Exception:
                    pass
                self._kill_children(pid)
                killed += 1
        self.status_label.setText(f"Killed {killed} process(es)")
        # Give SIGTERM a moment, then force-kill terminals
        QTimer.singleShot(500, self._force_kill_terminals)

    def _force_kill_terminals(self):
        """SIGKILL any surviving spawned PIDs and their terminal processes."""
        term = resolve_terminal(self.settings)
        for proc, name, ts in self.spawned:
            if proc.poll() is None:
                pid = proc.pid
                # SIGKILL the process group
                try:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                try:
                    proc.kill()
                except Exception:
                    pass
                # Sudo kill as last resort
                try:
                    subprocess.run(
                        ["sudo", "kill", "-9", str(pid)],
                        capture_output=True, timeout=3
                    )
                except Exception:
                    pass
        self._poll_processes()

    def _clean_dead_procs(self):
        """Remove finished processes from the tracking list."""
        before = len(self.spawned)
        self.spawned = [(p, n, t) for p, n, t in self.spawned
                        if p.poll() is None]
        cleaned = before - len(self.spawned)
        self.status_label.setText(f"Cleaned {cleaned} finished process(es)")
        self._update_proc_btn()

    def _nuke_all_procs(self):
        """Kill everything and clean the list."""
        self._kill_all_procs()
        # Wait for force-kill, then wipe the list
        QTimer.singleShot(1200, self._force_clean_all)

    def _force_clean_all(self):
        """Force-kill any survivors and clear the list."""
        term = resolve_terminal(self.settings)
        for proc, name, ts in self.spawned:
            if proc.poll() is None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                try:
                    proc.kill()
                except Exception:
                    pass
        # Nuclear option: pkill the terminal binary for any orphans
        # Only kill terminals spawned by our PID to avoid killing user terminals
        my_pid = os.getpid()
        try:
            subprocess.run(
                ["pkill", "-9", "-P", str(my_pid), term],
                capture_output=True, timeout=3
            )
        except Exception:
            pass
        self.spawned.clear()
        self._update_proc_btn()
        self.status_label.setText("All processes terminated")

    # ----- Toggles ---------------------------------------------------------
    def _toggle_sudo(self):
        self.sudo_mode = not self.sudo_mode
        self._apply_theme()

    def _cycle_launch_mode(self):
        modes = ["minimized", "small", "fullscreen"]
        cur = self.settings["term_launch"]
        idx = modes.index(cur) if cur in modes else 0
        nxt = modes[(idx + 1) % len(modes)]
        self.settings["term_launch"] = nxt
        self.settings.save()
        self._update_launch_btn()
        self._update_status()

    def _update_launch_btn(self):
        icons = {"minimized": "\u2581", "small": "\u25a1", "fullscreen": "\u2587"}
        tips  = {"minimized": "Launch: minimized",
                 "small":     "Launch: small window",
                 "fullscreen":"Launch: fullscreen"}
        mode = self.settings["term_launch"]
        self.launch_btn.setText(icons.get(mode, "\u25a1"))
        self.launch_btn.setToolTip(f"{tips.get(mode, '')}  [Ctrl+L]")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _escape_handler(self):
        if self.isFullScreen():
            self.showNormal()
        elif self.search.text():
            self.search.clear()
        self.search.setFocus()

    def _adjust_font(self, delta):
        cur = self.settings["font_size"]
        new = max(10, min(28, cur + delta))
        if new != cur:
            self.settings["font_size"] = new
            self.settings.save()
            self._apply_theme()

    # ----- Settings dialog -------------------------------------------------
    def _open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec_() == QDialog.Accepted:
            self._apply_theme()
            self._update_launch_btn()
            self._filter()  # refresh icons on/off

    # ----- Context menu ----------------------------------------------------
    def _context_menu(self, pos):
        item = self.tool_list.itemAt(pos)
        if not item:
            return

        name = item.data(Qt.UserRole)
        menu = QMenu(self)

        act_run = menu.addAction(f"Run  -  {name}")
        act_run.triggered.connect(lambda: self._run_item(item))

        act_sudo_run = menu.addAction("Run as Root")
        def run_as_root():
            was = self.sudo_mode
            self.sudo_mode = True
            self._run_item(item)
            self.sudo_mode = was
        act_sudo_run.triggered.connect(run_as_root)

        menu.addSeparator()

        act_export = menu.addAction("Export / Copy to...  [Ctrl+E]")
        act_export.triggered.connect(lambda: self._export_item(name))

        act_view = menu.addAction("View source")
        act_view.triggered.connect(lambda: self._view_source(name))

        menu.exec_(self.tool_list.mapToGlobal(pos))

    # ----- Export ----------------------------------------------------------
    def _export_selected(self):
        item = self.tool_list.currentItem()
        if item:
            self._export_item(item.data(Qt.UserRole))

    def _export_item(self, name):
        src = REPO_DIR / name
        if not src.exists():
            return

        dest, _ = QFileDialog.getSaveFileName(
            self, f"Export: {name}", str(Path.home() / name),
            "All Files (*)"
        )
        if not dest:
            return

        try:
            shutil.copy2(str(src), dest)
            reply = QMessageBox.question(
                self, "Make executable?",
                f"Make {Path(dest).name} executable?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                os.chmod(dest, 0o755)
            self.status_label.setText(f"Exported: {dest}")
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))

    # ----- View source -----------------------------------------------------
    def _view_source(self, name):
        script_path = REPO_DIR / name
        if not script_path.exists():
            return
        term = resolve_terminal(self.settings)
        try:
            subprocess.Popen([
                term, "-e",
                f"bash -c 'less \"{script_path}\"; read'"
            ])
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    # ----- Key handling ----------------------------------------------------
    def keyPressEvent(self, event):
        if (self.tool_list.hasFocus()
                and event.text()
                and event.text().isprintable()
                and not event.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
            self.search.setFocus()
            self.search.setText(self.search.text() + event.text())
            return
        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
#  Entry
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Glitch-Toolkit")
    win = ToolKitWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
