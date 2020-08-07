from __future__ import annotations

import struct

from enum import Enum, auto
from typing import Dict, Set, Tuple, TYPE_CHECKING
from abc import ABC

if TYPE_CHECKING:
    from zemberek.normalization.node import Node
    from zemberek.normalization.character_graph import CharacterGraph

from zemberek.core.turkish import TurkishAlphabet


class CharacterGraphDecoder:

    DIACRITICS_IGNORING_MATCHER: 'CharacterGraphDecoder.DiacriticsIgnoringMatcher'

    def __init__(self, graph: CharacterGraph):
        self.graph = graph
        self.max_penalty = 1.0
        self.check_near_key_substitution = False

    def get_suggestions(self, input_: str, matcher: 'CharacterGraphDecoder.CharMatcher') -> Tuple[str]:
        return tuple(CharacterGraphDecoder.Decoder(matcher, self).decode(input_).keys())

    class Decoder:

        def __init__(self, matcher: 'CharacterGraphDecoder.CharMatcher', outer: 'CharacterGraphDecoder'):
            self.finished: Dict[str, float] = {}
            self.matcher = matcher
            self.outer = outer

        def decode(self, inp: str) -> Dict[str, float]:
            hyp = CharacterGraphDecoder.Hypothesis(None, self.outer.graph.root, penalty=0.0,
                                                   operation=CharacterGraphDecoder.Operation.N_A, word=None,
                                                   ending=None)
            next_: Set['CharacterGraphDecoder.Hypothesis'] = self.expand(hyp, inp)

            while True:
                new_hyps: Set['CharacterGraphDecoder.Hypothesis'] = set()
                for hypothesis in next_:
                    expand_: Set['CharacterGraphDecoder.Hypothesis'] = self.expand(hypothesis, inp)
                    new_hyps |= expand_  # updating new_hyps set with new elements of expand

                if len(new_hyps) == 0:
                    return self.finished

                next_ = new_hyps

        def expand(self, hypothesis: 'CharacterGraphDecoder.Hypothesis', inp: str) -> \
                Set['CharacterGraphDecoder.Hypothesis']:

            new_hypotheses: Set['CharacterGraphDecoder.Hypothesis'] = set()
            next_index = hypothesis.char_index + 1
            next_char = inp[next_index] if next_index < len(inp) else chr(0)
            if next_index < len(inp):
                cc = None if self.matcher is None else self.matcher.matches(next_char)
                if hypothesis.node.has_epsilon_connection():
                    child_list: Tuple[Node] = hypothesis.node.get_child_list(c=next_char) if cc is None else \
                        hypothesis.node.get_child_list(char_array=cc)

                    for child in child_list:
                        h = hypothesis.get_new_move_forward(child, 0.0, CharacterGraphDecoder.Operation.NO_ERROR)
                        h.set_word(child)
                        new_hypotheses.add(h)
                        if next_index >= len(inp) - 1 and h.node.word:
                            self.add_hypothesis(h)
                elif cc is None:
                    child: Node = hypothesis.node.get_immediate_child(next_char)
                    if child:
                        h = hypothesis.get_new_move_forward(child, 0.0, CharacterGraphDecoder.Operation.NO_ERROR)
                        h.set_word(child)
                        new_hypotheses.add(h)
                        if next_index >= len(inp) - 1 and h.node.word:
                            self.add_hypothesis(h)
                else:
                    for c in cc:
                        child: Node = hypothesis.node.get_immediate_child(c)
                        if child:
                            h = hypothesis.get_new_move_forward(child, 0.0, CharacterGraphDecoder.Operation.NO_ERROR)
                            h.set_word(child)
                            new_hypotheses.add(h)
                            if next_index >= len(inp) - 1 and h.node.word:
                                self.add_hypothesis(h)

            elif hypothesis.node.word:
                self.add_hypothesis(hypothesis)

            if hypothesis.penalty >= self.outer.max_penalty:
                return new_hypotheses
            else:
                all_child_notes = hypothesis.node.get_all_child_nodes() if hypothesis.node.has_epsilon_connection() \
                    else hypothesis.node.get_immediate_child_node_iterable()
                if next_index < len(inp):
                    for child in all_child_notes:
                        # penalty = 0.0
                        if self.outer.check_near_key_substitution:
                            # IMPLEMENT IF NEEDED
                            raise NotImplementedError("Not implemented, implement if needed")
                        else:
                            penalty = 1.0

                        if penalty > 0.0 and hypothesis.penalty + penalty <= self.outer.max_penalty:
                            h = hypothesis.get_new_move_forward(child, penalty,
                                                                CharacterGraphDecoder.Operation.SUBSTITUTION)
                            h.set_word(child)
                            if next_index == len(inp) - 1:
                                if h.node.word:
                                    self.add_hypothesis(h)
                            else:
                                new_hypotheses.add(h)

                if hypothesis.penalty + 1.0 > self.outer.max_penalty:
                    return new_hypotheses
                else:
                    new_hypotheses.add(hypothesis.get_new_move_forward(hypothesis.node, 1.0,
                                                                       CharacterGraphDecoder.Operation.DELETION))
                    for child in all_child_notes:
                        h = hypothesis.get_new(child, 1.0, CharacterGraphDecoder.Operation.INSERTION)
                        h.set_word(child)
                        new_hypotheses.add(h)

                    if len(inp) > 2 and next_index < len(inp) - 1:
                        transpose: str = inp[next_index + 1]
                        if self.matcher:
                            tt: Tuple[str] = self.matcher.matches(transpose)
                            cc: Tuple[str] = self.matcher.matches(next_char)
                            for t in tt:
                                next_nodes: Tuple[Node] = hypothesis.node.get_child_list(c=t)
                                for next_node in next_nodes:
                                    for c in cc:
                                        if hypothesis.node.has_child(t) and next_node.has_child(c):
                                            for n in next_node.get_child_list(c=c):
                                                h = hypothesis.get_new(n,
                                                                       1.0,
                                                                       CharacterGraphDecoder.Operation.TRANSPOSITION,
                                                                       index=next_index + 1)
                                                h.set_word(n)
                                                if next_index == len(inp) - 1:
                                                    if h.node.word:
                                                        self.add_hypothesis(h)
                                                else:
                                                    new_hypotheses.add(h)
                        else:
                            next_nodes: Tuple[Node] = hypothesis.node.get_child_list(c=transpose)
                            for next_node in next_nodes:
                                if hypothesis.node.has_child(transpose) and next_node.has_child(next_char):
                                    for n in next_node.get_child_list(c=next_char):
                                        h = hypothesis.get_new(n, 1.0, CharacterGraphDecoder.Operation.TRANSPOSITION,
                                                               next_index + 1)
                                        h.set_word(n)
                                        if next_index == len(inp) - 1:
                                            if h.node.word:
                                                self.add_hypothesis(h)
                                        else:
                                            new_hypotheses.add(h)
                    return new_hypotheses

        def add_hypothesis(self, hypothesis: 'CharacterGraphDecoder.Hypothesis'):
            hyp_word = hypothesis.get_content()
            if hyp_word not in self.finished.keys():
                self.finished[hyp_word] = hypothesis.penalty
            elif self.finished[hyp_word] > hypothesis.penalty:
                self.finished[hyp_word] = hypothesis.penalty

    class Hypothesis:

        def __init__(self, previous, node: Node, penalty: float,
                     operation: 'CharacterGraphDecoder.Operation', word, ending, char_index: int = -1):
            self.previous = previous  # previous: Hypothesis, word: str, ending: str
            self.node = node
            self.penalty = penalty
            self.operation = operation
            self.word = word
            self.ending = ending
            self.char_index = char_index

        @staticmethod
        def float_to_int_bits(f: float) -> int:
            s = struct.pack('>f', f)
            return struct.unpack('>l', s)[0]

        def __eq__(self, other):
            if self is other:
                return True
            elif other is not None and self.__class__ == other.__class__:
                if self.char_index != other.char_index:
                    return False
                elif self.penalty != other.penalty:
                    return False
                elif self.node != other.node:
                    return False
                else:
                    return False if self.word != other.word else (self.ending == other.ending)
            else:
                return False

        def __hash__(self):
            result = self.char_index
            result = 31 * result + hash(self.node)
            result = 31 * result + (self.float_to_int_bits(self.penalty) if self.penalty != 0.0 else 0)
            result = 31 * result + (hash(self.word) if self.word is not None else 0)
            result = 31 * result + (hash(self.ending) if self.ending is not None else 0)
            return result

        def get_new(self, node: Node, penalty_to_add: float, op: 'CharacterGraphDecoder.Operation',
                    index: int = None) -> 'CharacterGraphDecoder.Hypothesis':
            char_index = self.char_index if index is None else index
            return CharacterGraphDecoder.Hypothesis(self, node, self.penalty + penalty_to_add, op, self.word,
                                                    self.ending, char_index=char_index)

        def get_new_move_forward(self, node: Node, penalty_to_add: float, op: 'CharacterGraphDecoder.Operation') -> \
                'CharacterGraphDecoder.Hypothesis':
            return CharacterGraphDecoder.Hypothesis(self, node, self.penalty + penalty_to_add, op, self.word,
                                                    self.ending, char_index=self.char_index + 1)

        def get_content(self):
            w = "" if self.word is None else self.word
            e = "" if self.ending is None else self.ending
            return w + e

        def set_word(self, node: Node):
            if node.word:
                if node.type_ == 1:
                    self.word = node.word
                elif node.type_ == 2:
                    self.ending = node.word

    class CharMatcher(ABC):
        def matches(self, var1: str) -> Tuple[str, ...]:
            raise NotImplementedError

    class DiacriticsIgnoringMatcher(CharMatcher):
        map_: Dict[int, Tuple[str, ...]] = {}

        def __init__(self):
            all_letters = TurkishAlphabet.INSTANCE.all_letters + "+.,'-"

            for c in all_letters:
                self.map_[ord(c)] = (c,)

            self.map_[99] = (u'c', u'ç')
            self.map_[103] = (u'g', u'ğ')
            self.map_[305] = (u'ı', u'i')
            self.map_[105] = (u'ı', u'i')
            self.map_[111] = (u'o', u'ö')
            self.map_[115] = (u's', u'ş')
            self.map_[117] = (u'u', u'ü')
            self.map_[97] = (u'a', u'â')
            self.map_[105] = (u'i', u'î')
            self.map_[117] = (u'u', u'û')
            self.map_[67] = (u'C', u'Ç')
            self.map_[71] = (u'G', u'Ğ')
            self.map_[73] = (u'I', u'İ')
            self.map_[304] = (u'İ', u'I')
            self.map_[79] = (u'O', u'Ö')
            self.map_[214] = (u'Ö', u'Ş')
            self.map_[85] = (u'U', u'Ü')
            self.map_[65] = (u'A', u'Â')
            self.map_[304] = (u'İ', u'Î')
            self.map_[85] = (u'U', u'Û')

        def matches(self, c: str) -> Tuple[str, ...]:
            res = self.map_.get(ord(c))
            return (c,) if res is None else res

    class Operation(Enum):
        NO_ERROR = auto()
        INSERTION = auto()
        DELETION = auto()
        SUBSTITUTION = auto()
        TRANSPOSITION = auto()
        N_A = auto()


CharacterGraphDecoder.DIACRITICS_IGNORING_MATCHER = CharacterGraphDecoder.DiacriticsIgnoringMatcher()
