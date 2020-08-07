from __future__ import annotations
from typing import Tuple, FrozenSet, TYPE_CHECKING
from pkg_resources import resource_filename

if TYPE_CHECKING:
    from zemberek.morphology import TurkishMorphology
    from zemberek.normalization.node import Node

from zemberek.core.turkish import PrimaryPos
from zemberek.normalization.character_graph import CharacterGraph


class StemEndingGraph:

    def __init__(self, morphology: TurkishMorphology):
        self.morphology = morphology
        endings = self.load_lines_from_resource()
        self.ending_graph: CharacterGraph = self.generate_ending_graph(endings)
        self.stem_graph: CharacterGraph = self.generate_stem_graph()
        stem_word_nodes: FrozenSet[Node] = frozenset(self.stem_graph.get_all_nodes())
        for node in stem_word_nodes:
            node.connect_epsilon(self.ending_graph.root)

    @staticmethod
    def load_lines_from_resource(path: str = None) -> Tuple[str]:
        if not path:
            path = resource_filename("zemberek", "resources/normalization/endings.txt")
        with open(path, 'r', encoding='utf-8') as f:
            lines = tuple(line.replace('\n', "") for line in f.readlines())
        return lines

    def generate_stem_graph(self) -> CharacterGraph:
        stem_graph = CharacterGraph()
        stem_transitions = self.morphology.morphotactics.stem_transitions

        for transition in stem_transitions.get_transitions():
            if len(transition.surface) != 0 and transition.item.primary_pos != PrimaryPos.Punctuation:
                stem_graph.add_word(transition.surface, type_=1)

        return stem_graph

    @staticmethod
    def generate_ending_graph(endings: Tuple[str]) -> CharacterGraph:
        graph = CharacterGraph()

        for ending in endings:
            graph.add_word(ending, type_=2)

        return graph
