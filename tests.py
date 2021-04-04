import logging
from pathlib import Path
import tempfile
import unittest
import zipfile

import anki
import bs4 as bs

from srt_to_anki.srt_to_anki import Card
from srt_to_anki.srt_to_anki import get_words_from_srt_file
from srt_to_anki.srt_to_anki import make_anki_deck_from_srt_file
from srt_to_anki.srt_to_anki import make_card_from_word
from srt_to_anki.srt_to_anki import make_cards_from_srt_file
from srt_to_anki.srt_to_anki import parse_srt_file


class TestSrtParser(unittest.TestCase):
    TEST_SRT_PATH = Path("test.srt").absolute()
    EXPECTED_CARDS = [
        Card('七', '【しち】: seven, hepta-'),
        Card('俺', '【おれ】: I'),
        Card('傷つける', "【きずつける】: to wound, to hurt someone's feelings (pride, etc.), to damage"),
        Card('誰', '【だれ】: who'),
        Card('諦める', '【あきらめる】: to give up'),
        Card('大罪', '【だいざい】: serious crime, Mortal sin'),
    ]

    def test_srt_parsing(self):
        rows = parse_srt_file(self.TEST_SRT_PATH)
        self.assertEqual(len(rows), 4)

    def test_get_words_from_srt(self):
        expected_words = ["誰", "傷つけ",  "諦", "俺",  "七", "大罪"]
        actual_words = get_words_from_srt_file(self.TEST_SRT_PATH)

        for word in expected_words:
            self.assertIn(word, actual_words)

    def test_make_card_from_word(self):
        word = "誰"
        card = make_card_from_word(word)
        self.assertEqual(card.front, word)
        self.assertEqual(card.back, "【だれ】: who")

    def test_make_cards_from_srt_file(self):
        actual_cards = make_cards_from_srt_file(self.TEST_SRT_PATH)

        self.assertEqual(set(self.EXPECTED_CARDS), set(actual_cards))

    def test_make_anki_deck_from_srt_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            apkg_path = make_anki_deck_from_srt_file(
                self.TEST_SRT_PATH,
                name="test",
                output_dir=Path(tmpdir)
            )
            self.assertTrue(apkg_path.is_file())

            with zipfile.ZipFile(apkg_path) as zip:
                zip.extractall(tmpdir)

            anki2_path = Path(tmpdir) / "collection.anki2"
            collection = anki.Collection(str(anki2_path))
            anki_cards = [
                collection.getCard(card_id)
                for card_id in collection.findCards("")
            ]

            self.assertEqual(len(anki_cards), 6)

            anki_cards_as_text = [get_anki_card_as_text(card) for card in anki_cards]
            self.assertEqual(
                {f"{card.front}{card.back}" for card in self.EXPECTED_CARDS},
                set(anki_cards_as_text)
            )


def get_anki_card_as_text(card: anki.cards.Card) -> str:
    front = html_to_raw_text(card.question())
    back = html_to_raw_text(card.answer())
    return f"{front}{back}"


def html_to_raw_text(html: str) -> str:
    soup = bs.BeautifulSoup(html, features="lxml")
    return soup.text
