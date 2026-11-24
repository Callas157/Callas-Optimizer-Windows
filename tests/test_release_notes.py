import unittest

from scripts.release_notes import render_notes


class ReleaseNotesTest(unittest.TestCase):
    def test_download_comes_first_and_notes_cover_only_the_requested_version(self):
        history = (
            "## v8.9.30 — Próxima versão\n\n- Mudança posterior.\n\n"
            "## v8.9.29 — Temporizador\n\n- Desligamento personalizado.\n\n"
            "## v8.9.28 — Versão anterior\n\n- Cartões compactos.\n"
        )
        notes = render_notes(history, "v8.9.29", "Callas157/Callas-Optimizer-Windows")
        self.assertEqual(
            notes.splitlines()[0],
            "**[Baixar instalador para Windows 11 x64 (.exe)]"
            "(https://github.com/Callas157/Callas-Optimizer-Windows/releases/download/"
            "v8.9.29/Callas_Optimizer_Setup_x64.exe)**",
        )
        self.assertIn("Desligamento personalizado.", notes)
        self.assertIn("/blob/v8.9.29/CHANGELOG.md", notes)
        self.assertNotIn("Mudança posterior.", notes)
        self.assertNotIn("Cartões compactos.", notes)

    def test_missing_version_fails_instead_of_publishing_the_wrong_notes(self):
        with self.assertRaisesRegex(ValueError, r"v8\.9\.2"):
            render_notes("## v8.9.29 — Temporizador\n\n- Temporizador.", "v8.9.2", "Callas157/Callas-Optimizer-Windows")
