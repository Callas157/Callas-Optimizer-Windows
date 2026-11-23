"""Callas Optima para Windows, com interface PySide6."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import threading
import uuid
import webbrowser

from PySide6.QtCore import QByteArray, QFileInfo, QRectF, QSettings, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QFileDialog, QFileIconProvider, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSplitter, QStackedWidget, QVBoxLayout, QWidget,
)

from cleaner import (
    clean_folders, clear_icon_cache, empty_recycle_bin, format_size, known_temp_folders,
    nvidia_dxcache_folders,
)
from windows_actions import ACTIONS, BY_ROUTE, HOME as ACTION_HOME, worker as run_windows_action
from extra_installers import (
    CATALOG as EXTRA_APPS, available_upgrades, download_and_open, installed_program,
    official_website, open_program, powershell_env, powershell_path, program_key, upgrade_program,
)
from virtualbox_templates import create_test_vms, VM_NAMES, get_vboxmanage

APP_VERSION = "8.9.25"
REPO = "Callas157/Callas-Optimizer-Windows"
PROJECT_URL = f"https://github.com/{REPO}"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CallasTeck"
NATIVE_PROGRAM_ICONS = {"steam", "discord", "epic", "medal", "lghub", "wise", "virtualbox"}

# Um id selecionado corresponde a UMA pagina, com conteudo proprio.
NAV_SECTIONS = [
    ("", [
        ("home", "Início", "⌂"),
        ("programs", "Programas", "▦"),
        ("clean", "Limpeza Total", "♻"),
        ("gamer", "Modo Gamer", "⚡"),
        ("repair", "Reparar Windows", "✚"),
        ("drivers", "Drivers", "▣"),
        ("updates", "Atualizações", "↓"),
        ("logs", "Registros", "≡"),
        ("about", "Sobre", "ⓘ"),
    ]),
    ("FERRAMENTAS DO WINDOWS", [
        ("edge", "Microsoft Edge", "◇"),
        ("windows_update", "Windows Update", "↻"),
        ("network", "Rede e DNS", "◎"),
        ("privacy", "Privacidade", "◉"),
        ("classic", "Menu clássico", "▤"),
        ("shutdown", "Desligamento", "⏻"),
        ("winutil", "WinUtil", "▣"),
        ("restore_point", "Ponto de restauração", "✦"),
        ("restore", "Restaurar padrões", "↩"),
    ]),
]

LEGACY = {
    "gamer": (1, "Modo Gamer", "Ajustes para jogos, Xbox, hibernação e plano de energia.",
              "Confira cada ajuste antes de aplicar. Algumas mudanças exigem reinicialização."),
    "edge": (2, "Microsoft Edge", "Ferramentas de remoção e recuperação do navegador.",
             "Remover o Edge pode afetar componentes do Windows. Faça backup primeiro."),
    "windows_update": (3, "Windows Update", "Configurações do serviço de atualização do Windows.",
                       "Desativar atualizações reduz a segurança do sistema. Prefira as opções reversíveis."),
    "network": (4, "Rede e DNS", "Gerenciamento de DNS, rede e configurações dos adaptadores.",
                "Algumas opções podem desconectar temporariamente a internet."),
    "privacy": (5, "Privacidade", "Controles de telemetria, permissões e privacidade.",
                "Revise cada configuração para não desativar funcionalidades importantes."),
    "repair": (6, "Reparar Windows", "Ferramentas oficiais de diagnóstico e recuperação.",
               "DISM e SFC podem demorar. Não desligue o computador durante reparos."),
    "classic": (8, "Menu clássico", "Alternar o menu de contexto clássico do Windows 11.",
                "A alteração pode exigir reinício do Explorer para ficar visível."),
    "shutdown": (9, "Desligamento", "Agendar e cancelar desligamentos automáticos.",
                 "Confira os horários para evitar fechar aplicativos ou perder trabalho."),
    "winutil": (10, "WinUtil", "Abrir a ferramenta WinUtil de Chris Titus Tech.",
                "Ferramenta de terceiros: revise seus comandos antes de executá-los."),
    "restore_point": (12, "Ponto de restauração", "Criar um ponto de restauração do Windows.",
                      "O Windows precisa ter a proteção do sistema habilitada."),
    "restore": (13, "Restaurar padrões", "Reverter modificações efetuadas pelo Callas Optimizer.",
                "Só configurações contempladas no motor original podem ser revertidas."),
}

STYLE = """
* { font-family: 'Segoe UI'; font-size: 13px; color: #e8ecff; }
QMainWindow, QWidget#MainRoot { background: #07091e; }
QFrame#Sidebar { background: qlineargradient(x1:0,y1:0,x2:0.45,y2:1,stop:0 #101226,stop:.73 #0d1023,stop:1 #191347); border-right: 1px solid #363468; }
QFrame#Topbar { background: #0a0e24; border-bottom: 1px solid #282449; }
QFrame#Card { background: #111b37; border: 1px solid #403a71; border-radius: 15px; }
QFrame#DashboardPanel { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #15173b,stop:1 #0c1e3f); border: 1px solid #595197; border-radius: 15px; }
QLabel#Metric { font-size: 19px; font-weight: 700; color: #f2f9ff; }
QFrame#QuickCard { background: qlineargradient(x1:0,y1:0,x2:.7,y2:1,stop:0 #28134e,stop:.64 #121332,stop:1 #321469); border: 1px solid #a466f1; border-radius: 16px; }
QFrame#QuickCard[accent="cyan"] { background: qlineargradient(x1:0,y1:0,x2:.7,y2:1,stop:0 #0c2d56,stop:.64 #0e1837,stop:1 #0b3a70); border-color: #4c9bea; }
QFrame#Hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #171b3b,stop:.5 #0a1028,stop:.77 #171044,stop:1 #0b2148); border: 1px solid #6255ba; border-radius: 18px; }
QLabel#Header { font-size: 31px; font-weight: 700; color: #f8f7ff; }
QLabel#Title { font-size: 27px; font-weight: 700; color: #f9f8ff; }
QLabel#HeroTitle { font-size: 26px; font-weight: 700; color: #fff; }
QLabel#SystemMetric { color: #e6efff; font-size: 14px; font-weight: 600; }
QLabel#CardTitle { font-size: 17px; font-weight: 700; color: #f8f8ff; }
QLabel#Muted { color: #a8b9d8; }
QLabel#Section { color: #bc91ff; font-weight: 700; font-size: 11px; letter-spacing: 1px; }
QPushButton { background: #22234e; color: #f2f3ff; border: 1px solid #635e9b; border-radius: 11px; padding: 10px 13px; font-weight: 600; }
QPushButton:hover { background: #38347c; border-color: #b87aff; }
QPushButton:disabled { color: #7880a6; background: #1b2241; border-color: #3a3b61; }
QPushButton#Primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #a02bdf,stop:.55 #523cec,stop:1 #087bff); border: 1px solid #9e6dff; color: #fff; }
QPushButton#Primary:hover { background: #8753ee; border-color: #52e3ff; }
QPushButton#Quick { text-align: left; background: transparent; border: none; padding: 4px 0; color: #ffffff; font-size: 21px; font-weight: 700; }
QPushButton#Quick:hover { background: #3a2877; }
QPushButton#Nav { background: transparent; border: none; border-radius: 9px; padding: 9px 12px; text-align: left; color: #d0d7f6; font-size: 13px; }
QPushButton#Nav:hover { background: #342563; color: white; }
QPushButton#Nav:checked { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6829a6,stop:1 #235ec5); border: 1px solid #bb73ff; color: white; }
QScrollArea { border: none; background: transparent; }
QWidget#PageContent { background: #07091e; }
QWidget#NavContent { background: #101226; }
QScrollBar:vertical { background: #10142d; width: 9px; }
QScrollBar::handle:vertical { background: #6154a0; border-radius: 4px; min-height: 35px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QSplitter::handle { background: #3f295d; width: 3px; }
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
            operation(self.app_id, self.progress.emit)
            self.result.emit(True, "", self.app_id)
        except OSError as exc:
            message = "A instalação foi cancelada." if getattr(exc, "winerror", None) == 1223 else str(exc)
            self.result.emit(False, message, self.app_id)
        except Exception as exc:
            self.result.emit(False, str(exc), self.app_id)


class VirtualBoxTemplateThread(QThread):
    progress = Signal(str)
    result = Signal(bool, str)

    def __init__(self, folder: Path):
        super().__init__()
        self.folder = folder

    def run(self):
        try:
            message = create_test_vms(self.folder, self.progress.emit)
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
    complete = Signal(object)

    def __init__(self, roots: list[Path], recycle: bool, icons: bool):
        super().__init__()
        self.roots = roots
        self.recycle = recycle
        self.icons = icons
        self.cancel_flag = threading.Event()

    def run(self):
        stats = clean_folders(self.roots, self.cancel_flag, self.progress.emit)
        if self.recycle:
            if self.cancel_flag.is_set():
                stats.recycle_bin = "etapa cancelada"
                stats.cancelled = True
            else:
                try:
                    stats.recycle_bin = empty_recycle_bin()
                    self.progress.emit(f"Lixeira: {stats.recycle_bin}.")
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
                except OSError as exc:
                    stats.icon_cache = "falhou"
                    self.progress.emit(f"Cache de ícones: {exc}")
        self.complete.emit(stats)


NAV_ICONS = {
    "home": "⌂", "gamer": "⚡", "edge": "◇", "windows_update": "↻",
    "network": "◎", "privacy": "◈", "repair": "✚", "clean": "♻",
    "classic": "▤", "shutdown": "⏻", "winutil": "▣",
    "updates": "↓", "restore_point": "✦", "restore": "↩",
    "programs": "▦", "drivers": "▣", "logs": "≡", "about": "ⓘ",
}


def menu_icon(route: str, color: str = "#c7cefb") -> QIcon:
    """Ícones vetoriais monocromáticos com traçado consistente."""
    # Ícones com fundo próprio, independentes das fontes de emojis do Windows.
    paths = {
        "home": '<path d="M3 11 12 3l9 8v10h-7v-7h-4v7H3z"/>',
        "gamer": '<path d="M5 12h14l2 7-5-2-2-2h-4l-2 2-5 2z"/><path d="M8 12V9m-2 1h4m7 0h.01"/>',
        "edge": '<circle cx="12" cy="12" r="9"/><path d="M5 16c3-7 12-7 14-2M8 19l4-5"/>',
        "windows_update": '<path d="M20 11a8 8 0 0 0-14-5L4 8m0-5v5h5M4 13a8 8 0 0 0 14 5l2-2m0 5v-5h-5"/>',
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


def card_layout(variant: str = "Card") -> tuple[QFrame, QVBoxLayout]:
    outer = QFrame()
    outer.setObjectName(variant)
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(22, 22, 22, 22)
    layout.setSpacing(12)
    return outer, layout


def action_button(text: str, function, primary: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setObjectName("Primary")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.clicked.connect(function)
    return button


class MemoryRing(QWidget):
    def __init__(self):
        super().__init__()
        self.percent = None
        self.setFixedSize(146, 146)
        self.setAccessibleName("Uso de memória RAM")

    def set_percent(self, percent):
        self.percent = percent
        self.setAccessibleDescription("Indisponível" if percent is None else f"{percent}%")
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
            painter.drawText(QRectF(0, 36, 146, 48), Qt.AlignmentFlag.AlignCenter, value)
            font.setBold(False)
            font.setPixelSize(13)
            painter.setFont(font)
            painter.drawText(QRectF(0, 83, 146, 23), Qt.AlignmentFlag.AlignCenter, "RAM em uso")


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
        self.extra_installer: ExtraInstallerThread | None = None
        self.vm_template_thread: VirtualBoxTemplateThread | None = None
        self.checking_program_updates = False
        self.program_updates_checked = False
        self.program_updates_result.connect(self.program_updates_done)
        self.extensions_job: BraveExtensionsThread | None = None
        self.installing_program: str | None = None
        self.program_controls = {}
        self.program_icons: dict[str, QLabel] = {}
        self.program_icon_sources: dict[str, Path | None] = {}
        self.program_icon_provider = QFileIconProvider()
        self.upgradeable_programs: set[str] = set()
        self.updater_process: subprocess.Popen | None = None
        self.update_mode = ""
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.update_elapsed = 0
        self.nav_buttons: dict[str, QPushButton] = {}
        self.pages: dict[str, QWidget] = {}

        root = QWidget()
        root.setObjectName("MainRoot")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(self.splitter)
        self._sidebar()
        self._main_area()
        self.splitter.setSizes([220, 1230])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.goto("home")

        try:
            runtime_files()
        except Exception as e:
            QMessageBox.warning(self, "Recursos indisponíveis", str(e))
            self.status_message("Alguns recursos não puderam ser preparados.")

        if self.settings.value("auto_update", True, type=bool):
            QTimer.singleShot(1800, lambda: self.check_update(False))

    def _sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(205)
        sidebar.setMaximumWidth(365)
        shell = QVBoxLayout(sidebar)
        shell.setContentsMargins(15, 19, 12, 14)
        shell.setSpacing(14)
        brand = QVBoxLayout()
        brand.setSpacing(8)
        logo = QLabel()
        logo.setPixmap(svg_icon("callas", 96).pixmap(79, 79))
        brand.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        name = label('Callas <span style="color:#c874ff">Optima</span>', "CardTitle")
        brand.addWidget(name, alignment=Qt.AlignmentFlag.AlignHCenter)
        shell.addLayout(brand)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("NavContent")
        nav = QVBoxLayout(content)
        nav.setContentsMargins(0, 0, 0, 0)
        nav.setSpacing(2)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        for section, entries in NAV_SECTIONS:
            if section:
                heading = label(section, "Section")
                heading.setContentsMargins(8, 12, 0, 4)
                nav.addWidget(heading)
            for route, title, glyph in entries:
                btn = action_button(title, lambda _=False, key=route: self.goto(key))
                btn.setIcon(menu_icon(route))
                btn.setIconSize(QSize(23, 23))
                btn.setMinimumHeight(35)
                btn.setObjectName("Nav")
                btn.setCheckable(True)
                self.nav_group.addButton(btn)
                self.nav_buttons[route] = btn
                nav.addWidget(btn)
        nav.addStretch()
        scroll.setWidget(content)
        shell.addWidget(scroll, 1)
        shell.addWidget(label("v" + APP_VERSION + "   •   Windows x64", "Muted"))
        self.splitter.addWidget(sidebar)

    def _main_area(self):
        central = QWidget()
        col = QVBoxLayout(central)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        bar = QFrame()
        bar.setObjectName("Topbar")
        bh = QHBoxLayout(bar)
        bh.setContentsMargins(25, 15, 24, 15)
        logo = QLabel()
        logo.setPixmap(svg_icon("callas", 70).pixmap(60, 60))
        bh.addWidget(logo)
        bh.addSpacing(6)
        titles = QVBoxLayout()
        titles.setSpacing(3)
        titles.addWidget(label('Callas <span style="color:#7ca7ff">Optima</span>', "Header"))
        titles.addWidget(label("Desempenho e renovação"))
        bh.addLayout(titles, 1)
        self.top_check = action_button("VERIFICAR ATUALIZAÇÃO", lambda: self.check_update(True))
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
        self.splitter.addWidget(central)

    def _page(self, route: str, title: str, description: str) -> QVBoxLayout:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("PageContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(15)
        if route != "home":
            layout.addWidget(label(title, "Title"))
            layout.addWidget(label(description, "Muted"))
        scroll.setWidget(content)
        self.pages[route] = scroll
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
        for route, (op, title, description, warning) in LEGACY.items():
            self._legacy_page(route, op, title, description, warning)

    def _home_page(self):
        """Painel Fênix interativo; todos os atalhos usam páginas da mesma janela."""
        col = self._page("home", "Callas Optima", "")
        hero, hero_box = card_layout("Hero")
        hero_box.setContentsMargins(23, 12, 18, 12)
        row = QHBoxLayout()
        row.setSpacing(22)

        self.memory_ring = MemoryRing()
        row.addWidget(self.memory_ring, alignment=Qt.AlignmentFlag.AlignVCenter)
        text_col = QVBoxLayout()
        text_col.setSpacing(8)
        text_col.addStretch()
        text_col.addWidget(label("Visão geral do sistema", "HeroTitle"))
        text_col.addWidget(label("Uso atual dos recursos do Windows."))
        self.live_cpu = label("CPU  —", "SystemMetric")
        self.live_memory = label("RAM  —", "SystemMetric")
        self.live_storage = label("Disco  —", "SystemMetric")
        stats = QHBoxLayout()
        stats.setSpacing(16)
        for metric in (self.live_cpu, self.live_memory, self.live_storage):
            stats.addWidget(metric)
        text_col.addLayout(stats)
        text_col.addStretch()
        row.addLayout(text_col, 2)

        art_box = QVBoxLayout()
        art_box.setSpacing(0)
        self.hero_phoenix = QLabel()
        self.hero_phoenix.setPixmap(phoenix_art().scaled(
            275, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.hero_phoenix.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_phoenix.setAccessibleName("Fênix Callas Optima")
        art_box.addWidget(self.hero_phoenix)
        art_box.addWidget(action_button("Explorar otimização", lambda: self.goto("gamer"), True))
        row.addLayout(art_box, 1)
        hero_box.addLayout(row)
        col.addWidget(hero)

        self._cpu_snapshot = None
        self.home_timer = QTimer(self)
        self.home_timer.setInterval(2500)
        self.home_timer.timeout.connect(self.refresh_system_metrics)
        self.refresh_system_metrics()

        self.home_quick_grid = QGridLayout()
        self.home_quick_grid.setSpacing(12)
        self.home_tiles = []
        shortcuts = [
            ("Clean", "Limpeza segura de arquivos temporários", "clean"),
            ("Boost", "Opções de desempenho e jogos", "gamer"),
            ("Repair", "Diagnóstico e reparo do Windows", "repair"),
            ("Apps", "Instalar programas oficiais", "programs"),
            ("Drivers", "NVIDIA App e Windows Update", "drivers"),
            ("Atualizar", "Verificar versões do Callas Optima", "updates"),
        ]
        for index, (title, description, route) in enumerate(shortcuts):
            tile, tile_box = card_layout("QuickCard")
            cyan = index % 2 == 1
            tile.setProperty("accent", "cyan" if cyan else "violet")
            tile_box.setContentsMargins(16, 12, 16, 12)
            tile_box.setSpacing(3)
            icon = QLabel()
            icon_route = {"gamer": "boost", "updates": "windows_update"}.get(route, route)
            icon.setPixmap(menu_icon(icon_route, "#37deff" if cyan else "#e6aaff").pixmap(34, 34))
            tile_box.addWidget(icon)
            button = action_button(
                title + "  ›", lambda _=False, destination=route: self.goto(destination)
            )
            button.setObjectName("Quick")
            tile_box.addWidget(button)
            tile_box.addWidget(label(description, "Muted"))
            tile_box.addStretch()
            self.home_tiles.append(tile)
        col.addLayout(self.home_quick_grid)

        self.home_detail_grid = QGridLayout()
        self.home_detail_grid.setSpacing(12)
        self.home_panels = []

        health, health_box = card_layout("DashboardPanel")
        health_box.addWidget(label("Saúde do sistema", "CardTitle"))
        health_box.addWidget(label(
            "Verifique arquivos do Windows e componentes do sistema usando "
            "as ferramentas oficiais de diagnóstico.", "Muted"
        ))
        health_box.addWidget(label(
            "A integridade só é confirmada depois que o diagnóstico é executado."
        ))
        health_box.addWidget(action_button(
            "ABRIR DIAGNÓSTICOS", lambda: self.goto("repair"), True
        ))
        health_box.addStretch()
        self.home_panels.append(health)

        startup, startup_box = card_layout("DashboardPanel")
        startup_box.addWidget(label("Programas de inicialização", "CardTitle"))
        startup_box.addWidget(label(
            "Gerencie os aplicativos que iniciam com o Windows na tela oficial "
            "de Configurações.", "Muted"
        ))
        startup_box.addWidget(action_button(
            "GERENCIAR INICIALIZAÇÃO",
            lambda: self.open_windows_settings("startupapps")
        ))
        self.home_panels.append(startup)

        storage, storage_box = card_layout("DashboardPanel")
        storage_box.addWidget(label("Armazenamento do sistema", "CardTitle"))
        try:
            drive = Path(os.environ.get("SystemDrive", "C:") + "\\") if os.name == "nt" else Path.home()
            usage = shutil.disk_usage(drive)
            free_gib = usage.free / (1024 ** 3)
            total_gib = usage.total / (1024 ** 3)
            storage_box.addWidget(label(
                f"{free_gib:.1f} GB livres de {total_gib:.1f} GB", "Metric"
            ))
            occupied = int(100 * (usage.total - usage.free) / usage.total)
            bar = QProgressBar()
            bar.setValue(occupied)
            storage_box.addWidget(bar)
        except (OSError, ZeroDivisionError):
            storage_box.addWidget(label("Armazenamento indisponível nesta sessão."))
        storage_box.addWidget(action_button(
            "ABRIR LIMPEZA", lambda: self.goto("clean")
        ))
        self.home_panels.append(storage)

        gaming, gaming_box = card_layout("DashboardPanel")
        gaming_box.addWidget(label("Modo Jogo", "CardTitle"))
        gaming_box.addWidget(label(
            "Acesse ajustes de energia, jogos e serviços. "
            "Nenhuma mudança é aplicada sem sua confirmação.", "Muted"
        ))
        gaming_box.addWidget(action_button(
            "AJUSTES PARA JOGOS", lambda: self.goto("gamer"), True
        ))
        self.home_panels.append(gaming)

        tools, tools_box = card_layout("DashboardPanel")
        tools_box.addWidget(label("Ferramentas rápidas", "CardTitle"))
        quick_tools = QGridLayout()
        for position, (title, route) in enumerate((
            ("Rede e DNS", "network"),
            ("Privacidade", "privacy"),
            ("Restauração", "restore_point"),
            ("Drivers", "drivers"),
        )):
            button = action_button(
                title, lambda _=False, destination=route: self.goto(destination)
            )
            quick_tools.addWidget(button, position // 2, position % 2)
        tools_box.addLayout(quick_tools)
        self.home_panels.append(tools)

        col.addLayout(self.home_detail_grid)
        col.addStretch()
        self._refresh_home_layout(force=True)

    def refresh_system_metrics(self):
        if os.name != "nt":
            return
        kernel = ctypes.windll.kernel32
        memory = WindowsMemoryStatus()
        memory.length = ctypes.sizeof(memory)
        if kernel.GlobalMemoryStatusEx(ctypes.byref(memory)):
            self.memory_ring.set_percent(memory.load)
            total = memory.total / 1024 ** 3
            used = (memory.total - memory.available) / 1024 ** 3
            self.live_memory.setText(f"RAM\n{used:.1f} / {total:.1f} GB")
        idle, system, user = (ctypes.c_ulonglong() for _ in range(3))
        if kernel.GetSystemTimes(ctypes.byref(idle), ctypes.byref(system), ctypes.byref(user)):
            current = idle.value, system.value + user.value
            if self._cpu_snapshot:
                idle_delta = current[0] - self._cpu_snapshot[0]
                total_delta = current[1] - self._cpu_snapshot[1]
                if total_delta > 0:
                    usage = max(0, min(100, round(100 * (1 - idle_delta / total_delta))))
                    self.live_cpu.setText(f"CPU\n{usage}%")
            self._cpu_snapshot = current
        try:
            drive = os.environ.get("SystemDrive", "C:")
            space = shutil.disk_usage(drive + "\\")
            self.live_storage.setText(f"Disco ({drive})\n{space.free / 1024 ** 3:.0f} GB livres")
        except OSError:
            pass

    def _refresh_home_layout(self, force: bool = False):
        """Mantém os cartões legíveis em janelas pequenas e monitores maiores."""
        if not hasattr(self, "home_quick_grid"):
            return
        width = self.width()
        profile = "compact" if width < 1120 else ("wide" if width >= 1390 else "medium")
        if not force and getattr(self, "_home_profile", None) == profile:
            return
        self._home_profile = profile
        for grid in (self.home_quick_grid, self.home_detail_grid):
            while grid.count():
                grid.takeAt(0)
        self.hero_phoenix.setVisible(profile != "compact")
        quick_columns = {"compact": 2, "medium": 3, "wide": 6}[profile]
        detail_columns = {"compact": 1, "medium": 2, "wide": 3}[profile]
        for column in range(6):
            self.home_quick_grid.setColumnStretch(column, int(column < quick_columns))
            if column < 3:
                self.home_detail_grid.setColumnStretch(column, int(column < detail_columns))
        for index, tile in enumerate(self.home_tiles):
            self.home_quick_grid.addWidget(
                tile, index // quick_columns, index % quick_columns
            )
        if profile == "compact":
            for index, panel in enumerate(self.home_panels):
                self.home_detail_grid.addWidget(panel, index, 0)
        elif profile == "medium":
            for index, panel in enumerate(self.home_panels):
                self.home_detail_grid.addWidget(panel, index // 2, index % 2)
        else:
            health, startup, storage, gaming, tools = self.home_panels
            self.home_detail_grid.addWidget(health, 0, 0, 2, 1)
            self.home_detail_grid.addWidget(startup, 0, 1)
            self.home_detail_grid.addWidget(gaming, 0, 2)
            self.home_detail_grid.addWidget(storage, 1, 1)
            self.home_detail_grid.addWidget(tools, 1, 2)

    def open_windows_settings(self, page: str):
        """Abre somente páginas aprovadas do Windows; não altera configurações."""
        if page not in ("startupapps", "gaming-gamemode"):
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
        col = self._page(
            "drivers", "Drivers", "Acesso às ferramentas oficiais. Nenhum driver é trocado automaticamente.")
        c, body = card_layout()
        body.addWidget(label("NVIDIA APP", "Section"))
        body.addWidget(label(
            "Abra o instalador oficial do NVIDIA App. Nele, você pode verificar "
            "drivers disponíveis e escolher quando instalar; o Callas não remove "
            "drivers nem força versões sem sua confirmação."))
        body.addWidget(action_button("ABRIR NVIDIA APP EM PROGRAMAS", self._show_nvidia_card, True))
        col.addWidget(c)
        other, layout = card_layout()
        layout.addWidget(label("DRIVERS PELO WINDOWS", "Section"))
        layout.addWidget(label("Use as opções oficiais de Windows Update para drivers opcionais. "
                               "Evite instaladores de terceiros que prometem atualizar tudo."))
        layout.addWidget(action_button("ABRIR WINDOWS UPDATE", lambda: self.goto("windows_update")))
        col.addWidget(other)
        col.addStretch()

    def _show_nvidia_card(self):
        self.goto("programs")
        self.pages["programs"].ensureWidgetVisible(self.nvidia_card)

    def _legacy_page(self, route, option, title, description, warning):
        col = self._page(route, title, description)
        header, panel = card_layout()
        panel.addWidget(label("AÇÕES EM PYTHON", "Section"))
        panel.addWidget(label("Cada função roda no Windows com confirmação e registro de resultado."))
        col.addWidget(header)
        for action in BY_ROUTE.get(route, []):
            card, contents = card_layout()
            contents.addWidget(label(action["name"], "CardTitle"))
            contents.addWidget(label(action["description"]))
            if action["warning"]:
                contents.addWidget(label("Atenção: " + action["warning"]))
            text = "EXECUTAR (ADMINISTRADOR)" if action["admin"] else "EXECUTAR"
            contents.addWidget(action_button(text,
                lambda _=False, code=action["id"]: self.native_action(code), True))
            col.addWidget(card)
        col.addWidget(action_button("VER REGISTROS", lambda: self.goto("logs")))
        col.addStretch()

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
        self.clean_progress = QProgressBar()
        self.clean_progress.setRange(0, 100)
        self.clean_progress.setValue(0)
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
        size = QSize(55, 55)
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
        outer, content = card_layout()
        title_row = QHBoxLayout()
        img = QLabel()
        img.setFixedSize(57, 57)
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.program_icons[icon] = img
        self.set_program_icon(icon)
        title_row.addWidget(img)
        names = QVBoxLayout()
        names.addWidget(label(name, "CardTitle"))
        names.addWidget(label(description))
        title_row.addLayout(names, 1)
        content.addLayout(title_row)
        primary = action_button(action_title, action, True)
        if program_key(icon) not in EXTRA_APPS:
            content.addWidget(primary)
            return outer
        actions = QHBoxLayout()
        actions.addWidget(primary, 1)
        upgrade = action_button("Atualizar", lambda: self.install_extra(icon, upgrade=True))
        upgrade.hide()
        actions.addWidget(upgrade)
        content.addLayout(actions)
        progress = QProgressBar()
        progress.setAccessibleName(f"Progresso de {name}")
        progress.hide()
        content.addWidget(progress)
        status = label("")
        status.setTextFormat(Qt.TextFormat.PlainText)
        status.hide()
        content.addWidget(status)
        self.program_controls[icon] = primary, upgrade, progress, status
        return outer

    def _program_page(self):
        col = self._page("programs", "Central de aplicativos", "Instale, abra e atualize seus aplicativos.")
        col.addWidget(action_button("VERIFICAR ATUALIZAÇÕES DOS APPS", self.check_program_updates),
                      alignment=Qt.AlignmentFlag.AlignLeft)
        self.program_grid = QGridLayout()
        self.program_grid.setSpacing(16)
        self.brave_card = self._program_card(
            "Brave Browser", "brave", "Navegador com configuração opcional de SteamDB e Bonjourr", "Instalar",
            lambda: self.install_extra("brave"))
        self.nvidia_card = self._program_card(
            "NVIDIA App", "nvidia", "Gerencie drivers e configurações da GPU", "Instalar",
            lambda: self.install_extra("nvidia"))
        self.medal_card = self._program_card(
            "Medal", "medal", "Gravação de clipes e melhores momentos", "BAIXAR INSTALADOR",
            lambda: self.install_extra("medal"))
        self.lghub_card = self._program_card(
            "Logitech G HUB", "lghub", "Configuração de periféricos Logitech G", "BAIXAR INSTALADOR",
            lambda: self.install_extra("lghub"))
        self.spotify_card = self._program_card(
            "Spotify", "spotify", "Aplicativo de música para Windows", "BAIXAR INSTALADOR",
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
            "Discord", "discord", "Conversas, comunidades e voz", "BAIXAR INSTALADOR",
            lambda: self.install_extra("discord"))
        self.steam_card = self._program_card(
            "Steam", "steam", "Biblioteca de jogos para PC", "BAIXAR INSTALADOR",
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
        for index, card in enumerate(self.all_program_cards):
            self.program_grid.addWidget(card, index // 2, index % 2)
        col.addLayout(self.program_grid)
        lab_card, lab = card_layout()
        lab.addWidget(label("LABORATÓRIO VIRTUALBOX · WINDOWS 11", "Section"))
        lab.addWidget(label(
            "Prepare duas máquinas independentes para testar o Callas: "
            "Windows 11 Pro e Windows 11 IoT Enterprise LTSC. "
            "Cada VM terá 6 GB de RAM, 5 vCPUs, disco dinâmico de 80 GB, "
            "UEFI, Secure Boot, TPM 2.0 e rede NAT. "
            "Os links podem ser copiados do PC para a VM após instalar Guest Additions. "
            "Arrastar arquivos permanece desativado. "
            "Você escolhe a pasta e adiciona as ISOs posteriormente."
        ))
        self.vm_template_button = action_button(
            "PREPARAR / AJUSTAR 2 VMS", self.prepare_virtualbox_templates, True)
        lab.addWidget(self.vm_template_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.vm_template_progress = QProgressBar()
        self.vm_template_progress.setRange(0, 0)
        self.vm_template_progress.hide()
        lab.addWidget(self.vm_template_progress)
        self.vm_template_status = label("")
        self.vm_template_status.setTextFormat(Qt.TextFormat.PlainText)
        self.vm_template_status.hide()
        lab.addWidget(self.vm_template_status)
        col.addWidget(lab_card)
        self.program_updates_status = label("")
        self.program_updates_status.hide()
        col.addWidget(self.program_updates_status)
        openai_card, openai_box = card_layout()
        openai_box.addWidget(label("CHATGPT + CODEX NO WINDOWS", "Section"))
        openai_box.addWidget(label(
            "O ChatGPT para desktop já inclui o Codex. É um único aplicativo oficial, "
            "sem precisar instalar dois programas. Entre com sua conta e, no Codex, "
            "selecione a pasta do projeto que deseja analisar. O Callas não concede "
            "acesso automático aos arquivos nem solicita chaves de API."
        ))
        openai_box.addWidget(action_button(
            "COMO USAR COM ARQUIVOS LOCAIS",
            lambda: webbrowser.open("https://learn.chatgpt.com/pt-BR/docs/quickstart")
        ))
        col.addWidget(openai_card)
        c, box = card_layout()
        box.addWidget(label("EXTENSÕES DO BRAVE", "Section"))
        box.addWidget(label("SteamDB e Bonjourr podem ser configurados por política local. Isso faz o Brave exibir 'Gerenciado pela organização'."))
        row = QHBoxLayout()
        row.addWidget(action_button("CONFIGURAR EXTENSÕES", lambda: self.configure_brave_extensions(False), True))
        row.addWidget(action_button("DESFAZER POLÍTICAS", lambda: self.configure_brave_extensions(True)))
        box.addLayout(row)
        self.extensions_status = label("")
        self.extensions_status.setTextFormat(Qt.TextFormat.PlainText)
        box.addWidget(self.extensions_status)
        col.addWidget(c)
        col.addStretch()
        self.refresh_program_cards()

    def _update_page(self):
        col = self._page("updates", "Atualizações", "Verificação automática pelo GitHub Releases, sempre com sua autorização.")
        c, inner = card_layout()
        inner.addWidget(label("CANAL ESTÁVEL", "Section"))
        inner.addWidget(label("Versão atual: " + APP_VERSION, "CardTitle"))
        inner.addWidget(label("Instalado em Program Files" if installed_mode() else "Edição portátil — instalador em Sobre"))
        self.update_note = label("Pronto para consultar as Releases oficiais.")
        inner.addWidget(self.update_note)
        self.update_progress = QProgressBar()
        self.update_progress.setRange(0, 100)
        self.update_progress.setValue(0)
        inner.addWidget(self.update_progress)
        row = QHBoxLayout()
        row.addWidget(action_button("VERIFICAR AGORA", lambda: self.check_update(True), True))
        row.addWidget(action_button("VER RELEASES", lambda: webbrowser.open(PROJECT_URL + "/releases")))
        inner.addLayout(row)
        col.addWidget(c)
        options, controls = card_layout()
        controls.addWidget(label("PREFERÊNCIAS", "Section"))
        auto = QCheckBox("Verificar novas versões ao abrir o aplicativo")
        auto.setChecked(self.settings.value("auto_update", True, type=bool))
        auto.toggled.connect(lambda flag: self.settings.setValue("auto_update", flag))
        controls.addWidget(auto)
        controls.addWidget(label("Só instala após confirmar e verificar SHA-256. Program Files usa Setup oficial com UAC; edição portátil mantém backup."))
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
        col = self._page("about", "Sobre o Callas Optimizer", "Aplicativo independente para Windows 11, mantido em repositório próprio.")
        about, l = card_layout()
        l.addWidget(label("CALLAS OPTIMIZER  /  WINDOWS EDITION", "CardTitle"))
        l.addWidget(label(f"Versão {APP_VERSION} · Python + PySide6 / Qt · Windows x64"))
        l.addWidget(label("Janela com maximização e redimensionamento; telas específicas; ícones oficiais de identificação; atualizações com confirmação."))
        l.addWidget(label("Todas as ferramentas de manutenção utilizam um executor Python e comandos oficiais do Windows, com UAC quando necessário."))
        l.addWidget(label("Modo de uso: " + ("Instalado em Program Files" if installed_mode() else "Portátil")))
        if not installed_mode():
            l.addWidget(label("Para instalar, criar atalhos e aparecer em Aplicativos Instalados, utilize o Setup oficial."))
            l.addWidget(action_button("BAIXAR SETUP OFICIAL", lambda: webbrowser.open(PROJECT_URL + "/releases/latest"), True))
        l.addWidget(action_button("ABRIR REPOSITÓRIO", lambda: webbrowser.open(PROJECT_URL), True))
        col.addWidget(about)
        col.addStretch()

    def goto(self, route: str):
        if route not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[route])
        self.nav_buttons[route].setChecked(True)
        if route == "logs":
            self.load_logs()
        self.status_message("Seção aberta: " + self.nav_buttons[route].text().strip())
        if route == "home":
            self.refresh_system_metrics()
            self.home_timer.start()
        else:
            self.home_timer.stop()
        if route == "programs":
            self.refresh_program_cards()
            if not self.program_updates_checked:
                self.check_program_updates(automatic=True)

    def status_message(self, message: str):
        self.status_label.setText(message)

    def native_action(self, code: str):
        if self.update_mode == "install":
            return
        task = ACTIONS.get(code)
        if task is None or getattr(self, "native_timer", None) is not None:
            return
        message = task["name"] + "\n\n" + task["description"]
        if task["warning"]:
            message += "\n\nATENÇÃO: " + task["warning"]
        if task["admin"]:
            message += "\n\nO Windows solicitará permissão de administrador."
        if not confirmar(self, "Confirmação da operação", message):
            return
        if os.name != "nt":
            QMessageBox.warning(self, "Indisponível", "Esta opção exige Windows.")
            return
        ACTION_HOME.mkdir(parents=True, exist_ok=True)
        self.native_report = ACTION_HOME / ("acao-" + uuid.uuid4().hex + ".json")
        self.native_report.unlink(missing_ok=True)
        self.native_task_name = task["name"]
        self.native_ticks = 0
        script_args = [] if getattr(sys, "frozen", False) else [str(Path(__file__).resolve())]
        args = [*script_args, "--callas-task", code, "--callas-report", self.native_report.name]
        try:
            if task["admin"]:
                rc = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, subprocess.list2cmdline(args), None, 1)
                if int(rc) <= 32:
                    raise RuntimeError("Permissão UAC não concedida.")
            else:
                subprocess.Popen(
                    [sys.executable, *args],
                    cwd=str(ACTION_HOME),
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception as exc:
            QMessageBox.critical(self, "Falha", str(exc))
            return
        self.status_message("Executando: " + self.native_task_name)
        self.native_timer = QTimer(self)
        self.native_timer.timeout.connect(self.poll_native_action)
        self.native_timer.start(800)

    def poll_native_action(self):
        self.native_ticks += 1
        if self.native_report.is_file():
            try:
                import json
                outcome = json.loads(self.native_report.read_text(encoding="utf-8"))
                self.native_report.unlink(missing_ok=True)
            except (OSError, ValueError):
                return
            self.native_timer.stop()
            self.native_timer.deleteLater()
            self.native_timer = None
            self.status_message(("Concluído: " if outcome["ok"] else "Falhou: ") + self.native_task_name)
            if outcome["ok"]:
                QMessageBox.information(self, "Operação concluída", outcome["message"] or "Concluído.")
            else:
                QMessageBox.warning(self, "Operação não concluída", outcome["message"])
            return
        if self.native_ticks > 2250:
            self.native_timer.stop()
            self.native_timer.deleteLater()
            self.native_timer = None
            QMessageBox.warning(self, "Tempo limite", "A tarefa excedeu o tempo previsto. Consulte os registros.")

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
        self.extensions_status.setText("Aplicando alteração…")
        self.extensions_job = BraveExtensionsThread(undo)
        self.extensions_job.result.connect(self.brave_extensions_done)
        self.extensions_job.start()

    def brave_extensions_done(self, ok: bool, message: str):
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
            upgrade.setVisible(installed[key] is not None and key in self.upgradeable_programs
                               and self.installing_program != key)
            upgrade.setEnabled(not self.installing_program)

    def check_program_updates(self, automatic=False):
        if self.checking_program_updates or self.installing_program:
            return
        self.checking_program_updates = True
        self.program_updates_checked = True
        if not automatic:
            self.program_updates_status.setText("Verificando atualizações pelo WinGet…")
            self.program_updates_status.show()

        def check():
            upgrades = available_upgrades()
            try:
                self.program_updates_result.emit(upgrades, automatic)
            except RuntimeError:
                pass  # A janela pode ter sido fechada durante a consulta.

        threading.Thread(target=check, daemon=True).start()

    def program_updates_done(self, upgrades, automatic: bool):
        self.checking_program_updates = False
        self.upgradeable_programs = upgrades or set()
        self.refresh_program_cards()
        if not automatic or self.upgradeable_programs:
            if upgrades is None:
                message = "Consulta indisponível. Os apps podem ser atualizados pelo próprio fabricante."
            elif upgrades:
                message = "Atualizações disponíveis nos cartões dos aplicativos."
            else:
                message = "O WinGet não encontrou atualizações para os aplicativos do catálogo."
            self.program_updates_status.setText(message)
            self.program_updates_status.show()

    def prepare_virtualbox_templates(self):
        if (self.vm_template_thread and self.vm_template_thread.isRunning()):
            return
        try:
            get_vboxmanage()
        except Exception as exc:
            QMessageBox.warning(self, "VirtualBox necessário", str(exc))
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
        self.vm_template_button.setEnabled(False)
        self.vm_template_progress.show()
        self.vm_template_status.setText("Preparando as máquinas no VirtualBox…")
        self.vm_template_status.show()
        self.vm_template_thread = VirtualBoxTemplateThread(Path(folder))
        self.vm_template_thread.progress.connect(self.vm_template_status.setText)
        self.vm_template_thread.result.connect(self.virtualbox_templates_finished)
        self.vm_template_thread.start()

    def virtualbox_templates_finished(self, ok: bool, message: str):
        self.vm_template_progress.hide()
        self.vm_template_button.setEnabled(True)
        self.vm_template_status.setText(message)
        self.status_message("Máquinas de teste preparadas." if ok else "Erro ao preparar VMs.")
        if ok:
            QMessageBox.information(self, "Máquinas preparadas", message)
        else:
            QMessageBox.warning(self, "Máquinas virtuais", message)

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
                self.status_message(f"{name} aberto.")
            except OSError as exc:
                QMessageBox.warning(self, "Falha ao abrir", str(exc))
            return
        if upgrade and app_id not in self.upgradeable_programs:
            return
        message = (f"Atualizar {name} pelo WinGet?" if upgrade else
                   f"Instalar {name}? A assinatura digital será conferida antes da execução.")
        if not confirmar(self, "Instalador oficial", message):
            return
        self.installing_program = app_id
        self.refresh_program_cards()
        self.show_program_progress("Preparando…", -1)
        self.extra_installer = ExtraInstallerThread(app_id, upgrade)
        self.extra_installer.progress.connect(self.show_program_progress)
        self.extra_installer.result.connect(self.extra_installer_done)
        self.extra_installer.start()

    def show_program_progress(self, message: str, percent: int):
        if self.installing_program is None:
            return
        for card, (primary, upgrade, progress, status) in self.program_controls.items():
            if program_key(card) != self.installing_program:
                continue
            primary.hide()
            upgrade.hide()
            progress.setRange(0, 0 if percent < 0 else 100)
            if percent >= 0:
                progress.setValue(percent)
            progress.show()
            status.setText(message)
            status.show()

    def extra_installer_done(self, ok: bool, message: str, app_id: str):
        name = EXTRA_APPS[app_id]["name"]
        self.installing_program = None
        installed = installed_program(app_id)
        if ok:
            self.upgradeable_programs.discard(app_id)
            message = "Pronto para abrir." if installed else (
                "O instalador terminou. O programa ainda não foi localizado; "
                "revise a instalação do fabricante.")
        for card, (_, _, progress, status) in self.program_controls.items():
            if program_key(card) == app_id:
                progress.hide()
                status.setText(message)
                status.show()
        self.refresh_program_cards()
        self.status_message(f"{name}: {message}")
        try:
            with (DATA_DIR / "instalacoes.log").open("a", encoding="utf-8") as log:
                log.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {name}: {message}\n")
        except OSError:
            pass
        if not ok:
            caixa = QMessageBox(self)
            caixa.setWindowTitle("Instalação interrompida")
            caixa.setTextFormat(Qt.TextFormat.PlainText)
            caixa.setText(f"{name}\n\n{message}")
            caixa.setIcon(QMessageBox.Icon.Warning)
            website = caixa.addButton("Abrir site oficial", QMessageBox.ButtonRole.ActionRole)
            caixa.addButton("Fechar", QMessageBox.ButtonRole.RejectRole)
            caixa.exec()
            if caixa.clickedButton() is website:
                webbrowser.open(official_website(app_id))

    def start_clean(self):
        if self.update_mode == "install":
            return
        if self.cleaner:
            return
        if not any(check.isChecked() for check in
                   (self.clean_user, self.clean_windows, self.clean_recycle, self.clean_icons, self.clean_nvidia)):
            QMessageBox.information(self, "Limpeza", "Selecione ao menos uma opção.")
            return
        selection = []
        unavailable = []
        if self.clean_user.isChecked():
            user_temp = known_temp_folders(False)
            selection.extend(user_temp)
            if not user_temp:
                unavailable.append("Pasta temporária do usuário indisponível.")
        if self.clean_windows.isChecked() and os.name == "nt":
            windows_temp = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp"
            system_temp = [p for p in known_temp_folders(True) if p == windows_temp]
            selection.extend(system_temp)
            if not system_temp:
                unavailable.append("Pasta temporária do Windows indisponível.")
        if self.clean_nvidia.isChecked():
            dxcache = nvidia_dxcache_folders()
            selection.extend(dxcache)
            if not dxcache:
                unavailable.append("Cache NVIDIA DXCache não localizado neste perfil.")
        selection = list(dict.fromkeys(selection))
        if not confirmar(self, "Confirmar limpeza", "Executar as opções selecionadas?\nArquivos protegidos ou em uso serão preservados."):
            return
        self.clean_output.clear()
        self.clean_output.appendPlainText("Iniciando limpeza...")
        for message in unavailable:
            self.clean_output.appendPlainText(message)
        self.clean_progress.setRange(0, 0)
        self.clean_start.setEnabled(False)
        self.clean_stop.setEnabled(True)
        self.cleaner = CleanerThread(selection, self.clean_recycle.isChecked(), self.clean_icons.isChecked())
        self.cleaner.progress.connect(self.clean_output.appendPlainText)
        self.cleaner.complete.connect(self.clean_finished)
        self.cleaner.finished.connect(self.clean_thread_finished)
        self.cleaner.start()
        self.status_message("Limpeza em andamento...")

    def cancel_clean(self):
        if self.cleaner and self.cleaner.isRunning():
            self.cleaner.cancel_flag.set()
            self.clean_output.appendPlainText("Cancelamento solicitado. Finalizando item atual...")

    def clean_finished(self, stats):
        self.clean_progress.setRange(0, 100)
        self.clean_progress.setValue(100 if not stats.cancelled else 0)
        self.clean_stop.setEnabled(False)
        final = (f"Arquivos removidos: {stats.files} | Pastas vazias: {stats.folders} | "
                 f"Espaço liberado: {format_size(stats.bytes_freed)} | Ignorados: {stats.skipped} | "
                 f"Lixeira: {stats.recycle_bin}"
                 f" | Cache de ícones: {stats.icon_cache}"
                 + (" | Cancelada" if stats.cancelled else ""))
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

    def clean_thread_finished(self):
        thread = self.cleaner
        self.cleaner = None
        thread.deleteLater()
        self.clean_start.setEnabled(True)

    def check_update(self, manual: bool):
        if self.updater_process is not None and self.updater_process.poll() is None:
            if manual:
                self.goto("updates")
            return
        if not (runtime_dir() / "updater.ps1").is_file():
            if manual:
                QMessageBox.warning(self, "Atualização", "O atualizador ainda não está disponível.")
            return
        self.update_mode = "check"
        self.update_elapsed = 0
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.top_check.setEnabled(False)
        self.update_note.setText("Consultando a última Release estável...")
        self.update_progress.setRange(0, 0)
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
        self.update_elapsed += 1
        if self.update_status.is_file():
            try:
                status = self.update_status.read_text(encoding="ascii").strip()
            except OSError:
                return
            if self.update_mode == "install" and status == "READY":
                self.update_timer.stop()
                self.status_message("Atualização verificada. Fechando para instalar...")
                QApplication.quit()
                return
            if status == "ERROR":
                self.update_failed("A atualização falhou. Consulte atualizacoes.log.")
                return
            if self.update_mode == "check" and status == "CURRENT":
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
                if confirmar(self, "Atualização disponível",
                         f"Nova versão encontrada: {release}\nVersão instalada: {APP_VERSION}\n\nDeseja baixar e atualizar agora?", True):
                    self.install_update()
                return
        if self.updater_process and self.updater_process.poll() is not None:
            self.update_failed("Atualizador encerrou sem informar o resultado. Consulte os logs.")
            return
        if self.update_elapsed > 900:
            self.update_failed("Tempo limite da atualização. Confira a conexão e os logs.")

    def stop_update_timer(self, success: bool = True):
        if hasattr(self, "update_timer"):
            self.update_timer.stop()
        self.updater_process = None
        self.update_mode = ""
        self.top_check.setEnabled(True)
        self.update_progress.setRange(0, 100)
        self.update_progress.setValue(100 if success else 0)

    def update_failed(self, message: str):
        self.stop_update_timer(False)
        self.update_note.setText(message)
        self.status_message(message)
        QMessageBox.warning(self, "Atualização", message)

    def install_update(self):
        if (self.installing_program or (self.cleaner and self.cleaner.isRunning()) or
                (self.extensions_job and self.extensions_job.isRunning()) or
                getattr(self, "native_timer", None) is not None):
            self.update_note.setText("Conclua a tarefa em andamento antes de instalar a atualização.")
            return
        if self.updater_process and self.updater_process.poll() is None:
            return
        if not getattr(sys, "frozen", False):
            QMessageBox.information(self, "Atualização", "A substituição automática exige a edição .exe. No modo código-fonte, use o GitHub Releases.")
            return
        self.update_mode = "install"
        self.update_elapsed = 0
        self.update_status = DATA_DIR / ("updater-" + uuid.uuid4().hex + ".status")
        self.top_check.setEnabled(False)
        self.update_progress.setRange(0, 0)
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
        if not hasattr(self, "program_grid"):
            return
        # Reorganiza os cards sem posicoes absolutas, conforme a largura visivel.
        narrow = self.width() < 1120
        if getattr(self, "_program_stacked", None) == narrow:
            return
        self._program_stacked = narrow
        columns = 1 if narrow else 2
        for card in self.all_program_cards:
            self.program_grid.removeWidget(card)
        for index, card in enumerate(self.all_program_cards):
            self.program_grid.addWidget(card, index // columns, index % columns)

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
        event.accept()


def main():
    if "--callas-task" in sys.argv:
        try:
            index = sys.argv.index("--callas-task")
            report_index = sys.argv.index("--callas-report")
            return run_windows_action(sys.argv[index+1], sys.argv[report_index+1])
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
