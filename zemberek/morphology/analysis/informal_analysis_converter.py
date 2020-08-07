from __future__ import annotations
from typing import Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..analysis.single_analysis import SingleAnalysis

from zemberek.morphology.generator import WordGenerator


class InformalAnalysisConverter:
    def __init__(self, generator: WordGenerator):
        self.generator = generator

    def convert(self, inp: str, a: SingleAnalysis) -> Union[WordGenerator.Result, None]:
        if not a.contains_informal_morpheme():
            return WordGenerator.Result(inp, a)

        formal_morphemes = self.to_formal_morpheme_names(a)
        generations: Tuple[WordGenerator.Result] = self.generator.generate(item=a.item, morphemes=formal_morphemes)
        if len(generations) > 0:
            return generations[0]
        else:
            return None

    @staticmethod
    def to_formal_morpheme_names(a: SingleAnalysis):  # -> Tuple[Morpheme]
        transform = []  # List[Morpheme]
        for m in a.get_morphemes():
            if m.informal and m.mapped_morpheme:
                transform.append(m.mapped_morpheme)
            else:
                transform.append(m)
        return tuple(transform)
