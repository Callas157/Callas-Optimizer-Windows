"""Regressoes da identidade Fênix e navegacao na mesma janela."""
from pathlib import Path
from xml.etree import ElementTree
import ast
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from extra_installers import CATALOG, _safe_https


class OptimaInterfaceContract(unittest.TestCase):
    def test_dashboard_and_routes(self):
        gui = (ROOT / "src/app.py").read_text(encoding="utf-8")
        ast.parse(gui)
        self.assertIn('Callas Optima', gui)
        self.assertIn('def _drivers_page(', gui)
        self.assertIn('QStackedWidget()', gui)
        self.assertIn('def _refresh_home_layout(', gui)
        self.assertIn('def open_windows_settings(', gui)
        self.assertIn('startupapps', gui)
        self.assertIn('Armazenamento do sistema', gui)

        for title, route in [('Clean', 'clean'), ('Boost', 'gamer'), ('Repair', 'repair'),
                             ('Apps', 'programs'), ('Drivers', 'drivers'), ('Atualizar', 'updates')]:
            self.assertIn(f'"{title}"', gui)
            self.assertIn(f'"{route}"', gui)
        self.assertNotIn('92% Otimizado', gui)

    def test_new_program_cards_and_sources(self):
        gui = (ROOT / "src/app.py").read_text(encoding="utf-8")
        for card in ('discord_card', 'steam_card', 'epic_card', 'wise_card'):
            self.assertIn('self.' + card, gui)
        for app_id in ("brave", "discord", "steam", "epic", "wise"):
            self.assertTrue(_safe_https(CATALOG[app_id]["url"], CATALOG[app_id]["hosts"]))
            self.assertTrue(CATALOG[app_id]["publisher"])
        self.assertTrue(CATALOG["epic"]["website"].startswith("https://store.epicgames.com/"))
        self.assertTrue(CATALOG["wise"]["website"].startswith("https://www.wisecleaner.com/"))

    def test_phoenix_visual_assets(self):
        for path in ("assets/icons/callas.svg", "assets/optima-preview.svg",
                     "assets/icons/discord.svg", "assets/icons/steam.svg",
                     "assets/icons/epic.svg", "assets/icons/wise.svg"):
            root = ElementTree.parse(ROOT / path).getroot()
            self.assertTrue(root.tag.endswith("svg"), path)
        png = (ROOT / "assets/icons/phoenix-approved.png").read_bytes()
        self.assertEqual(png[:8], bytes.fromhex("89504e470d0a1a0a"))
        self.assertTrue((ROOT / "assets/optima-approved-preview.jpg").is_file())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("assets/optima-interface.png", readme)
        self.assertLess(readme.index("Fênix Edition"), readme.index("assets/optima-interface.png"))
        self.assertIn("scripts/make_icon.py", (ROOT/"scripts/build.py").read_text() +
                      (ROOT/"README.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
