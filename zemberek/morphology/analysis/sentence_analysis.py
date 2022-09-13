from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from zemberek.morphology.analysis.sentence_word_analysis import SentenceWordAnalysis
    from zemberek.morphology.analysis.single_analysis import SingleAnalysis


class SentenceAnalysis:

    def __init__(self, sentence: str, word_analyses: List[SentenceWordAnalysis]):
        self.sentence = sentence
        self.word_analyses = word_analyses

    def __iter__(self):
        return iter(self.word_analyses)

    def __len__(self):
        return len(self.word_analyses)

    def __getitem__(self, item) -> 'SentenceWordAnalysis':
        return self.word_analyses[item]

    def best_analysis(self) -> List[SingleAnalysis]:
        return [s.best_analysis for s in self.word_analyses]
