from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from zemberek.morphology.analysis.sentence_word_analysis import SentenceWordAnalysis


class SentenceAnalysis:

    def __init__(self, sentence: str, word_analyses: List[SentenceWordAnalysis]):
        self.sentence = sentence
        self.word_analyses = word_analyses

    def __iter__(self):
        return iter(self.word_analyses)
