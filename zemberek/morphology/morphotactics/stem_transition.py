from __future__ import annotations
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.core.turkish import PhoneticAttribute
    from zemberek.morphology.lexicon import DictionaryItem
    from zemberek.morphology.morphotactics.morpheme_state import MorphemeState

from zemberek.morphology.morphotactics.morpheme_transition import MorphemeTransition


class StemTransition(MorphemeTransition):

    def __init__(self, surface: str, item: DictionaryItem, phonetic_attributes: Set[PhoneticAttribute],
                 to_state: MorphemeState):
        super().__init__()
        self.surface = surface
        self.item = item
        self.phonetic_attributes = phonetic_attributes
        self.to = to_state
        self.cached_hash = 0
        self.cached_hash = hash(self)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, StemTransition):
            return self.surface == other.surface and self.item == other.item and \
                   self.phonetic_attributes == other.phonetic_attributes
        else:
            return False

    def __hash__(self):
        return self.cached_hash if self.cached_hash != 0 else self.compute_hash()

    def __str__(self):
        return "[(Dict:" + str(self.item) + "):" + self.surface + " → " + str(self.to) + "]"

    def compute_hash(self) -> int:
        result = hash(self.surface)
        result = 31 * result + hash(self.item)
        for a in self.phonetic_attributes:
            result = 31 * result + hash(a)
        return result

    def get_copy(self) -> 'StemTransition':
        t = StemTransition(self.surface, self.item, self.phonetic_attributes, self.to)
        t.from_ = self.from_
        return t

    def has_surface_form(self):
        raise NotImplemented
