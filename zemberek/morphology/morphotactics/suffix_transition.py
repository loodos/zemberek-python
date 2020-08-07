from __future__ import annotations
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from zemberek.morphology.analysis.search_path import SearchPath
    from zemberek.morphology.morphotactics.morpheme_state import MorphemeState

from zemberek.core.turkish import TurkishAlphabet, PhoneticAttribute
from zemberek.morphology.analysis.surface_transitions import SurfaceTransition
from zemberek.morphology.morphotactics.conditions import Conditions
from zemberek.morphology.morphotactics.attribute_to_surface_cache import AttributeToSurfaceCache
from zemberek.morphology.morphotactics.morpheme_transition import MorphemeTransition


class SuffixTransition(MorphemeTransition):

    def __init__(self, builder: 'SuffixTransition.Builder' = None, surface_template: str = None):
        super().__init__()
        if surface_template is not None:
            self.surface_template = surface_template
        else:
            self.from_: MorphemeState = builder.from_
            self.to: MorphemeState = builder.to
            self.surface_template = "" if builder.surface_template is None else builder.surface_template
            self.condition = builder.condition
            self.conditions_from_template(self.surface_template)
            self.token_list = [item for item in SurfaceTransition.SuffixTemplateTokenizer(self.surface_template)]
            self.condition_count = self.count_conditions()
            self.surface_cache = AttributeToSurfaceCache()

    def __str__(self):
        return "[" + self.from_.id_ + "→" + self.to.id_ + \
               ("" if len(self.surface_template) == 0 else ":" + self.surface_template) + "]"

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, SuffixTransition):
            this_condition: str = "" if self.condition is None else str(self.condition)
            that_condition: str = "" if other.condition is None else str(other.condition)
            return self.surface_template == other.surface_template and self.from_ == other.from_ and \
                self.to == other.to and this_condition == that_condition
        else:
            return False

    def __hash__(self):
        this_condition = "" if self.condition is None else str(self.condition)
        result = hash(self.surface_template)
        result = 31 * result + hash(self.from_)
        result = 31 * result + hash(self.to)
        result = 31 * result + hash(this_condition)
        return result

    def can_pass(self, path: SearchPath) -> bool:
        return self.condition is None or self.condition.accept_(path)

    def get_copy(self) -> 'SuffixTransition':
        st = SuffixTransition(surface_template=self.surface_template)
        st.from_ = self.from_
        st.to = self.to
        st.condition = self.condition
        st.token_list = self.token_list.copy()
        st.surface_cache = self.surface_cache
        return st

    def connect(self):
        self.from_.add_outgoing((self,))
        self.to.add_incoming((self,))

    def count_conditions(self) -> int:
        if self.condition is None:
            return 0
        return self.condition.count() if isinstance(self.condition, Conditions.CombinedCondition) else 1

    def conditions_from_template(self, template: str):
        lower_map = {ord(u'I'): u'ı', ord(u'İ'): u'i'}
        if template is not None and len(template) != 0:
            lower = template.translate(lower_map).lower()
            c = None
            first_char_vowel: bool = TurkishAlphabet.INSTANCE.is_vowel(lower[0])

            if lower.startswith(">") or not first_char_vowel:
                c = Conditions.not_have(p_attribute=PhoneticAttribute.ExpectsVowel)

            if lower.startswith("+") and TurkishAlphabet.INSTANCE.is_vowel(lower[2]) or first_char_vowel:
                c = Conditions.not_have(p_attribute=PhoneticAttribute.ExpectsConsonant)

            if c:
                if self.condition is None:
                    self.condition = c
                else:
                    self.condition = c.and_(self.condition)

    def add_to_surface_cache(self, attributes: Set[PhoneticAttribute], value: str):
        self.surface_cache.add_surface(attributes=attributes, surface=value)

    def get_from_surface_cache(self, attributes: Set[PhoneticAttribute]) -> str:
        return self.surface_cache.get_surface(attributes=attributes)

    def get_last_template_token(self) -> SurfaceTransition.SuffixTemplateToken:
        return None if len(self.token_list) == 0 else self.token_list[-1]

    def has_surface_form(self) -> bool:
        return len(self.token_list) > 0

    class Builder:

        def __init__(self, from_: MorphemeState, to: MorphemeState, surface_template: str = None, condition=None):
            self.from_ = from_
            self.to = to
            self.surface_template = surface_template
            self.condition = condition

        def empty(self) -> 'SuffixTransition.Builder':
            self.surface_template = ""
            return self

        def build(self) -> 'SuffixTransition':
            transition = SuffixTransition(builder=self)
            transition.connect()
            return transition
