import logging
import re

from pkg_resources import resource_filename
from typing import Dict, List

from zemberek.core.turkish import TurkishSyllableExtractor, TurkishAlphabet
from zemberek.morphology.analysis.tr.turkish_numbers import TurkishNumbers

logger = logging.getLogger(__name__)


def load_map(resource: str) -> Dict[str, str]:
    d: Dict[str, str] = {}

    with open(resource, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("##"):
                continue
            key, value = line.split("=")
            d[key.strip()] = value.strip()

    return d


class PronunciationGuesser:
    alphabet = TurkishAlphabet.INSTANCE

    turkish_letter_prons: Dict[str, str] = load_map(
        resource_filename("zemberek", "resources/phonetics/turkish-letter-names.txt"))
    english_letter_prons: Dict[str, str] = load_map(
        resource_filename("zemberek", "resources/phonetics/english-letter-names.txt"))
    english_phones_to_turkish: Dict[str, str] = load_map(
        resource_filename("zemberek", "resources/phonetics/english-phones-to-turkish.txt"))
    extractor_for_abbrv: TurkishSyllableExtractor = TurkishSyllableExtractor.STRICT

    def to_turkish_letter_pronunciations(self, w: str) -> str:
        if self.alphabet.contains_digit(w):
            return self.to_turkish_letter_pronunciation_with_digit(w)
        else:
            sb = []

            for i, c in enumerate(w):
                if c != '-':
                    if c in self.turkish_letter_prons.keys():
                        if i == len(w) - 1 and c == "k":
                            sb.append("ka")
                        else:
                            sb.append(self.turkish_letter_prons.get(c))
                    else:
                        logger.debug("Cannot guess pronunciation of letter [" + c + "] in :[" + w + "]")
            return ''.join(sb)

    def to_turkish_letter_pronunciation_with_digit(self, w: str) -> str:
        pieces: List[str] = TurkishNumbers.separate_numbers(w)
        sb = []

        for i, piece in enumerate(pieces):
            if self.alphabet.contains_digit(piece):
                sb.append(TurkishNumbers.convert_number_to_string(piece))
            else:
                if i < len(pieces) - 1:
                    sb.append(self.to_turkish_letter_pronunciations(piece))
                else:
                    sb.append(self.replace_english_specific_chars(piece))
        return re.sub("[ ]+", "", ''.join(sb))

    @staticmethod
    def replace_english_specific_chars(w: str) -> str:
        sb = []
        for c in w:
            if c == '\'' or c == '-':
                continue
            elif c == 'q':
                sb.append("k")
            elif c == 'w':
                sb.append("v")
            elif c == 'x':
                sb.append("ks")
            else:
                sb.append(c)
        return ''.join(sb)
