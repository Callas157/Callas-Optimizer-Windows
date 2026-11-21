"""Callas Optimizer Windows 8.9.2 — Interface Qt responsiva.

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

APP_VERSION = "8.9.2"
REPO = "Callas157/Callas-Optimizer-Windows"
PROJECT_URL = f"https://github.com/{REPO}"
LEGACY_SCRIPT = "Callas_Optimizer_V8_8_GUI_Engine.bat"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CallasTeck"

# Um id selecionado corresponde a UMA pagina, com conteudo proprio.
NAV_SECTIONS = [
    ("VISÃO GERAL", [("home", "Início", "⌂")]),
    ("MANUTENÇÃO", [
        ("gamer", "1  Modo Gamer", "⚡"),
        ("edge", "2  Microsoft Edge", "◇"),
        ("windows_update", "3  Windows Update", "↻"),
        ("network", "4  Rede e DNS", "◎"),
        ("privacy", "5  Privacidade", "◉"),
        ("repair", "6  Reparar Windows", "✚"),
        ("clean", "7  Limpeza Total", "♻"),
        ("classic", "8  Menu clássico", "▤"),
        ("shutdown", "9  Desligamento", "⏻"),
        ("winutil", "10  WinUtil", "▣"),
        ("updates", "11  Atualizações", "↓"),
        ("restore_point", "12  Ponto de restauração", "✦"),
        ("restore", "13  Restaurar padrões", "↩"),
    ]),
    ("APLICATIVOS", [("programs", "Programas", "▦")]),
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
* { font-family: 'Segoe UI'; font-size: 13px; color: #d9e5fa; }
QMainWindow, QWidget#MainRoot { background: #0b1120; }
QFrame#Sidebar { background: #0c1425; border-right: 1px solid #24354f; }
QFrame#Topbar { background: #101a2d; border-bottom: 1px solid #263a5a; }
QFrame#Card { background: #152137; border: 1px solid #2a4160; border-radius: 16px; }
QFrame#Hero { background: #152b51; border: 1px solid #2e66b4; border-radius: 18px; }
QLabel#Header { font-size: 25px; font-weight: 700; color: #f2f7ff; }
QLabel#Title { font-size: 28px; font-weight: 700; color: #f6f9ff; }
QLabel#CardTitle { font-size: 17px; font-weight: 700; color: #f2f6ff; }
QLabel#Muted { color: #9fb2d1; }
QLabel#Section { color: #75afff; font-weight: 700; font-size: 11px; letter-spacing: 1px; }
QPushButton { background: #22324b; color: #eef5ff; border: 1px solid #3c567d; border-radius: 9px; padding: 11px 15px; font-weight: 600; }
QPushButton:hover { background: #2e4469; border-color: #628acd; }
QPushButton:disabled { color: #72849e; background: #1a283e; border-color: #2a3a54; }
QPushButton#Primary { background: #1d67ed; border: 1px solid #368aff; }
QPushButton#Primary:hover { background: #337dff; }
QPushButton#Nav { background: transparent; border: none; border-radius: 9px; padding: 10px 12px; text-align: left; color: #aebed6; font-size: 12px; }
QPushButton#Nav:hover { background: #1e304d; color: white; }
QPushButton#Nav:checked { background: #1d3e71; color: #fff; border-left: 3px solid #4390ff; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #0f182b; width: 9px; }
QScrollBar::handle:vertical { background: #385278; border-radius: 4px; min-height: 35px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QSplitter::handle { background: #253956; width: 3px; }
QCheckBox { spacing: 12px; font-size: 13px; }
QCheckBox::indicator { width: 19px; height: 19px; }
QProgressBar { border: 1px solid #3b557a; border-radius: 7px; text-align: center; background: #0f1b2c; min-height: 16px; }
QProgressBar::chunk { background: #2374ff; border-radius: 7px; }
QPlainTextEdit { background: #0b1627; color: #b3d0ed; border: 1px solid #315174; border-radius: 8px; padding: 10px; font-family: Consolas; font-size: 12px; }
QMessageBox { background: #152137; }
"""


