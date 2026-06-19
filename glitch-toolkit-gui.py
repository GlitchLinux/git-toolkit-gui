#!/usr/bin/env python3
"""
Glitch-Toolkit GUI - PyQt5 launcher for the Glitch-ToolKit repo.
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
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QKeySequence

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
