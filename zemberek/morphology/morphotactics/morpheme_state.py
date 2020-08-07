from __future__ import annotations

import logging

from typing import List, Union,Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.morphotactics.morpheme import Morpheme

from zemberek.morphology.morphotactics.conditions import Conditions
from zemberek.morphology.morphotactics.morpheme_transition import MorphemeTransition
from zemberek.morphology.morphotactics.suffix_transition import SuffixTransition

logger = logging.getLogger(__name__)


class MorphemeState:

    def __init__(self, id_: str, morpheme: Morpheme, terminal: bool, derivative: bool, pos_root: bool):
        self.id_ = id_
        self.morpheme = morpheme
        self.terminal_ = terminal
        self.derivative = derivative
        self.pos_root = pos_root
        self.outgoing: List[Union[SuffixTransition, MorphemeTransition]] = []
        self.incoming: List[Union[SuffixTransition, MorphemeTransition]] = []

    def __str__(self):
        return "[" + self.id_ + ":" + self.morpheme.id_ + "]"

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, MorphemeState):
            return self.id_ == other.id_
        else:
            return False

    def __hash__(self):
        return hash(self.id_)

    @staticmethod
    def builder(_id: str, morpheme: Morpheme, pos_root: bool = False):
        return MorphemeState.Builder(_id, morpheme, _pos_root=pos_root)

    @staticmethod
    def terminal(_id: str, morpheme: Morpheme, pos_root: bool = False) -> 'MorphemeState':
        return MorphemeState.Builder(_id, morpheme, _pos_root=pos_root, _terminal=True).build()

    @staticmethod
    def non_terminal(_id: str, morpheme: Morpheme, pos_root: bool = False) -> 'MorphemeState':
        return MorphemeState.Builder(_id, morpheme, _pos_root=pos_root).build()

    @staticmethod
    def terminal_derivative(_id: str, morpheme: Morpheme, pos_root: bool = False) -> 'MorphemeState':
        return MorphemeState.Builder(_id, morpheme, _pos_root=pos_root, _terminal=True, _derivative=True).build()

    @staticmethod
    def non_terminal_derivative(_id: str, morpheme: Morpheme, pos_root: bool = False) -> 'MorphemeState':
        return MorphemeState.Builder(_id, morpheme, _pos_root=pos_root, _derivative=True).build()

    def add_(self, to: 'MorphemeState', template: str, condition: Conditions.Condition = None) -> 'MorphemeState':
        if condition:
            SuffixTransition.Builder(from_=self, to=to, surface_template=template, condition=condition).build()
        else:
            SuffixTransition.Builder(from_=self, to=to, surface_template=template).build()
        return self

    def add_empty(self, to: 'MorphemeState', condition: Conditions.Condition = None) -> 'MorphemeState':
        if condition:
            SuffixTransition.Builder(from_=self, to=to, condition=condition).build()
        else:
            SuffixTransition.Builder(from_=self, to=to).build()
        return self

    def copy_outgoing_transitions_from(self, state: 'MorphemeState'):
        for transition in state.outgoing:
            copy = transition.get_copy()
            copy.from_ = self
            self.add_outgoing((transition,))

    def add_outgoing(self, suffix_transitions: Tuple[MorphemeTransition, ...]) -> 'MorphemeState':
        for suffix_transition in suffix_transitions:
            if suffix_transition in self.outgoing:
                logger.debug(f"Outgoing transition already exists{str(suffix_transition)}")

            self.outgoing.append(suffix_transition)
        return self

    def add_incoming(self, suffix_transitions: Tuple[MorphemeTransition, ...]) -> 'MorphemeState':
        for suffix_transition in suffix_transitions:
            if suffix_transition in self.incoming:
                logger.debug(f"Incoming transition already exists{str(suffix_transition)}")

            self.incoming.append(suffix_transition)
        return self

    def remove_transitions_to(self, morpheme: Morpheme):
        transitions: List[MorphemeTransition] = []
        for transition in self.outgoing:
            if transition.to.morpheme == morpheme:
                transitions.append(transition)

        for item in transitions:
            self.outgoing.remove(item)

    class Builder:

        def __init__(self, _id: str, _morpheme: Morpheme, _terminal: bool = False, _derivative: bool = False,
                     _pos_root: bool = False):
            self._id = _id
            self._morpheme = _morpheme
            self._terminal = _terminal
            self._derivative = _derivative
            self._pos_root = _pos_root

        def build(self):
            return MorphemeState(self._id, self._morpheme, self._terminal, self._derivative, self._pos_root)
