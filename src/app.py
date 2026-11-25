"""Callas Optima para Windows, com interface PySide6."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import threading
import uuid
import webbrowser

from PySide6.QtCore import QByteArray, QEvent, QFileInfo, QRect, QRectF, QSettings, QSize, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QFileDialog, QFileIconProvider, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QSpinBox, QStackedWidget, QVBoxLayout, QWidget,
)

from cleaner import (
    clean_folders, clear_icon_cache, empty_recycle_bin, format_size, known_temp_folders,
    nvidia_dxcache_folders, windows_temp_folder,
)
from windows_actions import (
    ACTIONS, BY_ROUTE, HOME as ACTION_HOME, MAX_SHUTDOWN_MINUTES, PROFILE_MISMATCH, ElevatedAction,
    applied_action_backups, dns_provider_status, edge_installed, remaining_shutdown_minutes, worker as run_windows_action,
)
from extra_installers import (
    CATALOG as EXTRA_APPS, available_upgrades, download_and_open, installed_program,
    official_website, open_program, powershell_env, powershell_path, program_key, upgrade_program,
)
from network_dns import DNS_PROVIDERS, DNS_REVERSALS
from task_progress import TaskProgressBar
from virtualbox_templates import create_test_vms, VM_NAMES, get_vboxmanage

APP_VERSION = "8.9.31"
REPO = "Callas157/Callas-Optimizer-Windows"
PROJECT_URL = f"https://github.com/{REPO}"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CallasTeck"
NATIVE_PROGRAM_ICONS = {"steam", "discord", "epic", "medal", "lghub", "wise", "virtualbox"}

HOME_SHORTCUTS = (
    ("programs", "Programas", "Instale e atualize seus aplicativos."),
    ("clean", "Limpeza Total", "Libere espaço removendo arquivos temporários."),
    ("gamer", "Modo Gamer", "Ajustes de desempenho e energia para jogos."),
    ("repair", "Reparar Windows", "Diagnóstico e recuperação do sistema."),
    ("drivers", "Drivers", "Acesse ferramentas oficiais de atualização."),
)

WINDOWS_SHORTCUTS = (
    ("network", "Rede e DNS"),
    ("windows_update", "Windows Update"),
    ("startupapps", "Inicialização"),
    ("privacy", "Privacidade"),
    ("shutdown", "Desligamento"),
    ("edge", "Microsoft Edge"),
    ("classic", "Menu clássico"),
    ("winutil", "WinUtil"),
    ("restore_point", "Ponto de restauração"),
    ("restore", "Restaurar padrões"),
)

APP_SHORTCUTS = (
    ("updates", "Atualizações do Callas"),
    ("logs", "Registros"),
    ("about", "Sobre"),
)

TOOL_PAGES = {
    "gamer": ("Modo Gamer", "Ajustes para jogos, Xbox, hibernação e plano de energia."),
    "repair": ("Reparar Windows", "Ferramentas oficiais de diagnóstico e recuperação."),
    "edge": ("Microsoft Edge", "Remoção e recuperação do navegador."),
    "windows_update": ("Windows Update", "Gerencie as políticas e os serviços de atualização do Windows."),
    "network": ("Rede e DNS", "Gerencie a rede e o DNS dos adaptadores."),
    "privacy": ("Privacidade", "Controles dos dados de diagnóstico do Windows."),
    "classic": ("Menu clássico", "Alterne o menu de contexto do Windows 11."),
    "shutdown": ("Desligamento", "Agende ou cancele um desligamento automático."),
    "winutil": ("WinUtil", "Ferramenta de manutenção de Chris Titus Tech."),
    "restore_point": ("Ponto de restauração", "A proteção do sistema precisa estar habilitada no Windows."),
    "restore": ("Restaurar padrões", "Recupere as configurações salvas pelo Callas Optimizer."),
}

REVERSIBLE_ACTIONS = {
    "gamer_on": ("gamer_off", "Modo Jogo", "Aplicar"),
    "power_on": ("power_off", "Alto desempenho", "Aplicar"),
    "gamer_services_off": ("gamer_services_on", "SysMain e Pesquisa", "Desativar"),
    "hiber_off": ("hiber_on", "Hibernação", "Desativar"),
    "edge_uninstall": ("edge_restore", "Navegador Microsoft Edge", "Remover"),
    "telemetry_reduce": ("telemetry_restore", "Telemetria opcional", "Reduzir"),
    "classic_on": ("classic_off", "Menu de contexto clássico", "Ativar"),
    "dns_cloudflare": ("dns_cloudflare_auto", "DNS Cloudflare", "Aplicar"),
    "dns_google": ("dns_google_auto", "DNS Google", "Aplicar"),
}
ACTION_CARD_KEYS = {undo: code for code, (undo, _, _) in REVERSIBLE_ACTIONS.items()}

STYLE = """
* { font-family: 'Segoe UI'; font-size: 13px; color: #e8ecff; }
QMainWindow, QWidget#MainRoot { background: #07091e; }
QFrame#Topbar { background: #0a0e24; border-bottom: 1px solid #282449; }
QFrame#Card { background: #111b37; border: 1px solid #403a71; border-radius: 15px; }
QFrame#DashboardPanel { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #15173b,stop:1 #0c1e3f); border: 1px solid #595197; border-radius: 15px; }
QFrame#Hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #171b3b,stop:.5 #0a1028,stop:.77 #171044,stop:1 #0b2148); border: 1px solid #6255ba; border-radius: 18px; }
QLabel#Header { font-size: 31px; font-weight: 700; color: #f8f7ff; }
QLabel#Title { font-size: 27px; font-weight: 700; color: #f9f8ff; }
QLabel#HeroTitle { font-size: 26px; font-weight: 700; color: #fff; }
QLabel#SystemMetric { color: #e6efff; font-size: 14px; font-weight: 600; }
QLabel#CardTitle { font-size: 17px; font-weight: 700; color: #f8f8ff; }
QLabel#ProgramTitle { font-size: 15px; font-weight: 700; color: #f8f8ff; }
QLabel#Muted { color: #a8b9d8; }
QLabel#Section { color: #bc91ff; font-weight: 700; font-size: 11px; letter-spacing: 1px; }
QPushButton { background: #22234e; color: #f2f3ff; border: 1px solid #635e9b; border-radius: 11px; padding: 10px 13px; font-weight: 600; }
QPushButton:hover { background: #38347c; border-color: #b87aff; }
QPushButton:disabled { color: #7880a6; background: #1b2241; border-color: #3a3b61; }
QPushButton#Primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #a02bdf,stop:.55 #523cec,stop:1 #087bff); border: 1px solid #9e6dff; color: #fff; }
QPushButton#Primary:hover { background: #8753ee; border-color: #52e3ff; }
QPushButton[compact="true"] { padding: 5px 10px; border-radius: 8px; }
QPushButton[updateAvailable="true"] { border-color: #6cc9f4; background: #213c65; }
QPushButton[updateAvailable="true"]:hover { background: #2d517d; }
QPushButton#Primary[compact="true"]:disabled { color: #a8b9d8; background: #1b2241; border-color: #3a3b61; }
QDialog#ShutdownDialog { background: #111b37; }
QSpinBox#ShutdownMinutes { background: #0a1026; border: 1px solid #635e9b; border-radius: 8px; padding: 7px 9px; }
QLabel#ActionWarning { color: #e6c890; }
QPushButton#QuickCard { background: qlineargradient(x1:0,y1:0,x2:.7,y2:1,stop:0 #28134e,stop:.64 #121332,stop:1 #321469); border: 1px solid #a466f1; border-radius: 16px; padding: 0; }
QPushButton#QuickCard[accent="cyan"] { background: qlineargradient(x1:0,y1:0,x2:.7,y2:1,stop:0 #0c2d56,stop:.64 #0e1837,stop:1 #0b3a70); border-color: #4c9bea; }
QPushButton#QuickCard:hover, QPushButton#QuickCard:focus { border: 2px solid #e6aaff; }
QPushButton#QuickCard[accent="cyan"]:hover, QPushButton#QuickCard[accent="cyan"]:focus { border: 2px solid #8deaff; }
QPushButton#ToolShortcut { text-align: left; }
QScrollArea { border: none; background: transparent; }
QWidget#PageContent { background: #07091e; }
QScrollBar:vertical { background: #10142d; width: 9px; }
QScrollBar::handle:vertical { background: #6154a0; border-radius: 4px; min-height: 35px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QCheckBox { spacing: 11px; font-size: 13px; }
QCheckBox::indicator { width: 19px; height: 19px; }
QProgressBar { border: 1px solid #5a4b9e; border-radius: 7px; text-align: center; background: #101631; min-height: 16px; }
QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #d337eb,stop:1 #06c8f5); border-radius: 7px; }
QPlainTextEdit { background: #0a1026; color: #c6d7f8; border: 1px solid #4c4684; border-radius: 8px; padding: 10px; font-family: Consolas; font-size: 12px; }
QMessageBox { background: #13172f; }
"""


def asset_dir() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / "assets" / "icons"


def app_icon() -> QIcon:
    # Na instalacao, usar o mesmo ICO persistente dos atalhos do Windows.
    # Isso evita depender do caminho temporario usado pelo PyInstaller onefile.
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "CallasOptimizer.ico")
    candidates.append(asset_dir() / "callas.ico")
    for ico in candidates:
        if ico.is_file():
            icon = QIcon(str(ico))
            if not icon.isNull():
                return icon
    return svg_icon("callas")


def installed_mode() -> bool:
    return bool(getattr(sys, "frozen", False) and
                (Path(sys.executable).resolve().parent / "installed.marker").is_file())


def runtime_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "runtime"
    return Path(__file__).resolve().parent


def svg_icon(name: str, pixels: int = 64) -> QIcon:
    # A Fênix aprovada e usada no painel e na marca do aplicativo.
    if name == "callas":
        image_file = asset_dir() / "phoenix-approved.png"
        if image_file.is_file():
            original = QPixmap(str(image_file))
            if not original.isNull():
                scaled = original.scaled(pixels, pixels, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
                return QIcon(scaled)
    svg = asset_dir() / (name + ".svg")
    renderer = QSvgRenderer(QByteArray(svg.read_bytes()))
    result = QPixmap(pixels, pixels)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    renderer.render(painter)
    painter.end()
    return QIcon(result)


def header_logo() -> QPixmap:
    source = svg_icon("callas", 70).pixmap(60, 60)
    rounded = QPixmap(source.size())
    rounded.setDevicePixelRatio(source.devicePixelRatio())
    rounded.fill(Qt.GlobalColor.transparent)
    bounds = QRectF(0, 0, source.deviceIndependentSize().width(), source.deviceIndependentSize().height())
    with QPainter(rounded) as painter:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(source))
        painter.drawRoundedRect(bounds, 11, 11)
    return rounded


def runtime_files() -> None:
    """Prepara a pasta de dados e confere os scripts empacotados."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("updater.ps1", "extensions.ps1", "undo_extensions.ps1"):
        if not (runtime_dir() / name).is_file():
            raise FileNotFoundError(f"Recurso da aplicação não encontrado: {name}")


def in_windows11() -> bool:
    if os.name != "nt":
        return False
    try:
        v = sys.getwindowsversion()
        return v.major == 10 and v.build >= 22000
    except AttributeError:
        return False


def confirmar(parent, titulo: str, mensagem: str, padrao_sim: bool = False) -> bool:
    """Caixa de confirmacao PT-BR independente do pacote de traducoes Qt."""
    caixa = QMessageBox(parent)
    caixa.setWindowTitle(titulo)
    caixa.setText(mensagem)
    caixa.setIcon(QMessageBox.Icon.Question)
    botao_sim = caixa.addButton("Sim", QMessageBox.ButtonRole.YesRole)
    botao_nao = caixa.addButton("Não", QMessageBox.ButtonRole.NoRole)
    caixa.setDefaultButton(botao_sim if padrao_sim else botao_nao)
    caixa.exec()
    return caixa.clickedButton() is botao_sim


class ExtraInstallerThread(QThread):
    progress = Signal(str, int)
    result = Signal(bool, str, str)

    def __init__(self, app_id: str, upgrade: bool):
        super().__init__()
        self.app_id = app_id
        self.upgrade = upgrade

    def run(self):
        try:
            operation = upgrade_program if self.upgrade else download_and_open
            message = operation(self.app_id, self.progress.emit)
            self.result.emit(True, message or "", self.app_id)
        except OSError as exc:
            message = "A instalação foi cancelada." if getattr(exc, "winerror", None) == 1223 else str(exc)
            self.result.emit(False, message, self.app_id)
        except Exception as exc:
            self.result.emit(False, str(exc), self.app_id)


class VirtualBoxTemplateThread(QThread):
    progress = Signal(str)
    percent = Signal(int)
    result = Signal(bool, str)

    def __init__(self, folder: Path):
        super().__init__()
        self.folder = folder

    def run(self):
        try:
            message = create_test_vms(self.folder, self.progress.emit, report_progress=self.percent.emit)
            self.result.emit(True, message)
        except Exception as exc:
            self.result.emit(False, str(exc))


class BraveExtensionsThread(QThread):
    result = Signal(bool, str)

    def __init__(self, undo: bool):
        super().__init__()
        self.script = "undo_extensions.ps1" if undo else "extensions.ps1"

    def run(self):
        try:
            process = subprocess.run(
                [str(powershell_path()), "-NoLogo", "-NoProfile", "-NonInteractive",
                 "-ExecutionPolicy", "Bypass", "-File", str(runtime_dir() / self.script)],
                cwd=DATA_DIR, capture_output=True, timeout=45,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                env=powershell_env(),
            )
            message = "Reinicie o Brave para carregar a alteração." if process.returncode == 0 else (
                "Falha ao configurar extensões. Consulte o log de instalações.")
            self.result.emit(process.returncode == 0, message)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.result.emit(False, str(exc))


class CleanerThread(QThread):
    progress = Signal(str)
    percent = Signal(int)
    complete = Signal(object)
    failed = Signal(str)

    def __init__(self, roots: list[Path], recycle: bool, icons: bool):
        super().__init__()
        self.roots = roots
        self.recycle = recycle
        self.icons = icons
        self.cancel_flag = threading.Event()

    def run(self):
        try:
            self.complete.emit(self.clean())
        except Exception as exc:
            self.failed.emit(str(exc))

    def clean(self):
        total_steps = len(self.roots) + int(self.recycle) + int(self.icons)
        completed = 0

        def complete_step():
            nonlocal completed
            if not self.cancel_flag.is_set():
                completed += 1
                self.percent.emit(100 * completed // total_steps)

        stats = clean_folders(self.roots, self.cancel_flag, self.progress.emit,
                              root_finished=lambda _: complete_step())
        if self.recycle:
            if self.cancel_flag.is_set():
                stats.recycle_bin = "etapa cancelada"
                stats.cancelled = True
            else:
                try:
                    stats.recycle_bin = empty_recycle_bin()
                    self.progress.emit(f"Lixeira: {stats.recycle_bin}.")
                    complete_step()
                except (OSError, RuntimeError) as exc:
                    stats.recycle_bin = "falhou"
                    stats.recycle_error = str(exc)
                    self.progress.emit(stats.recycle_error)
        if self.icons:
            if self.cancel_flag.is_set():
                stats.icon_cache = "etapa cancelada"
                stats.cancelled = True
            else:
                try:
                    removed, skipped = clear_icon_cache()
                    stats.icon_cache = f"{removed} removido(s), {skipped} preservado(s)"
                    self.progress.emit("O Windows recebeu o pedido para reconstruir os ícones.")
                    complete_step()
                except OSError as exc:
                    stats.icon_cache = "falhou"
                    self.progress.emit(f"Cache de ícones: {exc}")
        stats.cancelled = stats.cancelled or self.cancel_flag.is_set()
        return stats


def menu_icon(route: str, color: str = "#c7cefb") -> QIcon:
    """Ícones vetoriais monocromáticos com traçado consistente."""
    # Ícones com fundo próprio, independentes das fontes de emojis do Windows.
    paths = {
        "home": '<path d="M3 11 12 3l9 8v10h-7v-7h-4v7H3z"/>',
        "gamer": '<path d="M5 12h14l2 7-5-2-2-2h-4l-2 2-5 2z"/><path d="M8 12V9m-2 1h4m7 0h.01"/>',
        "edge": '<circle cx="12" cy="12" r="9"/><path d="M5 16c3-7 12-7 14-2M8 19l4-5"/>',
        "windows_update": '<path d="M20 11a8 8 0 0 0-14-5L4 8m0-5v5h5M4 13a8 8 0 0 0 14 5l2-2m0 5v-5h-5"/>',
        "startupapps": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m10 8 6 4-6 4z"/>',
        "network": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c5 5 5 13 0 18M12 3c-5 5-5 13 0 18"/>',
        "privacy": '<path d="M12 2 4 6v6c0 6 4 9 8 10 4-1 8-4 8-10V6z"/><path d="m9 12 2 2 4-4"/>',
        "repair": '<path d="m4 20 9-9M14 3a5 5 0 0 0 6 6l-6 6-5-5zM3 21l4-1"/>',
        "clean": '<path d="m15 9 5-6-2-1-5 6m-3 2 6 4-3 7-10-6 7-5Zm-3 4-2 3m6-1-2 3"/>',
        "boost": '<path d="M8 14c0-6 6-11 12-11 0 6-5 12-11 12l-1-1Zm0-4H5l-2 4h5m6 2v3l-4 2v-5m-4 1-3 4"/><circle cx="15" cy="8" r="1.5"/>',
        "classic": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 9v11"/>',
        "shutdown": '<path d="M12 2v10M6 5a9 9 0 1 0 12 0"/>',
        "winutil": '<path d="M4 4h16v16H4zM4 9h16m-10 0v11"/>',
        "updates": '<path d="M12 3v13m-5-5 5 5 5-5M4 20h16"/>',
        "restore_point": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2M7 6 5 4"/>',
        "restore": '<path d="M4 10h10a6 6 0 1 1-6 9M4 10l4-4M4 10l4 4"/>',
        "programs": '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
        "drivers": '<rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9 2v3m6-3v3M9 19v3m6-3v3M2 9h3m-3 6h3m14-6h3m-3 6h3"/>',
        "logs": '<path d="M4 6h16M4 12h16M4 18h16"/>',
        "about": '<circle cx="12" cy="12" r="9"/><path d="M12 10v7M12 7h.01"/>',
    }
    markup = paths.get(route, paths["about"])
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           f'fill="none" stroke="{color}" stroke-width="1.7" '
           'stroke-linecap="round" stroke-linejoin="round">' + markup + '</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def label(text: str, kind: str = "Muted", wrap: bool = True) -> QLabel:
    obj = QLabel(text)
    obj.setObjectName(kind)
    obj.setWordWrap(wrap)
    return obj


def compact_status() -> QLabel:
    status = label("")
    status.setTextFormat(Qt.TextFormat.PlainText)
    policy = status.sizePolicy()
    policy.setHorizontalPolicy(QSizePolicy.Policy.Ignored)
    status.setSizePolicy(policy)
    return status


def card_layout(variant: str = "Card", *, compact: bool = False) -> tuple[QFrame, QVBoxLayout]:
    outer = QFrame()
    outer.setObjectName(variant)
    layout = QVBoxLayout(outer)
    margin = 14 if compact else 22
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(7 if compact else 12)
    return outer, layout


def action_button(text: str, function, primary: bool = False, *, compact: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setObjectName("Primary")
    if compact:
        button.setProperty("compact", True)
        button.setFixedHeight(34)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.clicked.connect(function)
    return button


class ShortcutCard(QPushButton):
    def sizeHint(self):
        return self.layout().sizeHint()

    def minimumSizeHint(self):
        return self.layout().minimumSize()

    def heightForWidth(self, width):
        return self.layout().heightForWidth(width)


class CompactCardLayout(QLayout):
    """Measure and arrange each row using the same width, including wrapped labels."""

    MAX_COLUMNS = 3
    PREFERRED_CARD_WIDTH = 395
    GAP = 12

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(self.GAP)

    def addItem(self, item):
        self.items.append(item)
        self.invalidate()

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        return self.items[index] if 0 <= index < self.count() else None

    def takeAt(self, index):
        if self.itemAt(index) is None:
            return None
        item = self.items.pop(index)
        self.invalidate()
        return item

    def hasHeightForWidth(self):
        return True

    def minimumSize(self):
        size = QSize(0, 0)
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        return size

    def sizeHint(self):
        width = self.preferred_width(self.count())
        return QSize(width, self.heightForWidth(width))

    @classmethod
    def preferred_width(cls, count: int) -> int:
        columns = min(cls.MAX_COLUMNS, count)
        return columns * cls.PREFERRED_CARD_WIDTH + max(0, columns - 1) * cls.GAP

    def _rows(self, width: int):
        gap = self.spacing()
        columns = min(self.MAX_COLUMNS, max(1, (width + gap) // (275 + gap)))
        card_width = max(0, (width - (columns - 1) * gap) // columns)
        for start in range(0, self.count(), columns):
            items = self.items[start:start + columns]
            height = max(max(item.minimumSize().height(), item.heightForWidth(card_width)) for item in items)
            yield items, card_width, height

    def heightForWidth(self, width):
        heights = [height for _, _, height in self._rows(width)]
        return sum(heights) + max(0, len(heights) - 1) * self.spacing()

    def setGeometry(self, rect):
        super().setGeometry(rect)
        y = rect.y()
        gap = self.spacing()
        for items, width, height in self._rows(rect.width()):
            for column, item in enumerate(items):
                item.setGeometry(QRect(rect.x() + column * (width + gap), y, width, height))
            y += height + gap


class CompactGrid(QWidget):
    def __init__(self, cards: list[QFrame]):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = CompactCardLayout(self)
        for card in cards:
            layout.addWidget(card)
        self.setMaximumWidth(layout.sizeHint().width())


class NativeActionCard:
    def __init__(self, code: str, run_action):
        task = ACTIONS[code]
        self.reversal = REVERSIBLE_ACTIONS.get(code)
        title = self.reversal[1] if self.reversal else task["name"]
        self.widget, contents = card_layout(compact=True)
        self.title = label(title, "CardTitle")
        contents.addWidget(self.title)
        self.description = label("")
        contents.addWidget(self.description)
        self.warning = label("", "ActionWarning")
        contents.addWidget(self.warning)
        contents.addStretch()
        self.button = action_button("", lambda: run_action(self.code), True, compact=True)
        self.progress = TaskProgressBar(f"Progresso de {title}")
        self.execution = QStackedWidget()
        self.execution.setFixedSize(118, 34)
        self.execution.addWidget(self.button)
        self.execution.addWidget(self.progress)
        self.progress.setFixedHeight(34)
        contents.addWidget(self.execution, alignment=Qt.AlignmentFlag.AlignLeft)
        self.status = compact_status()
        self.status.hide()
        contents.addWidget(self.status)
        self.set_action(code)

    def set_action(self, code: str):
        self.code = code
        task = ACTIONS[code]
        if self.reversal:
            text = self.reversal[2] if code != self.reversal[0] else (
                "Restaurar" if code == "edge_restore" else "Reverter")
        else:
            text = "Executar"
        self.button.setText(text)
        self.button.setAccessibleName(f"{text} — {task['name']}")
        tooltip = task["name"]
        if task["admin"]:
            tooltip += " (requer administrador)"
        self.button.setToolTip(tooltip)
        self.description.setText(task["description"])
        self.warning.setText(task["warning"])
        self.warning.setVisible(bool(task["warning"]))


class MemoryRing(QWidget):
    def __init__(self):
        super().__init__()
        self.percent = None
        self.capacity = ""
        self.setFixedSize(146, 146)
        self.setAccessibleName("Uso de memória RAM")

    def set_usage(self, percent: int, capacity: str):
        self.percent = percent
        self.capacity = capacity
        self.setAccessibleDescription(f"{percent}% em uso, {capacity}")
        self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            track = QRectF(10, 10, 126, 126)
            painter.setPen(QPen(QColor("#273154"), 11))
            painter.drawEllipse(track)
            if self.percent is not None and self.percent > 0:
                spectrum = QConicalGradient(73, 73, 90)
                spectrum.setColorAt(0, QColor("#46dcf9"))
                spectrum.setColorAt(.5, QColor("#6a8cff"))
                spectrum.setColorAt(.86, QColor("#df72fb"))
                spectrum.setColorAt(1, QColor("#46dcf9"))
                pen = QPen(QBrush(spectrum), 11)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawArc(track, 90 * 16, -round(self.percent * 57.6))
            painter.setPen(QColor("#f5f4ff"))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(35)
            painter.setFont(font)
            value = "—" if self.percent is None else f"{self.percent}%"
            painter.drawText(QRectF(0, 28, 146, 48), Qt.AlignmentFlag.AlignCenter, value)
            font.setBold(False)
            font.setPixelSize(13)
            painter.setFont(font)
            painter.drawText(QRectF(0, 75, 146, 21), Qt.AlignmentFlag.AlignCenter, "RAM em uso")
            painter.drawText(QRectF(0, 97, 146, 19), Qt.AlignmentFlag.AlignCenter, self.capacity)


class WindowsMemoryStatus(ctypes.Structure):
    _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
        (name, ctypes.c_ulonglong) for name in
        ("total", "available", "page_total", "page_available", "virtual_total",
         "virtual_available", "extended_available")
    ]


def phoenix_art() -> QPixmap:
    """Usa o recorte da fênix da arte aprovada, sem os controles desenhados."""
    source = QPixmap(str(asset_dir().parent / "optima-approved-preview.jpg"))
    if source.isNull():
        return svg_icon("callas", 220).pixmap(220, 220)
    result = QPixmap(316, 231)
    result.fill(Qt.GlobalColor.transparent)
    outline = QPainterPath()
    outline.moveTo(5, 7)
    outline.lineTo(127, 0)
    outline.cubicTo(104, 39, 148, 74, 195, 68)
    outline.lineTo(314, 63)
    outline.lineTo(306, 190)
    outline.cubicTo(231, 193, 185, 225, 30, 231)
    outline.lineTo(35, 197)
    outline.cubicTo(100, 181, 64, 164, 12, 133)
    outline.closeSubpath()
    with QPainter(result) as painter:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(outline)
        painter.drawPixmap(0, 0, source, 875, 4, 316, 231)
        painter.setClipping(False)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        mask = QLinearGradient(0, 0, 316, 0)
        mask.setColorAt(0, QColor(0, 0, 0, 0))
        mask.setColorAt(.10, QColor(0, 0, 0, 255))
        mask.setColorAt(.88, QColor(0, 0, 0, 255))
        mask.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(result.rect(), mask)
    return result


class MainWindow(QMainWindow):
    dns_status_result = Signal(int, object)
    program_updates_result = Signal(object, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Callas Optima {APP_VERSION}  |  Windows Edition")
        self.setWindowIcon(app_icon())
        # Borda e controles nativos (incluindo maximizar); a janela pode ser redimensionada.
        self.setMinimumSize(810, 570)
        self.resize(1450, 850)
        self.settings = QSettings("Callas", "OptimizerWindows")
        self.cleaner: CleanerThread | None = None
        self.native_timer: QTimer | None = None
        self.native_controls: dict[str, NativeActionCard] = {}
        self.dns_status_request = 0
        self.dns_apply_buttons: dict[str, QPushButton] = {}
        self.dns_status_result.connect(self.update_dns_actions)
        self.extra_installer: ExtraInstallerThread | None = None
        self.vm_template_thread: VirtualBoxTemplateThread | None = None
        self.checking_program_updates = False
        self.program_updates_checked = False
        self.program_updates_result.connect(self.program_updates_done)
        self.extensions_job: BraveExtensionsThread | None = None
        self.installing_program: str | None = None
        self.program_controls = {}
        self.program_support_links = {}
        self.program_icons: dict[str, QLabel] = {}
        self.program_icon_sources: dict[str, Path | None] = {}
        self.program_icon_provider = QFileIconProvider()
        self.upgradeable_programs: set[str] = set()
        self.updater_process: subprocess.Popen | None = None
        self.update_timer: QTimer | None = None
        self.update_mode = ""
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.update_elapsed = 0
        self.pages: dict[str, QScrollArea] = {}
        self.page_titles: dict[str, str] = {}
        self.navigation_history: list[str] = []
        self.navigation_index = -1
        self.shutdown_countdown = QTimer(self)
        self.shutdown_countdown.setInterval(1000)
        self.shutdown_countdown.timeout.connect(self.refresh_shutdown_timer)

        self._main_area()
        self.goto("home")
        QApplication.instance().installEventFilter(self)

        try:
            runtime_files()
        except Exception as e:
            QMessageBox.warning(self, "Recursos indisponíveis", str(e))
            self.status_message("Alguns recursos não puderam ser preparados.")

        if os.environ.get("CALLAS_SMOKE") != "1" and self.settings.value("auto_update", True, type=bool):
            QTimer.singleShot(1800, lambda: self.check_update(False))

    def _main_area(self):
        central = QWidget()
        central.setObjectName("MainRoot")
        self.setCentralWidget(central)
        col = QVBoxLayout(central)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        bar = QFrame()
        bar.setObjectName("Topbar")
        bh = QHBoxLayout(bar)
        bh.setContentsMargins(25, 15, 24, 15)
        logo = QLabel()
        logo.setPixmap(header_logo())
        bh.addWidget(logo)
        bh.addSpacing(6)
        titles = QVBoxLayout()
        titles.setSpacing(3)
        titles.addWidget(label('Callas <span style="color:#7ca7ff">Optima</span>', "Header"))
        titles.addWidget(label("Desempenho e renovação"))
        bh.addLayout(titles, 1)
        self.home_button = action_button("Início", lambda: self.goto("home"), compact=True)
        self.home_button.setIcon(menu_icon("home"))
        bh.addWidget(self.home_button)
        self.top_check = action_button("Verificar atualização", lambda: self.check_update(True), compact=True)
        bh.addWidget(self.top_check)
        bh.addWidget(label("v" + APP_VERSION, "Section"))
        col.addWidget(bar)

        self.stack = QStackedWidget()
        col.addWidget(self.stack, 1)
        self._build_pages()

        foot = QFrame()
        foot.setObjectName("Topbar")
        fh = QHBoxLayout(foot)
        fh.setContentsMargins(20, 9, 20, 9)
        self.status_label = label("Pronto")
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        fh.addWidget(self.status_label, 1)
        fh.addWidget(label("Windows 11 x64", "Section", wrap=False))
        col.addWidget(foot)

    def _page(self, route: str, title: str, description: str = "", *,
              content_width: int | None = None) -> QVBoxLayout:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("PageContent")
        layout = QVBoxLayout(content)
        margin = 22
        layout.setContentsMargins(margin, 18, margin, margin)
        layout.setSpacing(15)
        if content_width is not None:
            content.setMaximumWidth(content_width + 2 * margin)
            scroll.viewport().setObjectName("PageContent")
            scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        if route != "home":
            layout.addWidget(label(title, "Title"))
        if description:
            layout.addWidget(label(description))
        scroll.setWidget(content)
        self.pages[route] = scroll
        self.page_titles[route] = title
        self.stack.addWidget(scroll)
        return layout

    def _build_pages(self):
        self._home_page()
        self._clean_page()
        self._program_page()
        self._drivers_page()
        self._update_page()
        self._logs_page()
        self._about_page()
        for route, (title, description) in TOOL_PAGES.items():
            self._tool_page(route, title, description)
        self.refresh_native_actions()

    def _home_page(self):
        col = self._page("home", "Início", content_width=1550)
        hero, hero_box = card_layout("Hero")
        hero_box.setContentsMargins(22, 14, 22, 14)
        row = QHBoxLayout()
        row.setSpacing(20)

        self.memory_ring = MemoryRing()
        row.addWidget(self.memory_ring, alignment=Qt.AlignmentFlag.AlignVCenter)
        metrics = QVBoxLayout()
        metrics.setSpacing(7)
        metrics.addWidget(label("Visão geral do sistema", "HeroTitle"))
        self.live_cpu = label("CPU  —", "SystemMetric")
        metrics.addWidget(self.live_cpu)
        metrics.addSpacing(4)
        metrics.addWidget(label("Armazenamento do sistema", "SystemMetric"))
        self.live_storage = label("—")
        metrics.addWidget(self.live_storage)
        self.storage_bar = QProgressBar()
        self.storage_bar.setAccessibleName("Armazenamento do sistema em uso")
        self.storage_bar.setFormat("%p% usado")
        metrics.addWidget(self.storage_bar)
        row.addLayout(metrics, 1)

        self.hero_art = phoenix_art()
        self.hero_phoenix = QLabel()
        self.hero_phoenix.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_phoenix.setAccessibleName("Fênix Callas Optima")
        row.addWidget(self.hero_phoenix, alignment=Qt.AlignmentFlag.AlignVCenter)
        hero_box.addLayout(row)
        col.addWidget(hero)

        col.addWidget(label("Atalhos principais", "CardTitle"))
        self.home_quick_grid = QGridLayout()
        self.home_quick_grid.setSpacing(12)
        self.home_tiles = []
        for index, (route, title, description) in enumerate(HOME_SHORTCUTS):
            tile = ShortcutCard()
            tile.setCursor(Qt.CursorShape.PointingHandCursor)
            tile.clicked.connect(lambda _=False, key=route: self.goto(key))
            tile_box = QVBoxLayout(tile)
            tile_box.setContentsMargins(16, 15, 16, 15)
            tile_box.setSpacing(8)
            tile.setObjectName("QuickCard")
            tile.setAccessibleName(title)
            tile.setAccessibleDescription(description)
            policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            policy.setHeightForWidth(True)
            tile.setSizePolicy(policy)
            cyan = index % 2 == 1
            tile.setProperty("accent", "cyan" if cyan else "violet")
            icon = QLabel()
            icon_route = "boost" if route == "gamer" else route
            icon.setPixmap(menu_icon(icon_route, "#37deff" if cyan else "#e6aaff").pixmap(32, 32))
            for item in (icon, label(title + "  ›", "CardTitle", wrap=False), label(description)):
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                tile_box.addWidget(item)
            tile_box.addStretch()
            self.home_tiles.append(tile)
        col.addLayout(self.home_quick_grid)

        tools, tools_box = card_layout("DashboardPanel", compact=True)
        tools_box.addWidget(label("Ferramentas do Windows", "CardTitle"))
        self.home_tools_grid = QGridLayout()
        self.home_tools_grid.setSpacing(8)
        self.home_tools = tools
        self.home_tool_buttons = []
        for route, title in WINDOWS_SHORTCUTS:
            action = self.open_windows_settings if route == "startupapps" else self.goto
            button = action_button(title, lambda _=False, run=action, key=route: run(key), compact=True)
            button.setObjectName("ToolShortcut")
            button.setIcon(menu_icon(route))
            self.home_tool_buttons.append(button)
        tools_box.addLayout(self.home_tools_grid)
        col.addWidget(tools)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer_buttons = []
        for route, title in APP_SHORTCUTS:
            button = action_button(title, lambda _=False, key=route: self.goto(key), compact=True)
            button.setIcon(menu_icon(route))
            footer.addWidget(button)
            footer_buttons.append(button)
        footer.addStretch()
        col.addLayout(footer)
        col.addStretch()

        self._cpu_snapshot = None
        self.home_timer = QTimer(self)
        self.home_timer.setInterval(2500)
        self.home_timer.timeout.connect(self.refresh_system_metrics)
        self._refresh_home_layout()
        tab_order = [self.pages["home"], *self.home_tiles, *self.home_tool_buttons, *footer_buttons]
        for previous, current in zip(tab_order, tab_order[1:]):
            self.setTabOrder(previous, current)

    def refresh_system_metrics(self):
        if os.name == "nt":
            self._refresh_windows_metrics()
        drive = Path(os.environ.get("SystemDrive", "C:") + "\\") if os.name == "nt" else Path.home()
        try:
            usage = shutil.disk_usage(drive)
            occupied = (usage.total - usage.free) * 100 // usage.total
        except (OSError, ZeroDivisionError):
            self.live_storage.setText("Armazenamento indisponível nesta sessão.")
            self.storage_bar.hide()
        else:
            free_gib = usage.free / 1024 ** 3
            total_gib = usage.total / 1024 ** 3
            self.live_storage.setText(f"{free_gib:.1f} GB livres de {total_gib:.1f} GB")
            self.storage_bar.setValue(occupied)
            self.storage_bar.show()

    def _refresh_windows_metrics(self):
        kernel = ctypes.windll.kernel32
        memory = WindowsMemoryStatus()
        memory.length = ctypes.sizeof(memory)
        if kernel.GlobalMemoryStatusEx(ctypes.byref(memory)):
            total = memory.total / 1024 ** 3
            used = (memory.total - memory.available) / 1024 ** 3
            self.memory_ring.set_usage(memory.load, f"{used:.1f} / {total:.1f} GB")
        idle, system, user = (ctypes.c_ulonglong() for _ in range(3))
        if kernel.GetSystemTimes(ctypes.byref(idle), ctypes.byref(system), ctypes.byref(user)):
            current = idle.value, system.value + user.value
            if self._cpu_snapshot:
                idle_delta = current[0] - self._cpu_snapshot[0]
                total_delta = current[1] - self._cpu_snapshot[1]
                if total_delta > 0:
                    usage = max(0, min(100, round(100 * (1 - idle_delta / total_delta))))
                    self.live_cpu.setText(f"CPU  {usage}%")
            self._cpu_snapshot = current

    def _refresh_home_layout(self):
        if not hasattr(self, "home_tools_grid"):
            return
        width = self.width()
        compact = width < 1050
        page = self.pages["home"]
        page_content = page.widget()
        page_margins = page_content.layout().contentsMargins()
        tool_margins = self.home_tools.layout().contentsMargins()
        content_width = min(width - page.verticalScrollBar().sizeHint().width(), page_content.maximumWidth())
        content_width -= page_margins.left() + page_margins.right()
        tool_width = content_width - tool_margins.left() - tool_margins.right() - 2 * self.home_tools.frameWidth()
        quick_columns = self._shortcut_columns(self.home_quick_grid, self.home_tiles, content_width)
        tool_columns = self._shortcut_columns(self.home_tools_grid, self.home_tool_buttons, tool_width)
        profile = (compact, quick_columns, tool_columns)
        if getattr(self, "_home_profile", None) == profile:
            return
        self._home_profile = profile
        self.hero_phoenix.setPixmap(self.hero_art.scaled(
            190 if compact else 275, 120 if compact else 160,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
        ))
        for grid, widgets, columns in (
            (self.home_quick_grid, self.home_tiles, quick_columns),
            (self.home_tools_grid, self.home_tool_buttons, tool_columns),
        ):
            while grid.count():
                grid.takeAt(0)
            # Dois espaços por cartão permitem centralizar uma última linha incompleta.
            for column in range(10):
                grid.setColumnStretch(column, int(column < 2 * columns))
            for index, widget in enumerate(widgets):
                row, column = divmod(index, columns)
                cards_in_row = min(columns, len(widgets) - row * columns)
                grid.addWidget(widget, row, 2 * column + columns - cards_in_row, 1, 2)

    @staticmethod
    def _shortcut_columns(grid: QGridLayout, buttons: list[QPushButton], width: int) -> int:
        gap = grid.spacing()
        button_width = max(button.minimumSizeHint().width() for button in buttons)
        return min(5, max(1, (width + gap) // (button_width + gap)))

    def open_windows_settings(self, page: str):
        """Abre somente páginas aprovadas do Windows; não altera configurações."""
        if page not in ("startupapps", "gaming-gamemode", "windowsupdate-optionalupdates"):
            return
        if os.name != "nt":
            QMessageBox.information(self, "Windows", "Disponível apenas no Windows 11.")
            return
        try:
            os.startfile("ms-settings:" + page)
            self.status_message("Configurações do Windows abertas: " + page)
        except OSError as exc:
            QMessageBox.warning(self, "Configurações", str(exc))

    def _drivers_page(self):
        col = self._page("drivers", "Drivers", "Acesso às ferramentas oficiais de atualização de drivers.")
        nvidia, body = card_layout(compact=True)
        body.addWidget(label("NVIDIA App", "CardTitle"))
        body.addWidget(label("Confira os drivers disponíveis e escolha quando instalá-los."))
        body.addStretch()
        body.addWidget(action_button("Ver em Programas", self._show_nvidia_card, True, compact=True),
                       alignment=Qt.AlignmentFlag.AlignLeft)
        windows, body = card_layout(compact=True)
        body.addWidget(label("Drivers pelo Windows", "CardTitle"))
        body.addWidget(label("Veja os drivers opcionais nas Configurações do Windows."))
        body.addStretch()
        body.addWidget(action_button("Abrir atualizações opcionais",
                                     lambda: self.open_windows_settings("windowsupdate-optionalupdates"),
                                     compact=True), alignment=Qt.AlignmentFlag.AlignLeft)
        col.addWidget(CompactGrid([nvidia, windows]))
        col.addStretch(1)

    def _show_nvidia_card(self):
        self.goto("programs")
        self.pages["programs"].ensureWidgetVisible(self.nvidia_card)

    def _tool_page(self, route, title, description):
        col = self._page(route, title, description)
        cards = []
        for action in BY_ROUTE[route]:
            code = action["id"]
            if code in ACTION_CARD_KEYS or code == "dns_auto":
                continue
            callback = self.configure_shutdown if code == "shutdown_custom" else self.native_action
            card = NativeActionCard(code, callback)
            self.native_controls[code] = card
            if code in DNS_PROVIDERS:
                button = action_button("Aplicar nas ativas",
                                       lambda _=False, selected=code: self.native_action(selected), compact=True)
                button.hide()
                card.widget.layout().addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
                self.dns_apply_buttons[code] = button
            cards.append(card.widget)
        col.addWidget(CompactGrid(cards))
        col.addWidget(action_button("Ver registros", lambda: self.goto("logs"), compact=True),
                      alignment=Qt.AlignmentFlag.AlignLeft)
        col.addStretch(1)

    def refresh_shutdown_timer(self):
        card = self.native_controls["shutdown_custom"]
        minutes = remaining_shutdown_minutes()
        if minutes is None:
            card.title.setText(ACTIONS["shutdown_custom"]["name"])
            card.description.setText(ACTIONS["shutdown_custom"]["description"])
            card.button.setText("Configurar")
        else:
            unit = "minuto" if minutes == 1 else "minutos"
            card.title.setText(f"Desligando em {minutes} {unit}")
            card.description.setText("O Windows mantém o agendamento mesmo com o Callas fechado.")
            card.button.setText("Reagendar")
        card.button.setAccessibleName(f"{card.button.text()} — {card.title.text()}")

    def configure_shutdown(self, code: str):
        if self.native_timer is not None or self.update_mode == "install":
            return
        dialog = QDialog(self)
        dialog.setObjectName("ShutdownDialog")
        dialog.setWindowTitle("Desligamento personalizado")
        dialog.setFixedWidth(360)
        panel = QVBoxLayout(dialog)
        panel.setContentsMargins(18, 16, 18, 16)
        panel.setSpacing(10)
        prompt = label("Desligar em quantos minutos?", "CardTitle")
        panel.addWidget(prompt)

        minutes = QSpinBox()
        minutes.setObjectName("ShutdownMinutes")
        minutes.setRange(1, MAX_SHUTDOWN_MINUTES)
        minutes.setSuffix(" min")
        minutes.setValue(remaining_shutdown_minutes() or 30)
        prompt.setBuddy(minutes)
        minutes.setAccessibleName("Tempo até o desligamento, em minutos")
        panel.addWidget(minutes)
        presets = QHBoxLayout()
        for value in (15, 30, 60):
            preset = action_button(f"{value} min", lambda _=False, n=value: minutes.setValue(n), compact=True)
            preset.setAutoDefault(False)
            presets.addWidget(preset)
        panel.addLayout(presets)
        panel.addWidget(label("Salve seus arquivos antes do desligamento. O novo tempo substitui o agendamento atual.",
                              "ActionWarning"))
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = action_button("Voltar", dialog.reject, compact=True)
        submit = action_button("Agendar", dialog.accept, True, compact=True)
        cancel.setAutoDefault(False)
        submit.setDefault(True)
        buttons.addWidget(cancel)
        buttons.addWidget(submit)
        panel.addLayout(buttons)

        dialog.adjustSize()
        dialog.move(self.frameGeometry().center() - dialog.rect().center())
        minutes.setFocus()
        minutes.selectAll()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.native_action(code, shutdown_minutes=minutes.value())
        dialog.deleteLater()

    def refresh_native_actions(self):
        edge = "edge_uninstall"
        self.native_controls[edge].set_action(edge if edge_installed() else "edge_restore")
        try:
            applied = applied_action_backups()
        except RuntimeError:
            return  # Preserve the current buttons if the backup cannot be read.
        for code, (undo, _, _) in REVERSIBLE_ACTIONS.items():
            if code != edge and code not in DNS_PROVIDERS:
                self.native_controls[code].set_action(undo if code in applied else code)

    def refresh_dns_actions(self):
        if os.name != "nt" or self.native_timer is not None:
            return
        self.dns_status_request += 1
        request = self.dns_status_request
        for code in DNS_PROVIDERS:
            self.native_controls[code].button.setEnabled(False)
            self.dns_apply_buttons[code].setEnabled(False)

        def check():
            try:
                active = dns_provider_status()
            except (OSError, RuntimeError, subprocess.SubprocessError):
                active = None
            try:
                self.dns_status_result.emit(request, active)
            except RuntimeError:
                pass  # The window may have been closed during the query.

        threading.Thread(target=check, daemon=True).start()

    @Slot(int, object)
    def update_dns_actions(self, request: int, active):
        if request != self.dns_status_request:
            return
        if active is None and self.stack.currentWidget() is self.pages["network"]:
            self.status_message("Não foi possível consultar o DNS. Reabra a aba Rede e DNS para tentar novamente.")
        available = active is not None and self.native_timer is None
        for code in DNS_PROVIDERS:
            card = self.native_controls[code]
            if active is not None:
                card.set_action(card.reversal[0] if code in active else code)
            card.button.setEnabled(available)
            apply_button = self.dns_apply_buttons[code]
            apply_button.setVisible(available and active.get(code, False))
            apply_button.setEnabled(available)

    def _clean_page(self):
        col = self._page("clean", "Limpeza Total", "Limpeza nativa com progresso, cancelamento e registro de arquivos ignorados.")
        settings, content = card_layout()
        content.addWidget(label("ESCOLHA O QUE LIMPAR", "Section"))
        self.clean_user = QCheckBox("Arquivos temporários do usuário")
        self.clean_user.setChecked(True)
        self.clean_windows = QCheckBox("Pasta temporária do Windows (pode exigir administrador)")
        self.clean_recycle = QCheckBox("Esvaziar a Lixeira do Windows")
        self.clean_icons = QCheckBox("Limpar e reconstruir o cache de ícones do Windows")
        self.clean_nvidia = QCheckBox("Cache de shaders NVIDIA (DXCache)")
        self.clean_nvidia.setToolTip("Os jogos podem recompilar shaders na próxima abertura.")
        for chk in (self.clean_user, self.clean_windows, self.clean_recycle, self.clean_icons, self.clean_nvidia):
            content.addWidget(chk)
        content.addWidget(label("Não apaga Prefetch, documentos, senhas, favoritos, logs de sistema ou a pasta do Callas Optimizer."))
        buttons = QHBoxLayout()
        self.clean_start = action_button("INICIAR LIMPEZA", self.start_clean, True)
        self.clean_stop = action_button("CANCELAR", self.cancel_clean)
        self.clean_stop.setEnabled(False)
        buttons.addWidget(self.clean_start)
        buttons.addWidget(self.clean_stop)
        buttons.addStretch()
        content.addLayout(buttons)
        col.addWidget(settings)
        progress, panel = card_layout()
        panel.addWidget(label("PROGRESSO E RESULTADO", "Section"))
        self.clean_progress = TaskProgressBar("Progresso da limpeza")
        panel.addWidget(self.clean_progress)
        self.clean_output = QPlainTextEdit()
        self.clean_output.setReadOnly(True)
        self.clean_output.setMinimumHeight(145)
        self.clean_output.setPlainText("Selecione o escopo e clique em INICIAR LIMPEZA.")
        panel.addWidget(self.clean_output)
        col.addWidget(progress)
        col.addStretch()

    def set_program_icon(self, app_id: str, executable: Path | None = None):
        if app_id in self.program_icon_sources and self.program_icon_sources[app_id] == executable:
            return
        size = QSize(42, 42)
        scale = self.devicePixelRatioF()
        pixmap = QPixmap()
        if executable and QApplication.platformName() == "windows":
            pixmap = self.program_icon_provider.icon(QFileInfo(str(executable))).pixmap(size, scale)
        if pixmap.isNull():
            bundled = asset_dir() / f"{app_id}.png"
            icon = QIcon(str(bundled)) if bundled.is_file() else svg_icon(app_id, 100)
            pixmap = icon.pixmap(size, scale)
        self.program_icons[app_id].setPixmap(pixmap)
        self.program_icon_sources[app_id] = executable

    def _program_card(self, name: str, icon: str, description: str, action_title: str, action):
        outer, content = card_layout(compact=True)
        content.setContentsMargins(13, 10, 13, 10)
        row = QHBoxLayout()
        row.setSpacing(10)
        img = QLabel()
        img.setFixedSize(44, 44)
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.program_icons[icon] = img
        self.set_program_icon(icon)
        row.addWidget(img, alignment=Qt.AlignmentFlag.AlignTop)
        details = QVBoxLayout()
        details.setSpacing(3)
        details.addWidget(label(name, "ProgramTitle"))
        details.addWidget(label(description))
        details.addStretch()
        row.addLayout(details, 1)
        content.addLayout(row)

        actions = QHBoxLayout()
        primary = action_button(action_title, action, True, compact=True)
        upgrade = action_button("Atualizar", lambda: self.install_extra(icon, upgrade=True), compact=True)
        for button in (primary, upgrade):
            button.setFixedSize(84, 32)
            actions.addWidget(button)
        actions.addStretch()
        content.addLayout(actions)

        progress = TaskProgressBar(f"Progresso de {name}")
        progress.setFixedHeight(32)
        progress.hide()
        content.addWidget(progress)
        status = compact_status()
        status.hide()
        content.addWidget(status)
        support = action_button("Abrir site oficial", lambda: webbrowser.open(official_website(program_key(icon))),
                                compact=True)
        support.hide()
        content.addWidget(support, alignment=Qt.AlignmentFlag.AlignLeft)
        self.program_support_links[icon] = support
        self.program_controls[icon] = primary, upgrade, progress, status
        return outer

    def _program_page(self):
        col = self._page(
            "programs", "Central de aplicativos", "Instale, abra e atualize seus aplicativos.",
            content_width=CompactCardLayout.preferred_width(CompactCardLayout.MAX_COLUMNS),
        )
        self.program_update_button = action_button("Verificar atualizações dos apps", self.check_program_updates,
                                                   compact=True)
        col.addWidget(self.program_update_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.program_updates_progress = TaskProgressBar("Progresso da verificação pelo WinGet")
        self.program_updates_progress.hide()
        col.addWidget(self.program_updates_progress)
        self.program_updates_status = label("")
        self.program_updates_status.hide()
        col.addWidget(self.program_updates_status)
        self.brave_card = self._program_card(
            "Brave Browser", "brave", "Navegador com configuração opcional de SteamDB e Bonjourr", "Instalar",
            lambda: self.install_extra("brave"))
        self.nvidia_card = self._program_card(
            "NVIDIA App", "nvidia", "Gerencie drivers e configurações da GPU", "Instalar",
            lambda: self.install_extra("nvidia"))
        self.medal_card = self._program_card(
            "Medal", "medal", "Gravação de clipes e melhores momentos", "Instalar",
            lambda: self.install_extra("medal"))
        self.lghub_card = self._program_card(
            "Logitech G HUB", "lghub", "Configuração de periféricos Logitech G", "Instalar",
            lambda: self.install_extra("lghub"))
        self.spotify_card = self._program_card(
            "Spotify", "spotify", "Aplicativo de música para Windows", "Instalar",
            lambda: self.install_extra("spotify"))
        self.chatgpt_card = self._program_card(
            "ChatGPT", "chatgpt", "Chat, Work e Codex no aplicativo oficial para Windows",
            "Instalar",
            lambda: self.install_extra("chatgpt"))
        self.codex_card = self._program_card(
            "Codex", "codex", "Incluído no mesmo aplicativo do ChatGPT para Windows",
            "Instalar",
            lambda: self.install_extra("codex"))
        self.discord_card = self._program_card(
            "Discord", "discord", "Conversas, comunidades e voz", "Instalar",
            lambda: self.install_extra("discord"))
        self.steam_card = self._program_card(
            "Steam", "steam", "Biblioteca de jogos para PC", "Instalar",
            lambda: self.install_extra("steam"))
        self.epic_card = self._program_card(
            "Epic Games Launcher", "epic", "Loja e biblioteca Epic Games", "Instalar",
            lambda: self.install_extra("epic"))
        self.wise_card = self._program_card(
            "Wise Program Uninstaller", "wise", "Desinstalação de aplicativos", "Instalar",
            lambda: self.install_extra("wise"))
        self.virtualbox_card = self._program_card(
            "Oracle VirtualBox", "virtualbox", "Crie e execute máquinas virtuais no Windows", "Instalar",
            lambda: self.install_extra("virtualbox"))
        self.all_program_cards = [
            self.brave_card, self.nvidia_card, self.discord_card, self.steam_card,
            self.epic_card, self.wise_card, self.virtualbox_card, self.medal_card,
            self.lghub_card, self.spotify_card, self.chatgpt_card, self.codex_card,
        ]
        col.addWidget(CompactGrid(self.all_program_cards))
        lab_card, lab = card_layout(compact=True)
        lab.addWidget(label("Laboratório VirtualBox", "CardTitle"))
        lab.addWidget(label(
            "Prepare duas VMs, uma para Windows 11 Pro e outra para IoT Enterprise LTSC. "
            "Você escolhe a pasta e adiciona as ISOs depois."
        ))
        lab.addStretch()
        self.vm_template_button = action_button(
            "PREPARAR / AJUSTAR 2 VMS", self.prepare_virtualbox_templates, True, compact=True)
        lab.addWidget(self.vm_template_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.vm_template_progress = TaskProgressBar("Progresso da preparação das VMs")
        self.vm_template_progress.hide()
        lab.addWidget(self.vm_template_progress)
        self.vm_template_status = compact_status()
        self.vm_template_status.hide()
        lab.addWidget(self.vm_template_status)
        openai_card, openai_box = card_layout(compact=True)
        openai_box.addWidget(label("ChatGPT e Codex", "CardTitle"))
        openai_box.addWidget(label(
            "O Codex já vem no ChatGPT para Windows. Entre na sua conta e escolha a pasta "
            "do projeto que deseja usar."
        ))
        openai_box.addStretch()
        openai_box.addWidget(action_button(
            "Como usar arquivos locais",
            lambda: webbrowser.open("https://learn.chatgpt.com/pt-BR/docs/quickstart"),
            compact=True), alignment=Qt.AlignmentFlag.AlignLeft)
        c, box = card_layout(compact=True)
        box.addWidget(label("Extensões do Brave", "CardTitle"))
        box.addWidget(label("Configure SteamDB e Bonjourr. O Brave poderá exibir 'Gerenciado pela organização'."))
        box.addStretch()
        row = QHBoxLayout()
        self.extension_buttons = (
            action_button("Configurar", lambda: self.configure_brave_extensions(False), True, compact=True),
            action_button("Desfazer", lambda: self.configure_brave_extensions(True), compact=True),
        )
        for button in self.extension_buttons:
            row.addWidget(button)
        row.addStretch()
        box.addLayout(row)
        self.extensions_progress = TaskProgressBar("Progresso das políticas do Brave")
        self.extensions_progress.hide()
        box.addWidget(self.extensions_progress)
        self.extensions_status = compact_status()
        box.addWidget(self.extensions_status)
        col.addWidget(CompactGrid([lab_card, openai_card, c]))
        col.addStretch(1)
        self.refresh_program_cards()

    def _update_page(self):
        col = self._page("updates", "Atualizações", "Verificação automática pelo GitHub Releases, sempre com sua autorização.")
        c, inner = card_layout()
        inner.addWidget(label("CANAL ESTÁVEL", "Section"))
        inner.addWidget(label("Versão atual: " + APP_VERSION, "CardTitle"))
        inner.addWidget(label("Instalado em Program Files" if installed_mode() else "Edição portátil — instalador em Sobre"))
        self.update_note = label("Pronto para consultar as Releases oficiais.")
        self.update_note.setTextFormat(Qt.TextFormat.PlainText)
        inner.addWidget(self.update_note)
        self.update_progress = TaskProgressBar("Progresso da atualização do Callas")
        inner.addWidget(self.update_progress)
        row = QHBoxLayout()
        self.update_check = action_button("VERIFICAR AGORA", lambda: self.check_update(True), True)
        row.addWidget(self.update_check)
        row.addWidget(action_button("VER RELEASES", lambda: webbrowser.open(PROJECT_URL + "/releases")))
        inner.addLayout(row)
        col.addWidget(c)
        options, controls = card_layout()
        controls.addWidget(label("PREFERÊNCIAS", "Section"))
        auto = QCheckBox("Verificar novas versões ao abrir o aplicativo")
        auto.setChecked(self.settings.value("auto_update", True, type=bool))
        auto.toggled.connect(lambda flag: self.settings.setValue("auto_update", flag))
        controls.addWidget(auto)
        controls.addWidget(label("A instalação automática usa o Setup oficial após confirmação e verificação SHA-256."))
        col.addWidget(options)
        col.addStretch()

    def _logs_page(self):
        col = self._page("logs", "Registros", "Histórico de manutenção, instalações e atualizações.")
        box, layout = card_layout()
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(370)
        layout.addWidget(self.log_view)
        row = QHBoxLayout()
        row.addWidget(action_button("RECARREGAR", self.load_logs, True))
        row.addWidget(action_button("ABRIR PASTA DE LOGS", self.open_log_folder))
        layout.addLayout(row)
        col.addWidget(box)
        col.addStretch()

    def _about_page(self):
        col = self._page("about", "Sobre o Callas Optima")
        about, body = card_layout(compact=True)
        about.setMaximumWidth(620)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(svg_icon("callas", 48).pixmap(48, 48))
        brand.addWidget(logo)
        details = QVBoxLayout()
        details.setSpacing(4)
        details.addWidget(label("Callas Optima", "CardTitle"))
        details.addWidget(label(f"Versão {APP_VERSION} · Windows 11 x64"))
        brand.addLayout(details, 1)
        body.addLayout(brand)
        body.addWidget(label(
            "Ferramentas para limpar, reparar e ajustar o Windows 11, além de instalar e atualizar programas."
        ))
        installed = installed_mode()
        body.addWidget(label("Instalado em Program Files" if installed else "Edição portátil"))
        links = QHBoxLayout()
        links.addWidget(action_button("Abrir repositório", lambda: webbrowser.open(PROJECT_URL), compact=True))
        if not installed:
            links.addWidget(action_button(
                "Obter instalador oficial", lambda: webbrowser.open(PROJECT_URL + "/releases/latest"), compact=True,
            ))
        links.addStretch()
        body.addLayout(links)
        col.addWidget(about)
        col.addStretch()

    def step_navigation(self, delta: int):
        index = self.navigation_index + delta
        if 0 <= index < len(self.navigation_history):
            self.navigation_index = index
            self.goto(self.navigation_history[index], remember=False)

    def eventFilter(self, watched, event):
        if isinstance(watched, QWidget) and watched.window() is self:
            event_type = event.type()
            if event_type in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
                              QEvent.Type.MouseButtonDblClick):
                mouse_button = event.button()
                if mouse_button in (Qt.MouseButton.BackButton, Qt.MouseButton.ForwardButton):
                    if event_type == QEvent.Type.MouseButtonRelease:
                        self.step_navigation(-1 if mouse_button == Qt.MouseButton.BackButton else 1)
                    return True
            if event_type == QEvent.Type.KeyPress:
                key = event.key()
                if key in (Qt.Key.Key_Back, Qt.Key.Key_Forward):
                    if not event.isAutoRepeat():
                        self.step_navigation(-1 if key == Qt.Key.Key_Back else 1)
                    return True
        return super().eventFilter(watched, event)

    def goto(self, route: str, *, remember: bool = True):
        if route not in self.pages:
            return
        if remember and (self.navigation_index < 0 or self.navigation_history[self.navigation_index] != route):
            del self.navigation_history[self.navigation_index + 1:]
            self.navigation_history.append(route)
            self.navigation_index += 1
        self.stack.setCurrentWidget(self.pages[route])
        self.home_button.setVisible(route != "home")
        if route == "logs":
            self.load_logs()
        self.status_message("Seção aberta: " + self.page_titles[route])
        if route == "home":
            self.refresh_system_metrics()
            self.home_timer.start()
        else:
            self.home_timer.stop()
        if route == "shutdown":
            self.refresh_shutdown_timer()
            self.shutdown_countdown.start()
        else:
            self.shutdown_countdown.stop()
        if route in TOOL_PAGES and self.native_timer is None:
            self.refresh_native_actions()
        if route == "network":
            self.refresh_dns_actions()
        if route == "programs":
            self.refresh_program_cards()
            if not self.program_updates_checked:
                self.check_program_updates(automatic=True)

    def status_message(self, message: str):
        self.status_label.setText(message)

    def native_action(self, code: str, *, shutdown_minutes: int | None = None):
        if self.update_mode == "install":
            self.status_message("Aguarde a atualização do Callas Optima.")
            return
        task = ACTIONS.get(code)
        if task is None:
            return
        if self.native_timer is not None:
            self.status_message("Em execução: " + self.native_task_name)
            return
        message = task["name"] + "\n\n" + task["description"]
        if task["warning"]:
            message += "\n\nATENÇÃO: " + task["warning"]
        if task["admin"]:
            message += "\n\nO Windows solicitará permissão de administrador."
        if code == "shutdown_custom":
            if shutdown_minutes is None:
                return
        elif not confirmar(self, "Confirmação da operação", message):
            return
        if self.update_mode == "install" or self.native_timer is not None:
            return
        self.native_report = ACTION_HOME / ("acao-" + uuid.uuid4().hex + ".json")
        self.native_progress_file = self.native_report.with_suffix(".progress")
        self.native_code = code
        self.native_task_name = task["name"]
        card = self.native_controls[ACTION_CARD_KEYS.get(code, code)]
        self.active_native_card = card
        card.progress.begin()
        card.execution.setCurrentWidget(card.progress)
        card.status.setText("Aguardando permissão do Windows…" if task["admin"] else "Executando…")
        card.status.show()
        for control in self.native_controls.values():
            control.button.setEnabled(False)
        for provider, button in self.dns_apply_buttons.items():
            button.setEnabled(False)
            if task["route"] == "network" and self.native_controls[provider] is not card:
                self.native_controls[provider].status.hide()
        if os.name != "nt":
            self.finish_native_action(False, "Esta opção exige Windows.")
            return
        script_args = [] if getattr(sys, "frozen", False) else [str(Path(__file__).resolve())]
        args = [*script_args, "--callas-task", code, "--callas-report", self.native_report.name,
                "--callas-profile", str(ACTION_HOME)]
        if code == "shutdown_custom":
            args.extend(("--shutdown-minutes", str(shutdown_minutes)))
        try:
            ACTION_HOME.mkdir(parents=True, exist_ok=True)
            if task["admin"]:
                self.native_process = ElevatedAction(sys.executable, args)
            else:
                self.native_process = subprocess.Popen(
                    [sys.executable, *args],
                    cwd=str(ACTION_HOME),
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception as exc:
            detail = "Permissão UAC cancelada." if getattr(exc, "winerror", None) == 1223 else str(exc)
            self.finish_native_action(False, detail)
            return
        card.status.setText("Executando…")
        self.status_message(self.native_task_name + " em execução")
        self.native_timer = QTimer(self)
        self.native_timer.timeout.connect(self.poll_native_action)
        self.native_timer.start(230)

    def poll_native_action(self):
        if self.native_timer is None:
            return
        try:
            pending = json.loads(self.native_progress_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pending = None
        percent = pending.get("percent") if isinstance(pending, dict) else None
        if type(percent) is int and 0 <= percent <= 99:
            progress = self.active_native_card.progress
            progress.advance(max(progress.value(), percent))
        try:
            code = self.native_process.poll()
            if code is None:
                return
            try:
                outcome = json.loads(self.native_report.read_text(encoding="utf-8"))
                if (not isinstance(outcome, dict) or type(outcome.get("ok")) is not bool
                        or not isinstance(outcome.get("message"), str)):
                    raise ValueError("Relatório incompleto.")
                ok = code == 0 and outcome["ok"]
                message = outcome["message"] or f"Resultado da ferramenta (código {code})."
            except FileNotFoundError:
                ok = False
                if code == PROFILE_MISMATCH:
                    message = ("A elevação abriu outro perfil do Windows. Entre na conta de administrador, "
                               "abra o Callas e execute a ferramenta nessa conta.")
                else:
                    message = f"A ferramenta encerrou sem deixar relatório para este usuário (código {code})."
        except (OSError, ValueError) as exc:
            ok = False
            message = f"Não foi possível obter o resultado: {exc}"
        for path in (self.native_report, self.native_progress_file):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        self.native_timer.stop()
        self.native_timer.deleteLater()
        self.native_timer = None
        self.native_process = None
        self.finish_native_action(ok, message)

    def finish_native_action(self, ok: bool, message: str):
        card = self.active_native_card
        self.refresh_native_actions()
        if (ok and self.native_code in ACTION_CARD_KEYS and self.native_code not in DNS_REVERSALS
                and card.code == self.native_code and self.native_code != "edge_restore"):
            ok = False  # A previous setting is still backed up after the restore attempt.
        card.progress.finish(ok)
        card.execution.setCurrentWidget(card.button)
        outcome = "Concluído." if ok else "Falhou."
        lines = [line.strip() for line in message.splitlines() if line.strip()]
        detail = "\n".join(lines)
        if len(detail) > 360 or len(lines) > 4:
            summary_prefixes = (
                "o windows verificou", "o windows examinou", "windows has scanned",
                "a proteção de recursos", "windows resource protection",
                "the restore operation", "a operação de restauração",
            )
            summary = next((line for line in reversed(lines) if line.casefold().startswith(summary_prefixes)), "")
            if not ok:
                summary = " ".join(lines[:2])
            detail = (summary[:260] + "\n" if summary else "") + "Saída em Registros."
        card.status.setText(outcome + ("\n" + detail if detail else ""))
        card.status.setVisible(not (ok and self.native_code == "shutdown_custom"))
        if ACTIONS[self.native_code]["route"] == "shutdown":
            self.refresh_shutdown_timer()
        for control in self.native_controls.values():
            control.button.setEnabled(True)
        self.status_message(self.native_task_name + (" concluído" if ok else " falhou"))
        if self.stack.currentWidget() is self.pages["network"]:
            self.refresh_dns_actions()

    def configure_brave_extensions(self, undo: bool):
        if self.update_mode == "install" or (self.extensions_job and self.extensions_job.isRunning()):
            return
        if not undo and not installed_program("brave"):
            self.extensions_status.setText("Instale o Brave antes de configurar as extensões.")
            return
        message = ("Remover as políticas de SteamDB e Bonjourr adicionadas pelo Callas?" if undo
                   else "Adicionar SteamDB e Bonjourr por política local? O Brave poderá exibir "
                        "'Gerenciado pela organização'.")
        if not confirmar(self, "Extensões do Brave", message):
            return
        if self.update_mode == "install":
            return
        self.extensions_status.setText("Aplicando alteração…")
        self.extensions_progress.begin()
        self.extensions_progress.show()
        for button in self.extension_buttons:
            button.setEnabled(False)
        self.extensions_job = BraveExtensionsThread(undo)
        self.extensions_job.result.connect(self.brave_extensions_done)
        self.extensions_job.start()

    @Slot(bool, str)
    def brave_extensions_done(self, ok: bool, message: str):
        self.extensions_progress.finish(ok)
        self.extensions_progress.hide()
        for button in self.extension_buttons:
            button.setEnabled(True)
        self.extensions_status.setText(message)
        self.status_message("Extensões do Brave: concluído." if ok else "Extensões do Brave: falha.")

    def refresh_program_cards(self):
        installed = {key: installed_program(key) for key in EXTRA_APPS}
        for app_id, (primary, upgrade, _, _) in self.program_controls.items():
            key = program_key(app_id)
            if app_id in NATIVE_PROGRAM_ICONS:
                target = installed[key]
                self.set_program_icon(app_id, target if isinstance(target, Path) else None)
            primary.setText("Abrir" if installed[key] else "Instalar")
            primary.setVisible(self.installing_program != key)
            primary.setEnabled(not self.installing_program)
            upgrade.setVisible(installed[key] is not None and self.installing_program != key)
            upgrade.setEnabled(not self.installing_program)
            available = key in self.upgradeable_programs
            if upgrade.property("updateAvailable") != available:
                upgrade.setProperty("updateAvailable", available)
                upgrade.style().unpolish(upgrade)
                upgrade.style().polish(upgrade)
            detail = ("Atualização disponível pelo WinGet." if available
                      else "Procurar uma atualização para este aplicativo.")
            upgrade.setToolTip(detail)
            upgrade.setAccessibleDescription(detail)

    def check_program_updates(self, automatic=False):
        if self.checking_program_updates or self.installing_program:
            return
        self.checking_program_updates = True
        self.program_updates_checked = True
        self.program_update_button.setEnabled(False)
        self.program_updates_progress.begin()
        self.program_updates_progress.show()
        self.program_updates_status.setText("Verificando atualizações pelo WinGet…")
        self.program_updates_status.show()

        def check():
            try:
                upgrades = available_upgrades()
            except (OSError, RuntimeError, subprocess.SubprocessError):
                upgrades = None
            try:
                self.program_updates_result.emit(upgrades, automatic)
            except RuntimeError:
                pass  # A janela pode ter sido fechada durante a consulta.

        threading.Thread(target=check, daemon=True).start()

    @Slot(object, bool)
    def program_updates_done(self, upgrades, automatic: bool):
        self.checking_program_updates = False
        self.program_update_button.setEnabled(True)
        self.upgradeable_programs = upgrades or set()
        self.refresh_program_cards()
        self.program_updates_progress.finish(upgrades is not None)
        self.program_updates_progress.hide()
        if upgrades is None:
            message = "Consulta do WinGet indisponível. Use Atualizar no cartão do aplicativo."
        elif upgrades:
            message = "Os botões em destaque indicam os apps com atualização no WinGet."
        else:
            message = "O WinGet não encontrou atualizações para os aplicativos do catálogo."
        self.program_updates_status.setText(message)
        self.program_updates_status.show()

    def prepare_virtualbox_templates(self):
        if self.update_mode == "install" or (self.vm_template_thread and self.vm_template_thread.isRunning()):
            return
        try:
            get_vboxmanage()
        except Exception as exc:
            self.vm_template_status.setText(str(exc))
            self.vm_template_status.show()
            return
        folder = QFileDialog.getExistingDirectory(
            self, "Escolha o disco ou pasta para as duas VMs",
            str(Path.home()), QFileDialog.Option.ShowDirsOnly)
        if not folder:
            return
        info = (
            "Criar as seguintes máquinas no VirtualBox?\n\n"
            + "\n".join("• " + name for name in VM_NAMES)
            + "\n\nCada máquina: 6 GB RAM, 5 vCPUs, VDI dinâmico até 80 GB, "
            "UEFI / TPM 2.0 / Secure Boot.\n"
            "Texto/links: copiar do PC para a VM (requer Guest Additions).\n"
            "Arrastar arquivos e transferir arquivos pelo clipboard: DESATIVADO.\n"
            "O Windows NÃO será instalado e nenhuma ISO será baixada.\n"
            "VMs Callas existentes e desligadas terão só CPU e compartilhamento ajustados.\n"
            "Máquinas em execução não serão alteradas. Discos e dados preservados.\n\n"
            "Destino: " + folder
        )
        if not confirmar(self, "Preparar laboratório Windows 11", info):
            return
        if self.update_mode == "install":
            return
        self.vm_template_button.setEnabled(False)
        self.vm_template_progress.begin()
        self.vm_template_progress.show()
        self.vm_template_status.setText("Preparando as máquinas no VirtualBox…")
        self.vm_template_status.show()
        self.vm_template_thread = VirtualBoxTemplateThread(Path(folder))
        self.vm_template_thread.progress.connect(self.vm_template_status.setText)
        self.vm_template_thread.percent.connect(self.vm_template_progress.advance)
        self.vm_template_thread.result.connect(self.virtualbox_templates_finished)
        self.vm_template_thread.start()

    @Slot(bool, str)
    def virtualbox_templates_finished(self, ok: bool, message: str):
        self.vm_template_progress.finish(ok)
        self.vm_template_progress.hide()
        self.vm_template_button.setEnabled(True)
        self.vm_template_status.setText(message)
        self.status_message("Máquinas de teste preparadas." if ok else "Erro ao preparar VMs.")

    def install_extra(self, app_id: str, upgrade: bool = False):
        app_id = program_key(app_id)
        if self.installing_program or (self.extra_installer and self.extra_installer.isRunning()):
            return
        if self.update_mode == "install" and self.updater_process:
            self.status_message("Aguarde a atualização do Callas Optima.")
            return
        name = EXTRA_APPS[app_id]["name"]
        if not upgrade and (installed := installed_program(app_id)):
            try:
                open_program(installed)
                message = f"{name} aberto."
            except OSError as exc:
                message = f"Falha ao abrir {name}: {exc}"
            for card, (_, _, progress, status) in self.program_controls.items():
                if program_key(card) == app_id:
                    progress.hide()
                    status.setText(message)
                    status.show()
            self.status_message(message)
            return
        if upgrade and not installed_program(app_id):
            self.refresh_program_cards()
            return
        message = (f"Verificar e atualizar {name} pela fonte oficial?" if upgrade else
                   f"Instalar {name}? A assinatura digital será conferida antes da execução.")
        if not confirmar(self, "Instalador oficial", message):
            return
        if self.update_mode == "install":
            return
        self.installing_program = app_id
        self.refresh_program_cards()
        self.show_program_progress("Preparando…", -1)
        self.extra_installer = ExtraInstallerThread(app_id, upgrade)
        self.extra_installer.progress.connect(self.show_program_progress)
        self.extra_installer.result.connect(self.extra_installer_done)
        self.extra_installer.start()

    @Slot(str, int)
    def show_program_progress(self, message: str, percent: int):
        if self.installing_program is None:
            return
        for card, (primary, upgrade, progress, status) in self.program_controls.items():
            if program_key(card) != self.installing_program:
                continue
            primary.hide()
            upgrade.hide()
            if not progress.running:
                progress.begin()
                self.program_support_links[card].hide()
            progress.advance(percent)
            progress.show()
            status.setText(message)
            status.show()

    @Slot(bool, str, str)
    def extra_installer_done(self, ok: bool, message: str, app_id: str):
        name = EXTRA_APPS[app_id]["name"]
        self.installing_program = None
        installed = installed_program(app_id)
        if ok:
            self.upgradeable_programs.discard(app_id)
            if not message:
                message = "Pronto para abrir." if installed else (
                    "O instalador terminou. O programa ainda não foi localizado; "
                    "revise a instalação do fabricante.")
        for card, (_, _, progress, status) in self.program_controls.items():
            if program_key(card) == app_id:
                progress.finish(ok)
                progress.hide()
                status.setText(message)
                status.show()
                self.program_support_links[card].setVisible(not ok)
        self.refresh_program_cards()
        self.status_message(f"{name}: {message}")
        try:
            with (DATA_DIR / "instalacoes.log").open("a", encoding="utf-8") as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {name}: {message}\n")
        except OSError:
            pass
    def start_clean(self):
        if self.update_mode == "install":
            return
        if self.cleaner:
            return
        if not any(check.isChecked() for check in
                   (self.clean_user, self.clean_windows, self.clean_recycle, self.clean_icons, self.clean_nvidia)):
            self.clean_output.setPlainText("Selecione ao menos uma opção.")
            return
        selection = []
        unavailable = []
        if self.clean_user.isChecked():
            user_temp = known_temp_folders(False)
            selection.extend(user_temp)
            if not user_temp:
                unavailable.append("Pasta temporária do usuário indisponível.")
        if self.clean_windows.isChecked():
            system_temp = windows_temp_folder()
            if system_temp is None:
                unavailable.append("Pasta temporária do Windows indisponível.")
            else:
                selection.append(system_temp)
        if self.clean_nvidia.isChecked():
            dxcache = nvidia_dxcache_folders()
            selection.extend(dxcache)
            if not dxcache:
                unavailable.append("Cache NVIDIA DXCache não localizado neste perfil.")
        selection = list(dict.fromkeys(selection))
        if unavailable and not selection and not (self.clean_recycle.isChecked() or self.clean_icons.isChecked()):
            self.clean_output.setPlainText("\n".join(unavailable))
            return
        if not confirmar(self, "Confirmar limpeza", "Executar as opções selecionadas?\nArquivos protegidos ou em uso serão preservados."):
            return
        if self.update_mode == "install":
            return
        self.clean_output.clear()
        self.clean_output.appendPlainText("Iniciando limpeza...")
        for message in unavailable:
            self.clean_output.appendPlainText(message)
        self.clean_progress.begin()
        self.clean_start.setEnabled(False)
        self.clean_stop.setEnabled(True)
        self.cleaner = CleanerThread(selection, self.clean_recycle.isChecked(), self.clean_icons.isChecked())
        self.cleaner.progress.connect(self.clean_output.appendPlainText)
        self.cleaner.percent.connect(self.clean_progress.advance)
        self.cleaner.complete.connect(self.clean_finished)
        self.cleaner.failed.connect(self.clean_failed)
        self.cleaner.finished.connect(self.clean_thread_finished)
        self.cleaner.start()
        self.status_message("Limpeza em andamento...")

    def cancel_clean(self):
        if self.cleaner and self.cleaner.isRunning():
            self.cleaner.cancel_flag.set()
            self.clean_output.appendPlainText("Cancelamento solicitado. Finalizando item atual...")

    @Slot(object)
    def clean_finished(self, stats):
        failed = stats.recycle_bin == "falhou" or stats.icon_cache == "falhou"
        self.clean_progress.finish(not (stats.cancelled or failed))
        self.clean_stop.setEnabled(False)
        final = (f"Arquivos removidos: {stats.files} | Pastas vazias: {stats.folders} | "
                 f"Espaço liberado: {format_size(stats.bytes_freed)} | Ignorados: {stats.skipped} | "
                 f"Lixeira: {stats.recycle_bin}"
                 f" | Cache de ícones: {stats.icon_cache}"
                 + (" | Cancelada" if stats.cancelled else " | Concluída com falhas" if failed else ""))
        self.clean_output.appendPlainText("\n" + final)
        self.status_message(final)
        try:
            DATA_DIR.mkdir(exist_ok=True, parents=True)
            with (DATA_DIR / "limpeza.log").open("a", encoding="utf-8") as log:
                log.write(datetime.now().isoformat(timespec="seconds") + " " + final + "\n")
                if stats.recycle_error:
                    log.write(stats.recycle_error + "\n")
        except OSError:
            pass

    @Slot(str)
    def clean_failed(self, message: str):
        self.clean_progress.finish(False)
        self.clean_stop.setEnabled(False)
        self.clean_output.appendPlainText("A limpeza falhou. " + message)
        self.status_message("A limpeza falhou.")

    def clean_thread_finished(self):
        thread = self.cleaner
        self.cleaner = None
        thread.deleteLater()
        self.clean_start.setEnabled(True)

    def check_update(self, manual: bool):
        if self.update_mode:
            if manual:
                self.goto("updates")
            return
        if not (runtime_dir() / "updater.ps1").is_file():
            if manual:
                self.goto("updates")
                self.update_failed("O atualizador ainda não está disponível.")
            return
        self.update_mode = "check"
        self.update_elapsed = 0
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.top_check.setEnabled(False)
        self.update_check.setEnabled(False)
        self.update_note.setText("Consultando a última Release estável...")
        self.update_progress.begin()
        try:
            args = ["-Check", "-CurrentVersion", APP_VERSION, "-StatusFile", str(self.update_status)]
            if installed_mode():
                args.append("-Installed")
            self._spawn_update(args)
        except Exception as e:
            self.update_failed(str(e))
            return
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.poll_update)
        self.update_timer.start(700)
        if manual:
            self.goto("updates")

    def _spawn_update(self, args: list[str]):
        if os.name != "nt":
            raise OSError("O atualizador só funciona no Windows.")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self.updater_process = subprocess.Popen(
            [str(powershell_path()), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(runtime_dir() / "updater.ps1"), *args],
            cwd=str(DATA_DIR), creationflags=flags,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=powershell_env(),
        )

    def poll_update(self):
        if not self.update_mode:
            return
        self.update_elapsed += 1
        process_exit = self.updater_process.poll() if self.updater_process is not None else None
        if self.update_status.is_file():
            try:
                status = self.update_status.read_text(encoding="utf-8-sig").strip()
            except (OSError, UnicodeError):
                status = ""
            if status.startswith("PROGRESS|"):
                parts = status.split("|", 2)
                if len(parts) == 3 and parts[1].isascii() and parts[1].isdecimal() and len(parts[1]) <= 2:
                    self.update_progress.advance(int(parts[1]))
                    self.update_note.setText(parts[2])
            if self.update_mode == "install" and status == "READY" and process_exit is None:
                self.update_timer.stop()
                self.status_message("Atualização verificada. Fechando para instalar...")
                self.update_note.setText("Instalador verificado. Abrindo a instalação…")
                self.update_progress.finish(True)
                QTimer.singleShot(350, self.close_to_update)
                return
            if status == "ERROR":
                self.update_failed("A atualização falhou. Consulte atualizacoes.log.")
                return
            if status == "CURRENT":
                self.stop_update_timer()
                self.update_note.setText("Você está na versão mais recente.")
                self.status_message("Callas Optimizer atualizado.")
                return
            if self.update_mode == "check" and status.startswith("AVAILABLE|v"):
                self.stop_update_timer()
                release = status.split("|", 1)[1]
                self.update_note.setText("Disponível: " + release)
                self.goto("updates")
                if self.isMinimized():
                    self.showNormal()
                self.raise_()
                self.activateWindow()
                question = ("Deseja baixar e atualizar agora?" if installed_mode()
                            else "Deseja abrir a página do instalador oficial?")
                if confirmar(self, "Atualização disponível",
                             f"Nova versão encontrada: {release}\nVersão em uso: {APP_VERSION}\n\n{question}", True):
                    self.install_update()
                return
        if process_exit is not None:
            self.update_failed("Atualizador encerrou sem informar o resultado. Consulte os logs.")
            return
        if self.update_elapsed > 900:
            self.update_failed("Tempo limite da atualização. Confira a conexão e os logs.")

    def close_to_update(self):
        if self.update_mode != "install" or self.update_timer is None:
            return
        if self.close():
            QApplication.quit()
        else:
            self.update_timer.start()

    def stop_update_timer(self, success: bool = True):
        if self.update_timer is not None:
            self.update_timer.stop()
            self.update_timer.deleteLater()
            self.update_timer = None
        try:
            self.update_status.unlink(missing_ok=True)
        except OSError:
            pass
        self.updater_process = None
        self.update_mode = ""
        self.top_check.setEnabled(True)
        self.update_check.setEnabled(True)
        self.update_progress.finish(success)

    def update_failed(self, message: str):
        self.stop_update_timer(False)
        self.update_note.setText(message)
        self.status_message(message)

    def install_update(self):
        if (self.installing_program or (self.cleaner and self.cleaner.isRunning()) or
                (self.extensions_job and self.extensions_job.isRunning()) or
                (self.vm_template_thread and self.vm_template_thread.isRunning()) or
                self.native_timer is not None):
            self.update_note.setText("Conclua a tarefa em andamento antes de instalar a atualização.")
            return
        if self.update_mode:
            return
        if not installed_mode():
            webbrowser.open(PROJECT_URL + "/releases/latest")
            return
        self.update_mode = "install"
        self.update_elapsed = 0
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.top_check.setEnabled(False)
        self.update_check.setEnabled(False)
        self.update_progress.begin()
        self.update_note.setText("Baixando, validando e preparando a nova versão. Mantenha o aplicativo aberto.")
        try:
            args = ["-Install", "-CurrentVersion", APP_VERSION, "-StatusFile", str(self.update_status),
                    "-Target", str(Path(sys.executable).resolve()), "-WaitPid", str(os.getpid())]
            if installed_mode():
                args.append("-Installed")
            self._spawn_update(args)
        except Exception as e:
            self.update_failed(str(e))
            return
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.poll_update)
        self.update_timer.start(700)
        self.goto("updates")

    def load_logs(self):
        result = []
        for name in ("limpeza.log", "instalacoes.log", "atualizacoes.log", "callas_teck.log", "acoes.log"):
            path = DATA_DIR / name
            if not path.is_file():
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-90:]
                result.append("===== " + name + " =====\n" + "\n".join(lines))
            except OSError:
                continue
        self.log_view.setPlainText("\n\n".join(result) if result else "Ainda não há registros.")

    def open_log_folder(self):
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        if os.name == "nt":
            os.startfile(DATA_DIR)
        else:
            QMessageBox.information(self, "Pasta", str(DATA_DIR))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_home_layout()

    def closeEvent(self, event):
        if self.vm_template_thread and self.vm_template_thread.isRunning():
            QMessageBox.information(self, "VMs em preparação",
                                    "Conclua a preparação das máquinas antes de fechar.")
            event.ignore()
            return
        if self.extra_installer and self.extra_installer.isRunning():
            QMessageBox.information(self, "Download em andamento",
                                    "Conclua o download do instalador antes de fechar.")
            event.ignore()
            return
        if self.extensions_job and self.extensions_job.isRunning():
            self.status_message("Aguarde a configuração das extensões do Brave.")
            event.ignore()
            return
        if self.cleaner and self.cleaner.isRunning():
            QMessageBox.information(self, "Limpeza em andamento", "Cancele ou conclua a Limpeza Total antes de fechar o aplicativo.")
            event.ignore()
            return
        if self.native_timer is not None and not confirmar(
                self, "Ferramenta em execução",
                f"{self.native_task_name} continuará em segundo plano. Fechar o Callas agora?"):
            event.ignore()
            return
        self.shutdown_countdown.stop()
        event.accept()


def main():
    if "--callas-task" in sys.argv:
        try:
            index = sys.argv.index("--callas-task")
            report_index = sys.argv.index("--callas-report")
            profile = sys.argv[sys.argv.index("--callas-profile") + 1] if "--callas-profile" in sys.argv else None
            minutes = None
            if "--shutdown-minutes" in sys.argv:
                minutes = int(sys.argv[sys.argv.index("--shutdown-minutes") + 1])
            return run_windows_action(sys.argv[index+1], sys.argv[report_index+1], profile, minutes)
        except (ValueError, IndexError):
            return 2
    if "--self-test" in sys.argv:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        # Exercita runtime Python/Qt empacotado, imports e assets apos instalacao.
        qtapp = QApplication([])
        qtapp.setStyleSheet(STYLE)
        w = MainWindow()
        qtapp.processEvents()
        if "clean" not in w.pages or "programs" not in w.pages:
            raise RuntimeError("Navegacao incompleta")
        w.goto("clean")
        w.goto("programs")
        w.close()
        return 0
    if os.name != "nt":
        # Os testes de layout com QT_QPA_PLATFORM=offscreen tambem podem rodar fora do Windows.
        if os.environ.get("QT_QPA_PLATFORM") != "offscreen":
            raise SystemExit("O Callas Optimizer Windows precisa de Windows 11.")
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True) if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling') else None
    if os.name == "nt":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CallasTeck.CallasOptimizer.Windows")
        except (OSError, AttributeError):
            pass
    app = QApplication(sys.argv)
    app.setWindowIcon(app_icon())
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
