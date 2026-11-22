"""Callas Optimizer Windows 8.9.6 — Manutenção em Python e runtime instalado.

Python/PySide6. Operacoes legadas ainda reutilizam o BAT original, mas
limpeza, atualizacoes, navegacao e painel de logs sao controles nativos.
"""
from __future__ import annotations

import ctypes
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

from PySide6.QtCore import QByteArray, QSettings, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSplitter, QStackedWidget, QVBoxLayout, QWidget,
)

from cleaner import clean_folders, empty_recycle_bin, format_size, known_temp_folders
from windows_actions import ACTIONS, BY_ROUTE, HOME as ACTION_HOME, worker as run_windows_action
from extra_installers import CATALOG as EXTRA_APPS, download_and_open, official_website

APP_VERSION = "8.9.14"
REPO = "Callas157/Callas-Optimizer-Windows"
PROJECT_URL = f"https://github.com/{REPO}"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CallasTeck"

# Um id selecionado corresponde a UMA pagina, com conteudo proprio.
NAV_SECTIONS = [
    ("VISÃO GERAL", [("home", "Início", "⌂"), ("programs", "Programas", "▦")]),
    ("MANUTENÇÃO", [
        ("gamer", "Modo Gamer", "⚡"),
        ("edge", "Microsoft Edge", "◇"),
        ("windows_update", "Windows Update", "↻"),
        ("network", "Rede e DNS", "◎"),
        ("privacy", "Privacidade", "◉"),
        ("repair", "Reparar Windows", "✚"),
        ("drivers", "Drivers", "▣"),
        ("clean", "Limpeza Total", "♻"),
        ("classic", "Menu clássico", "▤"),
        ("shutdown", "Desligamento", "⏻"),
        ("winutil", "WinUtil", "▣"),
        ("updates", "Atualizações", "↓"),
        ("restore_point", "Ponto de restauração", "✦"),
        ("restore", "Restaurar padrões", "↩"),
    ]),
    ("CENTRAL", [("logs", "Registros", "≡"), ("about", "Sobre", "ⓘ")]),
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
QFrame#Sidebar { background: qlineargradient(x1:0,y1:0,x2:0.4,y2:1,stop:0 #0b0d2c,stop:0.65 #101131,stop:1 #19104a); border-right: 1px solid #4a297b; }
QFrame#Topbar { background: #0b102a; border-bottom: 1px solid #37265a; }
QFrame#Card { background: #111b37; border: 1px solid #403a71; border-radius: 15px; }
QFrame#QuickCard { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #27134e,stop:.55 #151c43,stop:1 #07274c); border: 1px solid #7954dc; border-radius: 18px; }
QFrame#Hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #30135a,stop:.43 #101d4b,stop:1 #052b55); border: 2px solid #8159ff; border-radius: 21px; }
QLabel#Header { font-size: 25px; font-weight: 700; color: #f8f7ff; }
QLabel#Title { font-size: 27px; font-weight: 700; color: #f9f8ff; }
QLabel#HeroTitle { font-size: 34px; font-weight: 800; color: #fff; }
QLabel#CardTitle { font-size: 17px; font-weight: 700; color: #f8f8ff; }
QLabel#Muted { color: #a8b9d8; }
QLabel#Section { color: #bc91ff; font-weight: 700; font-size: 11px; letter-spacing: 1px; }
QPushButton { background: #22234e; color: #f2f3ff; border: 1px solid #635e9b; border-radius: 11px; padding: 10px 13px; font-weight: 600; }
QPushButton:hover { background: #38347c; border-color: #b87aff; }
QPushButton:disabled { color: #7880a6; background: #1b2241; border-color: #3a3b61; }
QPushButton#Primary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #a02bdf,stop:.55 #523cec,stop:1 #087bff); border: 1px solid #9e6dff; color: #fff; }
QPushButton#Primary:hover { background: #8753ee; border-color: #52e3ff; }
QPushButton#Quick { text-align: left; background: transparent; border: none; padding: 7px; color: #ffffff; font-size: 17px; font-weight: 700; }
QPushButton#Quick:hover { background: #3a2877; }
QPushButton#Nav { background: transparent; border: none; border-radius: 9px; padding: 9px 12px; text-align: left; color: #d0d7f6; font-size: 13px; }
QPushButton#Nav:hover { background: #342563; color: white; }
QPushButton#Nav:checked { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6829a6,stop:1 #235ec5); border: 1px solid #bb73ff; color: white; }
QScrollArea { border: none; background: transparent; }
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
    svg = asset_dir() / (name + ".svg")
    renderer = QSvgRenderer(QByteArray(svg.read_bytes()))
    result = QPixmap(pixels, pixels)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    renderer.render(painter)
    painter.end()
    return QIcon(result)


def runtime_files() -> None:
    """Instala recursos versionados numa pasta do usuario sem executar da temp do PyInstaller."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("updater.ps1", "install_brave.ps1", "install_nvidia.ps1",
                 "extensions.ps1", "undo_extensions.ps1"):
        source = runtime_dir() / name
        target = DATA_DIR / name
        if not source.is_file():
            raise FileNotFoundError(f"Recurso da aplicação não encontrado: {name}")
        data = source.read_bytes()
        if target.is_file() and target.read_bytes() == data:
            continue
        temp_target = target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp")
        temp_target.write_bytes(data)
        os.replace(temp_target, target)


def in_windows11() -> bool:
    if os.name != "nt":
        return False
    try:
        v = sys.getwindowsversion()
        return v.major == 10 and v.build >= 22000
    except AttributeError:
        return False


def start_script(name: str) -> None:
    path = DATA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(str(path))
    flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    subprocess.Popen(["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                      "-File", str(path)], cwd=str(DATA_DIR), creationflags=flags)



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
    progress = Signal(str)
    result = Signal(bool, str)

    def __init__(self, app_id: str):
        super().__init__()
        self.app_id = app_id

    def run(self):
        try:
            message = download_and_open(self.app_id, self.progress.emit)
            self.result.emit(True, message)
        except Exception as exc:
            self.result.emit(False, str(exc))


class CleanerThread(QThread):
    progress = Signal(str)
    complete = Signal(object)

    def __init__(self, roots: list[Path], recycle: bool):
        super().__init__()
        self.roots = roots
        self.recycle = recycle
        self.cancel_flag = threading.Event()

    def run(self):
        stats = clean_folders(self.roots, self.cancel_flag, self.progress.emit)
        if self.recycle and not self.cancel_flag.is_set():
            try:
                empty_recycle_bin()
                stats.recycle_bin = True
                self.progress.emit("Lixeira esvaziada com sucesso")
            except Exception as e:
                stats.skipped += 1
                self.progress.emit(f"Não foi possível esvaziar a lixeira: {e}")
        self.complete.emit(stats)


NAV_ICONS = {
    "home": "⌂", "gamer": "⚡", "edge": "◇", "windows_update": "↻",
    "network": "◎", "privacy": "◈", "repair": "✚", "clean": "♻",
    "classic": "▤", "shutdown": "⏻", "winutil": "▣",
    "updates": "↓", "restore_point": "✦", "restore": "↩",
    "programs": "▦", "drivers": "▣", "logs": "≡", "about": "ⓘ",
}


def menu_icon(route: str) -> QIcon:
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
        "clean": '<path d="M6 3h12M9 3v3h6V3M5 7h14l-1 14H6zM10 10v8m4-8v8"/>',
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
           'fill="none" stroke="#8ec3ff" stroke-width="1.7" '
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Callas Optima {APP_VERSION}  |  Windows Edition")
        self.setWindowIcon(app_icon())
        # Borda e controles nativos (incluindo maximizar); a janela pode ser redimensionada.
        self.setMinimumSize(810, 570)
        self.resize(1200, 815)
        self.settings = QSettings("Callas", "OptimizerWindows")
        self.cleaner: CleanerThread | None = None
        self.extra_installer: ExtraInstallerThread | None = None
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
        self.splitter.setSizes([300, 900])
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
        sidebar.setMinimumWidth(245)
        sidebar.setMaximumWidth(365)
        shell = QVBoxLayout(sidebar)
        shell.setContentsMargins(15, 19, 12, 14)
        shell.setSpacing(14)
        brand = QHBoxLayout()
        brand.setSpacing(12)
        logo = QLabel()
        logo.setPixmap(app_icon().pixmap(43, 43))
        brand.addWidget(logo)
        words = QVBoxLayout()
        words.setSpacing(0)
        words.addWidget(label("Callas Optima", "CardTitle"))
        words.addWidget(label("WINDOWS • FÊNIX EDITION", "Muted"))
        brand.addLayout(words)
        brand.addStretch()
        shell.addLayout(brand)
        shell.addWidget(label("CENTRAL DE CONTROLE", "Section"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        nav = QVBoxLayout(content)
        nav.setContentsMargins(0, 0, 0, 0)
        nav.setSpacing(2)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        for section, entries in NAV_SECTIONS:
            heading = label(section, "Section")
            heading.setContentsMargins(8, 15, 0, 6)
            nav.addWidget(heading)
            for route, title, glyph in entries:
                btn = action_button(title, lambda _=False, key=route: self.goto(key))
                btn.setIcon(menu_icon(route))
                btn.setIconSize(QSize(23, 23))
                btn.setMinimumHeight(47)
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
        titles = QVBoxLayout()
        titles.setSpacing(3)
        titles.addWidget(label("Callas Optima", "Header"))
        titles.addWidget(label("Desempenho e renovação • Windows 11"))
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
        self.status_label = label("Pronto. Selecione uma ferramenta na lateral.")
        fh.addWidget(self.status_label, 1)
        fh.addWidget(label("Windows 11 Pro / Enterprise / IoT LTSC", "Section"))
        col.addWidget(foot)
        self.splitter.addWidget(central)

    def _page(self, route: str, title: str, description: str) -> QVBoxLayout:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 26, 30, 34)
        layout.setSpacing(18)
        layout.addWidget(label("CALLAS  /  CONTROLE CENTRAL", "Section"))
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
        """Dashboard Fênix: atalhos levam às páginas reais do mesmo QStackedWidget."""
        col = self._page("home", "Callas Optima", "Seu centro de manutenção, desempenho e renovação do Windows.")
        hero, box = card_layout("Hero")
        row = QHBoxLayout()
        content = QVBoxLayout()
        content.setSpacing(12)
        content.addWidget(label("FÊNIX EDITION  •  v" + APP_VERSION, "Section"))
        content.addWidget(label("Seu Windows no controle", "HeroTitle"))
        content.addWidget(label(
            "Limpeza, ajustes para jogos, reparos e aplicativos oficiais, "
            "com cada ferramenta em uma seção da mesma janela."))
        primary = action_button("EXPLORAR OTIMIZAÇÃO", lambda: self.goto("gamer"), True)
        content.addWidget(primary)
        content.addStretch()
        row.addLayout(content, 3)
        image = QLabel()
        image.setPixmap(svg_icon("callas", 210).pixmap(QSize(205, 205)))
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(image, 2)
        box.addLayout(row)
        col.addWidget(hero)

        col.addWidget(label("ACESSO RÁPIDO", "Section"))
        tiles = QGridLayout()
        tiles.setHorizontalSpacing(13)
        tiles.setVerticalSpacing(13)
        shortcuts = [
            ("✦", "Clean", "Limpeza de arquivos temporários", "clean"),
            ("↗", "Boost", "Ajustes de desempenho para jogos", "gamer"),
            ("✚", "Repair", "Reparar arquivos e componentes", "repair"),
            ("▦", "Apps", "Instaladores e programas oficiais", "programs"),
            ("▣", "Drivers", "NVIDIA App e ferramentas oficiais", "drivers"),
            ("↻", "Atualizar", "Versões estáveis do Callas Optima", "updates"),
        ]
        for index, (glyph, title, description, route) in enumerate(shortcuts):
            tile, layout = card_layout("QuickCard")
            layout.setContentsMargins(15, 14, 15, 12)
            head = action_button(glyph + "  " + title + "    ›",
                                 lambda _=False, target=route: self.goto(target))
            head.setObjectName("Quick")
            layout.addWidget(head)
            layout.addWidget(label(description, "Muted"))
            tiles.addWidget(tile, index // 3, index % 3)
        col.addLayout(tiles)

        footer = QHBoxLayout()
        health, h = card_layout()
        h.addWidget(label("Saúde do sistema", "CardTitle"))
        h.addWidget(label("Execute os diagnósticos do Windows para verificar a integridade. "
                          "O Callas não atribui uma nota de saúde sem medição."))
        h.addWidget(action_button("VER DIAGNÓSTICOS", lambda: self.goto("repair")))
        footer.addWidget(health, 1)
        space, sc = card_layout()
        sc.addWidget(label("Armazenamento", "CardTitle"))
        try:
            root = Path(os.environ.get("SystemDrive", "C:") + "\\") if os.name == "nt" else Path.home()
            usage = shutil.disk_usage(root)
            free = usage.free / (1024**3)
            total = usage.total / (1024**3)
            sc.addWidget(label(f"{free:.1f} GB livres de {total:.1f} GB"))
            progress = QProgressBar()
            progress.setValue(int(100 * (usage.total - usage.free) / usage.total))
            sc.addWidget(progress)
        except (OSError, ZeroDivisionError):
            sc.addWidget(label("Dados indisponíveis neste computador."))
        sc.addWidget(action_button("ABRIR LIMPEZA", lambda: self.goto("clean")))
        footer.addWidget(space, 1)
        col.addLayout(footer)
        col.addStretch()

    def _drivers_page(self):
        col = self._page(
            "drivers", "Drivers", "Acesso às ferramentas oficiais. Nenhum driver é trocado automaticamente.")
        c, body = card_layout()
        body.addWidget(label("NVIDIA APP", "Section"))
        body.addWidget(label(
            "Abra o instalador oficial do NVIDIA App. Nele, você pode verificar "
            "drivers disponíveis e escolher quando instalar; o Callas não remove "
            "drivers nem força versões sem sua confirmação."))
        body.addWidget(action_button(
            "BAIXAR NVIDIA APP", lambda: self.ps_action("install_nvidia.ps1", "NVIDIA App"), True))
        col.addWidget(c)
        other, layout = card_layout()
        layout.addWidget(label("DRIVERS PELO WINDOWS", "Section"))
        layout.addWidget(label("Use as opções oficiais de Windows Update para drivers opcionais. "
                               "Evite instaladores de terceiros que prometem atualizar tudo."))
        layout.addWidget(action_button("ABRIR WINDOWS UPDATE", lambda: self.goto("windows_update")))
        col.addWidget(other)
        col.addStretch()

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
        for chk in (self.clean_user, self.clean_windows, self.clean_recycle):
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

    def _program_card(self, name: str, icon: str, description: str, action_title: str, action):
        outer, content = card_layout()
        title_row = QHBoxLayout()
        img = QLabel()
        img.setPixmap(svg_icon(icon, 100).pixmap(QSize(55, 55)))
        img.setFixedSize(57, 57)
        title_row.addWidget(img)
        names = QVBoxLayout()
        names.addWidget(label(name, "CardTitle"))
        names.addWidget(label(description))
        title_row.addLayout(names, 1)
        content.addLayout(title_row)
        content.addWidget(action_button(action_title, action, True))
        return outer

    def _program_page(self):
        col = self._page("programs", "Central de aplicativos", "Programas oficiais e configurações do navegador, separados das ferramentas do sistema.")
        self.program_grid = QGridLayout()
        self.program_grid.setSpacing(16)
        self.brave_card = self._program_card(
            "Brave Browser", "brave", "Com SteamDB e Bonjourr", "INSTALAR / CONFIGURAR",
            lambda: self.ps_action("install_brave.ps1", "Brave Browser"))
        self.nvidia_card = self._program_card(
            "NVIDIA App", "nvidia", "Instalação oficial; não muda o driver sozinho", "BAIXAR / INSTALAR",
            lambda: self.ps_action("install_nvidia.ps1", "NVIDIA App"))
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
            "OBTER APP OFICIAL",
            lambda: self.open_openai_download("ChatGPT"))
        self.codex_card = self._program_card(
            "Codex", "codex", "Trabalhe em projetos e arquivos locais com sua autorização",
            "OBTER APP COM CODEX",
            lambda: self.open_openai_download("Codex"))
        self.discord_card = self._program_card(
            "Discord", "discord", "Conversas, comunidades e voz", "BAIXAR INSTALADOR",
            lambda: self.install_extra("discord"))
        self.steam_card = self._program_card(
            "Steam", "steam", "Biblioteca de jogos para PC", "BAIXAR INSTALADOR",
            lambda: self.install_extra("steam"))
        self.epic_card = self._program_card(
            "Epic Games Launcher", "epic", "Loja e biblioteca Epic Games", "ABRIR DOWNLOAD OFICIAL",
            lambda: self.open_program_website("epic"))
        self.wise_card = self._program_card(
            "Wise Program Uninstaller", "wise", "Desinstalação de aplicativos", "ABRIR DOWNLOAD OFICIAL",
            lambda: self.open_program_website("wise"))
        self.all_program_cards = [
            self.brave_card, self.nvidia_card, self.medal_card,
            self.lghub_card, self.spotify_card, self.chatgpt_card, self.codex_card,
            self.discord_card, self.steam_card, self.epic_card, self.wise_card,
        ]
        for index, card in enumerate(self.all_program_cards):
            self.program_grid.addWidget(card, index // 2, index % 2)
        col.addLayout(self.program_grid)
        self.extra_status = label("Discord, Steam, Medal, Logitech e Spotify: executáveis com assinatura verificada. Epic, Wise e ChatGPT/Codex: site oficial.")
        col.addWidget(self.extra_status)
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
        row.addWidget(action_button("CONFIGURAR EXTENSÕES", lambda: self.ps_action("extensions.ps1", "Extensões Brave"), True))
        row.addWidget(action_button("DESFAZER POLÍTICAS", lambda: self.ps_action("undo_extensions.ps1", "Remover políticas")))
        box.addLayout(row)
        col.addWidget(c)
        col.addStretch()

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

    def status_message(self, message: str):
        self.status_label.setText(message)

    def native_action(self, code: str):
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
        args = f'--callas-task {code} --callas-report {self.native_report.name}'
        try:
            if task["admin"]:
                rc = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, args, None, 1)
                if int(rc) <= 32:
                    raise RuntimeError("Permissão UAC não concedida.")
            else:
                subprocess.Popen(
                    [sys.executable, "--callas-task", code, "--callas-report", self.native_report.name],
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

    def ps_action(self, script: str, name: str):
        if not confirmar(self, "Confirmar operação", f"Abrir a ferramenta {name}?", True):
            return
        try:
            start_script(script)
            self.status_message(f"{name}: ferramenta aberta no PowerShell.")
        except Exception as e:
            QMessageBox.critical(self, "Não foi possível iniciar", str(e))

    def open_openai_download(self, requested: str):
        # ChatGPT, Work e Codex pertencem ao mesmo aplicativo oficial para Windows.
        # Apenas abre a página do fabricante, sem instaladores espelhados, API keys,
        # login capturado ou acesso automático a arquivos da máquina.
        if requested not in ("ChatGPT", "Codex"):
            return
        message = (
            f"Obter {requested} pelo site oficial da OpenAI?\n\n"
            "O aplicativo ChatGPT para Windows já inclui Chat, Work e Codex. "
            "Não é necessário instalar dois aplicativos.\n\n"
            "O acesso a arquivos locais é configurado dentro do aplicativo oficial, "
            "quando você escolher um projeto ou pasta."
        )
        if not confirmar(self, "Download oficial da OpenAI", message, True):
            return
        if not webbrowser.open("https://chatgpt.com/download/"):
            QMessageBox.warning(
                self, "Abrir download",
                "Não foi possível abrir o navegador. Acesse https://chatgpt.com/download/"
            )
        else:
            self.status_message("Página oficial de ChatGPT e Codex aberta no navegador.")

    def open_program_website(self, app_id: str):
        """Instaladores de URL dinamica: apenas o site HTTPS oficial."""
        from extra_installers import WEBSITE_ONLY
        if app_id not in WEBSITE_ONLY:
            return
        entry = WEBSITE_ONLY[app_id]
        if confirmar(self, "Site oficial", f"Abrir o download oficial de {entry['name']} no navegador?", True):
            if webbrowser.open(entry["website"]):
                self.status_message(f"Site oficial de {entry['name']} aberto.")
            else:
                QMessageBox.warning(self, "Navegador", "Não foi possível abrir o site oficial.")

    def install_extra(self, app_id: str):
        if self.extra_installer and self.extra_installer.isRunning():
            QMessageBox.information(self, "Download em andamento", "Conclua o download atual antes de iniciar outro.")
            return
        name = EXTRA_APPS[app_id]["name"]
        if not confirmar(self, "Instalador oficial",
                         f"Baixar o instalador de {name} pelo site oficial?\n"
                         "A assinatura digital será conferida antes de abrir o arquivo."):
            return
        self.extra_status.setText(f"Preparando o download de {name}...")
        self.extra_installer = ExtraInstallerThread(app_id)
        self.extra_installer.progress.connect(self.extra_status.setText)
        self.extra_installer.result.connect(
            lambda ok, msg, key=app_id: self.extra_installer_done(ok, msg, key))
        # Mantenha o objeto da thread ate a proxima acao.
        # deleteLater aqui deixaria uma referencia invalida em self.extra_installer.
        self.extra_installer.start()

    def extra_installer_done(self, ok: bool, message: str, app_id: str):
        name = EXTRA_APPS[app_id]["name"]
        self.extra_status.setText(
            f"{name}: instalador aberto." if ok else f"{name}: download não concluído.")
        if ok:
            QMessageBox.information(self, "Instalador oficial", message)
        else:
            caixa = QMessageBox(self)
            caixa.setWindowTitle("Falha no download")
            caixa.setText(f"Não foi possível preparar o {name}.\n\n{message}")
            caixa.setIcon(QMessageBox.Icon.Warning)
            website = caixa.addButton("Abrir site oficial", QMessageBox.ButtonRole.ActionRole)
            caixa.addButton("Fechar", QMessageBox.ButtonRole.RejectRole)
            caixa.exec()
            if caixa.clickedButton() is website:
                webbrowser.open(official_website(app_id))

    def start_clean(self):
        if self.cleaner and self.cleaner.isRunning():
            return
        if not any((self.clean_user.isChecked(), self.clean_windows.isChecked(), self.clean_recycle.isChecked())):
            QMessageBox.information(self, "Limpeza", "Selecione ao menos uma opção.")
            return
        selection = []
        if self.clean_user.isChecked():
            selection.extend(known_temp_folders(False))
        if self.clean_windows.isChecked() and os.name == "nt":
            windows_temp = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp"
            selection.extend([p for p in known_temp_folders(True) if p == windows_temp.resolve()])
        selection = list(dict.fromkeys(selection))
        if not confirmar(self, "Confirmar limpeza", "Remover arquivos temporários selecionados e, se marcado, esvaziar a Lixeira?\nArquivos em uso serão ignorados."):
            return
        self.clean_output.clear()
        self.clean_output.appendPlainText("Iniciando limpeza...")
        self.clean_progress.setRange(0, 0)
        self.clean_start.setEnabled(False)
        self.clean_stop.setEnabled(True)
        self.cleaner = CleanerThread(selection, self.clean_recycle.isChecked())
        self.cleaner.progress.connect(self.clean_output.appendPlainText)
        self.cleaner.complete.connect(self.clean_finished)
        self.cleaner.finished.connect(self.cleaner.deleteLater)
        self.cleaner.finished.connect(lambda: setattr(self, "cleaner", None))
        self.cleaner.start()
        self.status_message("Limpeza em andamento...")

    def cancel_clean(self):
        if self.cleaner and self.cleaner.isRunning():
            self.cleaner.cancel_flag.set()
            self.clean_output.appendPlainText("Cancelamento solicitado. Finalizando item atual...")

    def clean_finished(self, stats):
        self.clean_progress.setRange(0, 100)
        self.clean_progress.setValue(100 if not stats.cancelled else 0)
        self.clean_start.setEnabled(True)
        self.clean_stop.setEnabled(False)
        final = (f"Arquivos removidos: {stats.files} | Pastas vazias: {stats.folders} | "
                 f"Espaço liberado: {format_size(stats.bytes_freed)} | Ignorados: {stats.skipped} | "
                 f"Lixeira: {'esvaziada' if stats.recycle_bin else 'mantida'}"
                 + (" | Cancelada" if stats.cancelled else ""))
        self.clean_output.appendPlainText("\n" + final)
        self.status_message(final)
        try:
            DATA_DIR.mkdir(exist_ok=True, parents=True)
            with (DATA_DIR / "limpeza.log").open("a", encoding="utf-8") as log:
                log.write(datetime.now().isoformat(timespec="seconds") + " " + final + "\n")
        except OSError:
            pass

    def check_update(self, manual: bool):
        if self.updater_process is not None and self.updater_process.poll() is None:
            if manual:
                self.goto("updates")
            return
        if not (DATA_DIR / "updater.ps1").is_file():
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
            ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(DATA_DIR / "updater.ps1"), *args],
            cwd=str(DATA_DIR), creationflags=flags,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
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
        self.top_check.setEnabled(True)
        self.update_progress.setRange(0, 100)
        self.update_progress.setValue(100 if success else 0)

    def update_failed(self, message: str):
        self.stop_update_timer(False)
        self.update_note.setText(message)
        self.status_message(message)
        QMessageBox.warning(self, "Atualização", message)

    def install_update(self):
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
        if self.extra_installer and self.extra_installer.isRunning():
            QMessageBox.information(self, "Download em andamento",
                                    "Conclua o download do instalador antes de fechar.")
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
