from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
from abc import ABC

if TYPE_CHECKING:
    from zemberek.core.turkish import SecondaryPos, RootAttribute, PhoneticAttribute
    from zemberek.morphology.lexicon import DictionaryItem
    from zemberek.morphology.analysis.search_path import SearchPath
    from zemberek.morphology.morphotactics.morpheme import Morpheme
    from zemberek.morphology.morphotactics.morpheme_state import MorphemeState

from zemberek.morphology.morphotactics.operator import Operator


class Conditions(ABC):
    HAS_TAIL = None
    HAS_SURFACE = None
    HAS_NO_SURFACE = None
    CURRENT_GROUP_EMPTY = None

    @staticmethod
    def not_(condition):
        return Conditions.NotCondition(condition)

    @staticmethod
    def not_have(p_attribute: PhoneticAttribute = None, r_attribute: RootAttribute = None) -> 'Conditions.Condition':
        if r_attribute:
            return Conditions.HasRootAttribute(r_attribute).not_()
        return Conditions.HasPhoneticAttribute(p_attribute).not_()

    @staticmethod
    def condition(operator: Operator, left: 'Conditions.Condition', right: 'Conditions.Condition') -> \
            'Conditions.Condition':
        return Conditions.CombinedCondition.of(operator, left, right)

    @staticmethod
    def and_(left: 'Conditions.Condition', right: 'Conditions.Condition'):
        return Conditions.condition(Operator.AND, left, right)

    @staticmethod
    def root_is(item: DictionaryItem) -> 'Conditions.Condition':
        return Conditions.DictionaryItemIs(item)

    @staticmethod
    def root_is_not(item: DictionaryItem) -> 'Conditions.Condition':
        return Conditions.DictionaryItemIs(item).not_()

    @staticmethod
    def root_is_any(items: Tuple[DictionaryItem, ...]) -> 'Conditions.Condition':
        return Conditions.DictionaryItemIsAny(items)

    @staticmethod
    def root_is_none(items: Tuple[DictionaryItem, ...]) -> 'Conditions.Condition':
        return Conditions.DictionaryItemIsNone(items)

    @staticmethod
    def has(r_attribute: RootAttribute = None, p_attribute: PhoneticAttribute = None) -> 'Conditions.Condition':
        if p_attribute:
            return Conditions.HasPhoneticAttribute(p_attribute)
        return Conditions.HasRootAttribute(r_attribute)

    @staticmethod
    def or_(left: 'Conditions.Condition', right: 'Conditions.Condition') -> 'Conditions.Condition':
        return Conditions.condition(Operator.OR, left, right)

    @staticmethod
    def prvious_morpheme_is(morpheme: Morpheme) -> 'Conditions.Condition':
        return Conditions.PreviousMorphemeIs(morpheme)

    @staticmethod
    def previous_morpheme_is_not(morpheme: Morpheme) -> 'Conditions.Condition':
        return Conditions.PreviousMorphemeIs(morpheme).not_()

    @staticmethod
    def previous_state_is(state) -> 'Conditions.Condition':  # state: MorphemeState
        return Conditions.PreviousStateIs(state)

    @staticmethod
    def previous_state_is_not(state) -> 'Conditions.Condition':  # state: MorphemeState
        return Conditions.PreviousStateIsNot(state)

    @staticmethod
    def last_derivation_is(state) -> 'Conditions.Condition':  # state: MorphemeState
        return Conditions.LastDerivationIs(state)

    class Condition(ABC):

        def not_(self):
            raise NotImplementedError

        def and_(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            raise NotImplementedError

        def or_(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            raise NotImplementedError

        def and_not(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            raise NotImplementedError

        def accept_(self, path: SearchPath) -> bool:
            raise NotImplementedError
    
    class AbstractCondition(Condition):

        def not_(self) -> 'Conditions.Condition':
            return Conditions.not_(self)

        def and_(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            return Conditions.and_(self, other)

        def or_(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            return Conditions.or_(self, other)

        def and_not(self, other: 'Conditions.Condition') -> 'Conditions.Condition':
            return self.and_(other.not_())

        def accept_(self, path: SearchPath) -> bool:
            raise NotImplementedError

    class HasPhoneticAttribute(AbstractCondition):
        def __init__(self, attribute: PhoneticAttribute):
            super().__init__()
            self.attribute = attribute

        def accept_(self, visitor: SearchPath) -> bool:
            return self.attribute in visitor.phonetic_attributes

        def __str__(self):
            return "HasPhoneticAttribute{" + self.attribute.name + '}'

    class NotCondition(AbstractCondition):
        def __init__(self, condition: 'Conditions.Condition'):
            super().__init__()
            self.condition = condition

        def accept_(self, visitor: SearchPath) -> bool:
            return not self.condition.accept_(visitor)

        def __str__(self):
            return "Not(" + str(self.condition) + ")"

    class CombinedCondition(AbstractCondition):

        def __init__(self, operator: Operator, left: 'Conditions.Condition', right: 'Conditions.Condition'):
            super().__init__()
            self.operator = operator
            self.conditions = []

            self.add_(operator, left)
            self.add_(operator, right)

        @classmethod
        def convert_to_combined(cls, obj) -> 'Conditions.CombinedCondition':
            obj.__class__ = Conditions.CombinedCondition
            return obj

        def add_(self, op: Operator, condition: 'Conditions.Condition') -> 'Conditions.CombinedCondition':
            if isinstance(condition, Conditions.CombinedCondition):
                combined_condition = Conditions.CombinedCondition.convert_to_combined(condition)
                if combined_condition.operator == op:
                    self.conditions.extend(combined_condition.conditions)
                else:
                    self.conditions.append(condition)
            else:
                if condition is None:
                    raise ValueError("The argument 'conditions' must not contain none")
                self.conditions.append(condition)

            return self

        @staticmethod
        def of(operator: Operator, left: 'Conditions.Condition', right: 'Conditions.Condition') -> \
                'Conditions.Condition':
            return Conditions.CombinedCondition(operator, left, right)

        def count(self) -> int:
            if len(self.conditions) == 0:
                return 0
            elif len(self.conditions) == 1:
                first = self.conditions[0]
                return Conditions.CombinedCondition.convert_to_combined(first).count() if \
                    isinstance(first, Conditions.CombinedCondition) else 1
            else:
                cnt = 0
                for condition in self.conditions:
                    if isinstance(condition, Conditions.CombinedCondition):
                        cnt += Conditions.CombinedCondition.convert_to_combined(condition).count()
                    else:
                        cnt += 1

                return cnt

        def accept_(self, path: SearchPath) -> bool:
            if len(self.conditions) == 0:
                return True
            elif len(self.conditions) == 1:
                return self.conditions[0].accept_(path)
            else:
                if self.operator == Operator.AND:
                    for condition in self.conditions:
                        if not condition.accept_(path):
                            return False
                    return True
                else:
                    for condition in self.conditions:
                        if condition.accept_(path):
                            return True
                    return False

        def __str__(self):
            if len(self.conditions) == 0:
                return "[No-Condition]"
            elif len(self.conditions) == 1:
                return str(self.conditions[0])
            else:
                string = ""
                i = 0
                if self.operator == Operator.AND:
                    for condition in self.conditions:
                        string += str(condition)
                        if i < len(self.conditions) - 1:
                            string += " AND "
                        i += 1
            return string

    class CurrentGroupContainsAny(AbstractCondition):
        def __init__(self, states: Tuple[MorphemeState, ...]):  # states: Tuple[MorphemeState]
            self.states = set(states)

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            for sf in reversed(suffixes[1:]):
                if sf.get_state() in self.states:
                    return True
                if sf.get_state().derivative:
                    return False

            return False

        def __str__(self):
            return "CurrentGroupContainsAny{" + str(self.states) + "}"

    class DictionaryItemIsAny(AbstractCondition):
        def __init__(self, items: Tuple[DictionaryItem, ...]):
            self.items = set(items)

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.get_dictionary_item() in self.items

        def __str__(self):
            return "DictionaryItemIsAny{" + str(self.items) + "}"

    class HasRootAttribute(AbstractCondition):
        def __init__(self, attribute: RootAttribute):
            self.attribute = attribute

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.get_dictionary_item().has_attribute(self.attribute)

        def __str__(self):
            return "HasRootAttribute{" + self.attribute.name + "}"

    class LastDerivationIs(AbstractCondition):
        def __init__(self, state):  # state: MorphemeState
            self.state = state

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            for sf in reversed(suffixes[1:]):
                if sf.get_state().derivative:
                    return sf.get_state() == self.state
            return False

        def __str__(self):
            return "LastDerivationIs{" + str(self.state) + "}"

    class LastDerivationIsAny(AbstractCondition):
        def __init__(self, states: Tuple[MorphemeState, ...]):  # states: Tuple[MorphemeState]
            self.states = set(states)

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            for sf in reversed(suffixes[1:]):
                if sf.get_state().derivative:
                    return sf.get_state() in self.states
            return False

        def __str__(self):
            return "LastDerivationIsAny{" + str(self.states) + "}"

    class HasAnySuffixSurface(AbstractCondition):
        def __init__(self):
            pass

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.contains_suffix_with_surface_()

        def __str__(self):
            return "HasAnySuffixSurface{}"

    class PreviousMorphemeIs(AbstractCondition):
        def __init__(self, morpheme: Morpheme):
            self.morpheme = morpheme

        def accept_(self, visitor: SearchPath) -> bool:
            previous_state = visitor.get_previous_state()
            return previous_state is not None and previous_state.morpheme == self.morpheme

        def __str__(self):
            return "PreviousMorphemeIs{" + str(self.morpheme) + "}"

    class HasTail(AbstractCondition):
        def __init__(self):
            pass

        def accept_(self, visitor: SearchPath) -> bool:
            return len(visitor.tail) != 0

        def __str__(self):
            return "HasTail{}"

    class ContainsMorpheme(AbstractCondition):
        def __init__(self, morphemes: Tuple[Morpheme, ...]):
            self.morphemes = set(morphemes)

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            for suffix in suffixes:
                if suffix.get_state().morpheme in self.morphemes:
                    return True
            return False

        def __str__(self):
            return "ContainsMorpheme{" + str(self.morphemes) + "}"

    class PreviousStateIs(AbstractCondition):
        def __init__(self, state):  # state: MorphemeState
            self.state = state

        def accept_(self, visitor: SearchPath) -> bool:
            previous_state = visitor.get_previous_state()
            return previous_state is not None and previous_state == self.state

        def __str__(self):
            return "PreviousStateIs{" + str(self.state) + "}"

    class PreviousStateIsNot(AbstractCondition):
        def __init__(self, state):  # state: MorphemeState
            self.state = state

        def accept_(self, visitor: SearchPath) -> bool:
            previous_state = visitor.get_previous_state()
            return previous_state is None or not previous_state == self.state

        def __str__(self):
            return "PreviousStateIsNot{" + str(self.state) + "}"

    class PreviousStateIsAny(AbstractCondition):
        def __init__(self, states: Tuple[MorphemeState, ...]):  # state: MorphemeState
            self.states = set(states)

        def accept_(self, visitor: SearchPath) -> bool:
            previous_state = visitor.get_previous_state()
            return previous_state is not None and previous_state in self.states

        def __str__(self):
            return "PreviousStateIsAny{}"

    class RootSurfaceIs(AbstractCondition):
        def __init__(self, surface: str):
            self.surface = surface

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.get_stem_transition().surface == self.surface

        def __str__(self):
            return "RootSurfaceIs§{" + self.surface + "}"

    class RootSurfaceIsAny(AbstractCondition):
        def __init__(self, surfaces: Tuple[str, ...]):
            self.surfaces = surfaces

        def accept_(self, visitor: SearchPath) -> bool:
            for s in self.surfaces:
                if visitor.get_stem_transition().surface == s:
                    return True
            return False

        def __str__(self):
            return "RootSurfaceIsAny{" + str(self.surfaces) + "}"

    class PreviousMorphemeIsAny(AbstractCondition):
        def __init__(self, morphemes: Tuple[Morpheme, ...]):
            self.morphemes = morphemes

        def accept_(self, visitor: SearchPath) -> bool:
            previous_state = visitor.get_previous_state()
            return previous_state is not None and previous_state.morpheme in self.morphemes

        def __str__(self):
            return "PreviousMorphemeIsAny{" + str(self.morphemes) + "}"

    class PreviousGroupContains(AbstractCondition):
        def __init__(self, states: Tuple[MorphemeState, ...]):  # state: MorphemeState
            self.states = states

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            last_index = len(suffixes) - 1

            sf = suffixes[last_index]
            while not sf.get_state().derivative:
                if last_index == 0:
                    return False
                last_index -= 1
                sf = suffixes[last_index]

            for i in range(last_index - 1, 0, -1):
                sf = suffixes[i]
                if sf.get_state() in self.states:
                    return True

                if sf.get_state().derivative:
                    return False

            return False

        def __str__(self):
            return "PreviousGroupContains{" + str(self.states) + "}"

    class DictionaryItemIs(AbstractCondition):
        def __init__(self, item: DictionaryItem):
            self.item = item

        def accept_(self, visitor: SearchPath) -> bool:
            return self.item is not None and visitor.has_dictionary_item(self.item)

        def __str__(self):
            return "DictionaryItemIs{" + str(self.item) + "}"

    class DictionaryItemIsNone(AbstractCondition):
        def __init__(self, items: Tuple[DictionaryItem, ...]):
            self.items = items

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.get_dictionary_item() not in self.items

        def __str__(self):
            return "DictionaryItemIsNone{" + str(self.items) + "}"

    class HasTailSequence(AbstractCondition):
        def __init__(self, morphemes: Tuple[Morpheme, ...]):
            self.morphemes = morphemes

        def accept_(self, visitor: SearchPath) -> bool:
            forms = visitor.transitions
            if len(forms) < len(self.morphemes):
                return False
            else:
                i = 0
                j = len(forms) - len(self.morphemes)
                if i >= len(self.morphemes):
                    return True
                while self.morphemes[i] == forms[j].get_morpheme():
                    i += 1
                    j += 1
                    if i >= len(self.morphemes):
                        return True
                return False

        def __str__(self):
            return "HasTailSequence{" + str(self.morphemes) + "}"

    class ContainsMorphemeSequence(AbstractCondition):
        def __init__(self, morphemes: Tuple[Morpheme, ...]):
            self.morphemes = morphemes

        def accept_(self, visitor: SearchPath) -> bool:
            forms = visitor.transitions
            if len(forms) < len(self.morphemes):
                return False
            else:
                m = 0
                for form in forms:
                    if form.get_morpheme() == self.morphemes[m]:
                        m += 1
                        if m == len(self.morphemes):
                            return True
                    else:
                        m = 0
                return False

        def __str__(self):
            return "ContainsMorphemeSequence{" + str(self.morphemes) + "}"

    class PreviousGroupContainsMorpheme(AbstractCondition):
        def __init__(self, morphemes: Tuple[Morpheme, ...]):
            self.morphemes = morphemes

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions
            last_index = len(suffixes) - 1

            sf = suffixes[last_index]
            while not sf.get_state().derivative:
                if last_index == 0:
                    return False
                last_index -= 1
                sf = suffixes[last_index]

            for i in range(last_index - 1, 0, -1):
                sf = suffixes[i]
                if sf.get_state().morpheme in self.morphemes:
                    return True

                if sf.get_state().derivative:
                    return False
            return False

        def __str__(self):
            return "PreviousGroupContainsMorpheme" + str(self.morphemes) + "}"

    class NoSurfaceAfterDerivation(AbstractCondition):
        def __init__(self):
            pass

        def accept_(self, visitor: SearchPath) -> bool:
            suffixes = visitor.transitions

            for sf in reversed(suffixes[1:]):
                if sf.get_state().derivative:
                    return True

                if len(sf.surface) != 0:
                    return False
            return True

        def __str__(self):
            return "NoSurfaceAfterDerivation{}"

    class SecondaryPosIs(AbstractCondition):
        def __init__(self, pos: SecondaryPos):
            self.pos = pos

        def accept_(self, visitor: SearchPath) -> bool:
            return visitor.get_dictionary_item().secondary_pos == self.pos

        def __str__(self):
            return "SecondaryPosIs{" + self.pos.name + "}"


Conditions.HAS_TAIL = Conditions.HasTail()
Conditions.HAS_SURFACE = Conditions.HasAnySuffixSurface()
Conditions.HAS_NO_SURFACE = Conditions.HasAnySuffixSurface().not_()
Conditions.CURRENT_GROUP_EMPTY = Conditions.NoSurfaceAfterDerivation()
