from .morphology import TurkishMorphology
from .normalization import TurkishSentenceNormalizer, TurkishSpellChecker
from .tokenization import TurkishSentenceExtractor

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.ERROR)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\nMsg: %(message)s\n')
handler.setFormatter(formatter)
root.addHandler(handler)

