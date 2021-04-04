import argparse
import logging
from pathlib import Path

from .srt_to_anki import make_anki_deck_from_srt_file


def main(srt_file: Path, *, output_name: str, output_dir: Path) -> None:
    logging.basicConfig(level=logging.INFO)
    make_anki_deck_from_srt_file(srt_file, name=output_name, output_dir=output_dir)


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--name", required=True, type=str)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("srt", type=Path)

    return parser
