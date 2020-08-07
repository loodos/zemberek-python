from typing import Union

from zemberek.core.turkish.turkish_alphabet import TurkishAlphabet


class TurkishSyllableExtractor:

    STRICT: Union['TurkishSyllableExtractor', None] = None

    def __init__(self, strict: bool):
        self.alphabet = TurkishAlphabet.INSTANCE
        self.strict = strict


TurkishSyllableExtractor.STRICT = TurkishSyllableExtractor(strict=True)
