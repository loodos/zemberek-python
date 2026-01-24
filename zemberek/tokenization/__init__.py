import sys

# antlr4 imports typing.io to use TextIO; typing.io was removed in Python 3.12
# Therefore a compatibility shim is needed
if sys.version_info >= (3, 12):
    import typing

    typing.io = typing
    sys.modules.setdefault("typing.io", typing)

from .turkish_tokenizer import TurkishTokenizer
from .turkish_sentence_extractor import TurkishSentenceExtractor
