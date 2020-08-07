from __future__ import annotations
from typing import Set, Union, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from zemberek.morphology.morphotactics.suffix_transition import SuffixTransition
    from zemberek.morphology.morphotactics.morpheme_transition import MorphemeTransition
    from zemberek.morphology.morphotactics.stem_transition import StemTransition

from zemberek.core.turkish import PhoneticAttribute, TurkishAlphabet
from zemberek.morphology.analysis.attributes_helper import AttributesHelper


class SurfaceTransition:

    alphabet = TurkishAlphabet.INSTANCE

    def __init__(self, surface: str, transition: Union[SuffixTransition, StemTransition, MorphemeTransition]):
        self.surface = surface
        self.lexical_transition = transition

    def is_derivative(self) -> bool:
        return self.lexical_transition.to.derivative

    def get_morpheme(self):
        return self.lexical_transition.to.morpheme

    def get_state(self):  # -> MorphemeState
        return self.lexical_transition.to

    def __str__(self):
        return ("" if len(self.surface) == 0 else self.surface + ":") + self.get_state().id_

    @staticmethod
    def generate_surface(transition: SuffixTransition, phonetic_attributes: Set[PhoneticAttribute]):
        cached: str = transition.get_from_surface_cache(phonetic_attributes)
        if cached:
            return cached
        else:
            sb = ""

            for index, token in enumerate(transition.token_list):
                attrs: Set[PhoneticAttribute] = AttributesHelper.get_morphemic_attributes(sb, phonetic_attributes)

                if token.type_ == SurfaceTransition.TemplateTokenType.LETTER:
                    sb += token.letter
                elif token.type_ == SurfaceTransition.TemplateTokenType.A_WOVEL:
                    if index != 0 or PhoneticAttribute.LastLetterVowel not in phonetic_attributes:
                        if PhoneticAttribute.LastVowelBack in attrs:
                            sb += 'a'
                        else:
                            if PhoneticAttribute.LastVowelFrontal not in attrs:
                                raise ValueError("Cannot generate A form!")
                            sb += 'e'
                elif token.type_ == SurfaceTransition.TemplateTokenType.I_WOVEL:
                    if index != 0 or PhoneticAttribute.LastLetterVowel not in phonetic_attributes:
                        if PhoneticAttribute.LastVowelFrontal in attrs and PhoneticAttribute.LastVowelUnrounded in attrs:
                            sb += 'i'
                        elif PhoneticAttribute.LastVowelBack in attrs and PhoneticAttribute.LastVowelUnrounded in attrs:
                            sb += "ı"
                        elif PhoneticAttribute.LastVowelBack in attrs and PhoneticAttribute.LastVowelRounded in attrs:
                            sb += "u"
                        else:
                            if PhoneticAttribute.LastVowelFrontal not in attrs or PhoneticAttribute.LastVowelRounded not in attrs:
                                raise ValueError("Cannot generate I form!")
                            sb += "ü"
                elif token.type_ == SurfaceTransition.TemplateTokenType.APPEND:
                    if PhoneticAttribute.LastLetterVowel in attrs:
                        sb += token.letter
                elif token.type_ == SurfaceTransition.TemplateTokenType.DEVOICE_FIRST:
                    ld = token.letter
                    if PhoneticAttribute.LastLetterVoiceless in attrs:
                        ld = SurfaceTransition.alphabet.devoice(ld)

                    sb += ld
                elif token.type_ == SurfaceTransition.TemplateTokenType.LAST_VOICED or token.type_ == SurfaceTransition.TemplateTokenType.LAST_NOT_VOICED:
                    ld = token.letter
                    sb += ld

            transition.add_to_surface_cache(phonetic_attributes, sb)
            return sb

    class SuffixTemplateTokenizer:

        def __init__(self, generation_word: str):
            self.generation_word = generation_word
            self.pointer = 0

        def has_next(self) -> bool:
            return self.generation_word is not None and self.pointer < len(self.generation_word)

        def __iter__(self):
            return self

        def __next__(self) -> 'SurfaceTransition.SuffixTemplateToken':
            if not self.has_next():
                raise StopIteration
            else:
                c = self.generation_word[self.pointer]
                self.pointer += 1
                c_next = 0  # char
                if self.pointer < len(self.generation_word):
                    c_next = ord(self.generation_word[self.pointer])

                undefined = 0  # char
                if c == "!":
                    self.pointer += 1
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.LAST_NOT_VOICED,
                                                                 chr(c_next))
                elif c == "+":
                    self.pointer += 1
                    if c_next == ord("I"):
                        return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.I_WOVEL,
                                                                     chr(undefined), True)
                    elif c_next == ord("A"):
                        return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.A_WOVEL,
                                                                     chr(undefined), True)
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.APPEND,
                                                                 chr(c_next))
                elif c == ">":
                    self.pointer += 1
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.DEVOICE_FIRST,
                                                                 chr(c_next))
                elif c == "A":
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.A_WOVEL,
                                                                 chr(undefined))
                elif c == "I":
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.I_WOVEL,
                                                                 chr(undefined))
                elif c == "~":
                    self.pointer += 1
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.LAST_VOICED,
                                                                 chr(c_next))
                else:
                    return SurfaceTransition.SuffixTemplateToken(SurfaceTransition.TemplateTokenType.LETTER, c)

    class SuffixTemplateToken:
        def __init__(self, type_: 'SurfaceTransition.TemplateTokenType', letter: str, append: bool = False):
            self.type_ = type_
            self.letter = letter
            self.append = append

        def get_type(self) -> 'SurfaceTransition.TemplateTokenType':
            return self.type_

        def get_letter(self) -> str:
            return self.letter

    class TemplateTokenType(Enum):
        I_WOVEL = auto()
        A_WOVEL = auto()
        DEVOICE_FIRST = auto()
        LAST_VOICED = auto()
        LAST_NOT_VOICED = auto()
        APPEND = auto()
        LETTER = auto()