def asset_dir() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / "assets" / "icons"


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
    for name in (LEGACY_SCRIPT, "updater.ps1", "install_brave.ps1", "install_nvidia.ps1",
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


def start_admin_bat(option: int) -> None:
    if os.name != "nt":
        raise OSError("O motor de manutenção exige Windows.")
    script = str(DATA_DIR / LEGACY_SCRIPT)
    if not Path(script).is_file():
        raise FileNotFoundError(script)
    command = f'/k ""{script}" :gui{option}"'
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", command, str(DATA_DIR), 1)
    if int(rc) <= 32:
        raise OSError(f"Windows não abriu a ferramenta (código {rc}).")


def start_script(name: str) -> None:
    path = DATA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(str(path))
    flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    subprocess.Popen(["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                      "-File", str(path)], cwd=str(DATA_DIR), creationflags=flags)


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
        self.setWindowTitle(f"Callas Optimizer {APP_VERSION}  |  Windows Edition")
        self.setWindowIcon(svg_icon("callas"))
        # Borda e controles nativos (incluindo maximizar); a janela pode ser redimensionada.
        self.setMinimumSize(810, 570)
        self.resize(1200, 815)
        self.settings = QSettings("Callas", "OptimizerWindows")
        self.cleaner: CleanerThread | None = None
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
        self.splitter.setSizes([247, 950])
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
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(290)
        shell = QVBoxLayout(sidebar)
        shell.setContentsMargins(15, 19, 12, 14)
        shell.setSpacing(14)
        brand = QHBoxLayout()
        brand.setSpacing(12)
        logo = QLabel()
        logo.setPixmap(svg_icon("callas", 96).pixmap(43, 43))
        brand.addWidget(logo)
        words = QVBoxLayout()
        words.setSpacing(0)
        words.addWidget(label("CALLAS", "CardTitle"))
        words.addWidget(label("OPTIMIZER  /  WINDOWS", "Muted"))
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
                btn = action_button(f"{glyph}    {title}", lambda _=False, key=route: self.goto(key))
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
        titles.addWidget(label("CALLAS OPTIMIZER", "Header"))
        titles.addWidget(label("Manutenção, programas e atualizações em um só lugar"))
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
        self._update_page()
        self._logs_page()
        self._about_page()
        for route, (op, title, description, warning) in LEGACY.items():
            self._legacy_page(route, op, title, description, warning)

    def _home_page(self):
        col = self._page("home", "Seu Windows, sob controle.", "Uma central de manutenção de verdade, com telas dedicadas para cada tarefa.")
        hero, box = card_layout("Hero")
        box.addWidget(label("WINDOWS EDITION  •  v" + APP_VERSION, "Section"))
        box.addWidget(label("Pronto para cuidar do seu PC", "Header"))
        box.addWidget(label("Limpeza com progresso, instaladores oficiais, diagnósticos e novas versões pelo GitHub."))
        actions = QHBoxLayout()
        actions.addWidget(action_button("ABRIR LIMPEZA TOTAL", lambda: self.goto("clean"), True))
        actions.addWidget(action_button("GERENCIAR PROGRAMAS", lambda: self.goto("programs")))
        actions.addStretch()
        box.addLayout(actions)
        col.addWidget(hero)
        row = QHBoxLayout()
        for title, desc, target in [
            ("13", "Ferramentas de manutenção", "gamer"),
            ("2", "Instaladores oficiais", "programs"),
            ("GitHub", "Atualizações com confirmação", "updates"),
        ]:
            tile, tcol = card_layout()
            tcol.addWidget(label(title, "Header"))
            tcol.addWidget(label(desc))
            tcol.addWidget(action_button("EXPLORAR", lambda _=False, r=target: self.goto(r)))
            row.addWidget(tile, 1)
        col.addLayout(row)
        safety, s = card_layout()
        s.addWidget(label("Transparência das operações", "CardTitle"))
        s.addWidget(label("A Limpeza Total funciona nesta interface. Algumas opções avançadas ainda utilizam o motor BAT com console e UAC, identificado em cada tela."))
        col.addWidget(safety)
        col.addStretch()

    def _legacy_page(self, route, option, title, description, warning):
        col = self._page(route, title, description)
        c, inner = card_layout()
        inner.addWidget(label("O QUE ESTA FERRAMENTA FAZ", "Section"))
        inner.addWidget(label(description, "CardTitle"))
        inner.addWidget(label(warning))
        inner.addWidget(label("Motor de manutenção 8.8 (compatibilidade): abre uma janela de console para opções e confirmações interativas."))
        inner.addWidget(action_button("ABRIR FERRAMENTA", lambda _=False, n=option: self.legacy_action(n), True))
        col.addWidget(c)
        follow, text = card_layout()
        text.addWidget(label("Precisa reverter uma alteração?", "CardTitle"))
        text.addWidget(label("Use o item Restaurar padrões ou consulte os logs antes de repetir a operação."))
        text.addWidget(action_button("CONSULTAR REGISTROS", lambda: self.goto("logs")))
        col.addWidget(follow)
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
        self.program_grid.addWidget(self.brave_card, 0, 0)
        self.program_grid.addWidget(self.nvidia_card, 0, 1)
        col.addLayout(self.program_grid)
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
        inner.addWidget(label("Versão instalada: " + APP_VERSION, "CardTitle"))
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
        controls.addWidget(label("A nova versão só substitui o executável depois de download completo, SHA-256, validação de arquitetura e backup."))
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
        l.addWidget(label("As funções avançadas ainda utilizam o motor BAT 8.8 enquanto migram gradualmente para módulos nativos."))
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

    def legacy_action(self, option: int):
        safety = "Esta opção pode alterar serviços e configurações do Windows."
        if option == 2:
            safety = "A remoção do Edge pode afetar aplicativos e componentes do Windows."
        if QMessageBox.question(self, "Confirmar operação", safety + "\n\nAbrir o motor de manutenção?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            start_admin_bat(option)
            self.status_message(f"Ferramenta {option} aberta no console (motor legado 8.8).")
        except Exception as e:
            QMessageBox.critical(self, "Falha ao iniciar", str(e))

    def ps_action(self, script: str, name: str):
        if QMessageBox.question(self, "Confirmar operação", f"Abrir a ferramenta {name}?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.Yes) != QMessageBox.StandardButton.Yes:
            return
        try:
            start_script(script)
            self.status_message(f"{name}: ferramenta aberta no PowerShell.")
        except Exception as e:
            QMessageBox.critical(self, "Não foi possível iniciar", str(e))

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
        if QMessageBox.question(self, "Confirmar limpeza", "Remover arquivos temporários selecionados e, se marcado, esvaziar a Lixeira?\nArquivos em uso serão ignorados.",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
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
            self._spawn_update(["-Check", "-CurrentVersion", APP_VERSION,
                                "-StatusFile", str(self.update_status)])
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
                if QMessageBox.question(self, "Atualização disponível",
                                        f"Nova versão encontrada: {release}\nVersão instalada: {APP_VERSION}\n\nDeseja baixar e atualizar agora?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.Yes) == QMessageBox.StandardButton.Yes:
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
            self._spawn_update(["-Install", "-CurrentVersion", APP_VERSION,
                                "-StatusFile", str(self.update_status),
                                "-Target", str(Path(sys.executable).resolve()), "-WaitPid", str(os.getpid())])
        except Exception as e:
            self.update_failed(str(e))
            return
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.poll_update)
        self.update_timer.start(700)
        self.goto("updates")

    def load_logs(self):
        result = []
        for name in ("limpeza.log", "instalacoes.log", "atualizacoes.log", "callas_teck.log"):
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
        self.program_grid.removeWidget(self.brave_card)
        self.program_grid.removeWidget(self.nvidia_card)
        self.program_grid.addWidget(self.brave_card, 0, 0)
        self.program_grid.addWidget(self.nvidia_card, 1 if narrow else 0, 0 if narrow else 1)

    def closeEvent(self, event):
        if self.cleaner and self.cleaner.isRunning():
            QMessageBox.information(self, "Limpeza em andamento", "Cancele ou conclua a Limpeza Total antes de fechar o aplicativo.")
            event.ignore()
            return
        event.accept()


def main():
    if os.name != "nt":
        # Os testes de layout com QT_QPA_PLATFORM=offscreen tambem podem rodar fora do Windows.
        if os.environ.get("QT_QPA_PLATFORM") != "offscreen":
            raise SystemExit("O Callas Optimizer Windows precisa de Windows 11.")
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True) if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling') else None
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
