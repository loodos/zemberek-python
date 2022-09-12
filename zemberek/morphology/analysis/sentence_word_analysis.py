from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.analysis.single_analysis import SingleAnalysis
    from zemberek.morphology.analysis.word_analysis import WordAnalysis


class SentenceWordAnalysis:

    def __init__(self, best_analysis: 'SingleAnalysis', word_analysis: 'WordAnalysis'):
        self.best_analysis = best_analysis
        self.word_analysis = word_analysis
