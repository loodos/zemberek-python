from __future__ import annotations
from copy import deepcopy
from typing import List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.morphotactics.morpheme_state import MorphemeState
    from zemberek.morphology.morphotactics.stem_transition import StemTransition

from zemberek.core.turkish import PhoneticAttribute
from zemberek.morphology.analysis.surface_transitions import SurfaceTransition


class SearchPath:

    def __init__(self, tail: str, current_state: MorphemeState, transitions: List[SurfaceTransition],
                 phonetic_attributes: Set[PhoneticAttribute], terminal: bool):
        self.tail = tail
        self.current_state = current_state
        self.transitions = transitions
        self.phonetic_attributes = phonetic_attributes
        self.terminal = terminal

        self.contains_derivation = False
        self.contains_suffix_with_surface = False

    def has_dictionary_item(self, item) -> bool:
        return item == self.get_stem_transition().item

    def contains_suffix_with_surface_(self):
        return self.contains_suffix_with_surface

    def get_stem_transition(self):
        return self.transitions[0].lexical_transition

    def get_last_transition(self) -> SurfaceTransition:
        return self.transitions[-1]

    def get_dictionary_item(self):
        return self.get_stem_transition().item

    def get_previous_state(self) -> MorphemeState:
        return None if len(self.transitions) < 2 else self.transitions[len(self.transitions) - 2].get_state()

    def get_copy_for_generation(self, surface_node: SurfaceTransition, phonetic_attributes: Set[PhoneticAttribute]) -> \
            'SearchPath':
        is_terminal = surface_node.get_state().terminal_
        hist: List[SurfaceTransition] = list(self.transitions)
        hist.append(surface_node)
        path = SearchPath(self.tail, surface_node.get_state(), hist, phonetic_attributes, is_terminal)
        path.contains_suffix_with_surface = self.contains_suffix_with_surface or len(surface_node.surface) != 0
        path.contains_derivation = self.contains_derivation or surface_node.get_state().derivative
        return path

    def get_copy(self, surface_node: SurfaceTransition, phonetic_attributes: Set[PhoneticAttribute]) -> 'SearchPath':
        is_terminal = surface_node.get_state().terminal_
        hist: List[SurfaceTransition] = self.transitions + [surface_node]
        new_tail = self.tail[len(surface_node.surface):]
        path: 'SearchPath' = SearchPath(new_tail, surface_node.get_state(), hist, phonetic_attributes, is_terminal)
        path.contains_suffix_with_surface = self.contains_suffix_with_surface or len(surface_node.surface) != 0
        path.contains_derivation = self.contains_derivation or surface_node.get_state().derivative
        return path

    @staticmethod
    def initial_path(stem_transition: StemTransition, tail: str) -> 'SearchPath':
        morphemes: List[SurfaceTransition] = []
        root = SurfaceTransition(stem_transition.surface, stem_transition)
        morphemes.append(root)
        return SearchPath(tail, stem_transition.to, morphemes, deepcopy(stem_transition.phonetic_attributes),
                          stem_transition.to.terminal_)

    def __str__(self):
        st = self.get_stem_transition()
        morpheme_str = " + ".join(str(s) for s in self.transitions)
        return "[(" + st.item.id_ + ")(-" + self.tail + ") " + morpheme_str + "]"
