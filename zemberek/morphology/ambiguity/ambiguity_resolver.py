from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.analysis.sentence_analysis import SentenceAnalysis
    from zemberek.morphology.analysis.word_analysis import WordAnalysis


class AmbiguityResolver:

    def disambiguate(self, sentence: str, all_analyses: List[WordAnalysis]) -> SentenceAnalysis:
        raise NotImplementedError()
