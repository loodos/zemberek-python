from .morphology import TurkishMorphology
from .normalization import TurkishSentenceNormalizer, TurkishSpellChecker
from .tokenization import TurkishSentenceExtractor, TurkishTokenizer

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\nMsg: %(message)s\n')
handler.setFormatter(formatter)
root.addHandler(handler)

