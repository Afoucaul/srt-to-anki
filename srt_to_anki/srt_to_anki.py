from typing import Any, Dict, List, Optional, Tuple

import argparse
import dataclasses as dc
import logging
from multiprocessing import dummy as mp_dummy
from pathlib import Path

import genanki
import nagisa
import regex as re
import requests


LOGGER = logging.getLogger("srt_parser")
LOGGER.setLevel(logging.INFO)


@dc.dataclass
class Card:
    front: str
    back: str

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Card)
            and self.front == other.front
            and self.back == other.back
        )

    def __hash__(self) -> int:
        return hash(self.front)


def make_anki_deck_from_srt_file(
    srt_file: Path, *, name: str, output_dir: Path
) -> Path:
    srt_file = srt_file.absolute()
    deck = genanki.Deck(1, name)
    model = genanki.Model(
        1,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": "{{Answer}}",
            }
        ],
    )

    cards = make_cards_from_srt_file(srt_file)
    for card in cards:
        note = genanki.Note(model=model, fields=[card.front, card.back])
        deck.add_note(note)

    output_path = (output_dir / f"{name}.apkg").absolute()
    genanki.Package(deck).write_to_file(output_path)

    return output_path


def make_cards_from_srt_file(srt_file: Path) -> List[Card]:
    words = get_words_from_srt_file(srt_file)
    with mp_dummy.Pool(20) as pool:
        cards = pool.map(make_card_from_word, words)

    return [card for card in cards if card is not None]


def get_words_from_srt_file(srt_path: Path) -> List[str]:
    raw_text = "\n".join(parse_srt_file(srt_path))
    segments = [
        segment
        for segment in nagisa.wakati(raw_text)
        if re.match(r"^\p{Han}[\p{Han}\p{Hiragana}\p{Katakana}]*$", segment)
    ]
    return segments


def make_card_from_word(word: str) -> Optional[Card]:
    LOGGER.info("Making card for word %s", word)

    try:
        jisho_data = search_word_on_jisho(word)

        front = jisho_data["japanese"][0]["word"]
        back = "【{kana}】: {senses}".format(
            kana=jisho_data["japanese"][0]["reading"],
            senses=", ".join(
                sense["english_definitions"][0] for sense in jisho_data["senses"]
            ),
        )

        return Card(front, back)

    except:
        return None


def search_word_on_jisho(word: str) -> Dict[Any, Any]:
    return requests.get(
        "https://jisho.org/api/v1/search/words", params={"keyword": word}
    ).json()["data"][0]


def parse_srt_file(srt_path: Path) -> List[str]:
    with open(srt_path, "r") as fd:
        text = fd.read()

    rows = []
    blocks = text.split("\n\n")
    for block in blocks:
        if re.match(r"^\s*$", block):
            continue

        block_rows = [row for row in block.split("\n") if not re.match(r"^\s*$", row)]
        rows.extend(block_rows[2:])

    return rows


def main(srt_file: Path, *, output_name: str, output_dir: Path) -> None:
    logging.basicConfig(level=logging.INFO)
    make_anki_deck_from_srt_file(srt_file, name=output_name, output_dir=output_dir)


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--name", required=True, type=str)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("srt", type=Path)

    return parser


if __name__ == "__main__":
    argparser = make_argparser()
    args = argparser.parse_args()
    main(srt_file=args.srt, output_name=args.name, output_dir=args.output_dir)
