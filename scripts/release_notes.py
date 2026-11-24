"""Gera as notas de uma versão com o download direto do Setup no topo."""
import argparse
from pathlib import Path
import re


def render_notes(changelog: str, tag: str, repository: str) -> str:
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError(f"Tag inválida: {tag}")
    heading = re.compile(rf"## {re.escape(tag)}(?:[ \t]+.*)?")
    section = next(
        (entry.strip() for entry in re.split(r"(?m)(?=^## )", changelog)
         if heading.fullmatch(entry.partition("\n")[0])),
        None,
    )
    if not section:
        raise ValueError(f"Não encontrei a entrada de {tag} no CHANGELOG.md.")
    base = f"https://github.com/{repository}"
    asset = f"{base}/releases/download/{tag}/Callas_Optimizer_Setup_x64.exe"
    return (
        f"**[Baixar instalador para Windows 11 x64 (.exe)]({asset})**\n\n"
        f"{section}\n\n"
        f"[Histórico completo de versões]({base}/blob/{tag}/CHANGELOG.md)\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("repository")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    history = Path(__file__).resolve().parents[1] / "CHANGELOG.md"
    try:
        notes = render_notes(history.read_text(encoding="utf-8"), args.tag, args.repository)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
