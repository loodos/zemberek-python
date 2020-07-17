from copy import deepcopy
from typing import Set

from zemberek.core.turkish import TurkishAlphabet, PhoneticAttribute


class AttributesHelper:

    alphabet = TurkishAlphabet.INSTANCE
    NO_VOWEL_ATTRIBUTES = (PhoneticAttribute.LastLetterConsonant, PhoneticAttribute.FirstLetterConsonant,
                           PhoneticAttribute.HasNoVowel)

    @classmethod
    def get_morphemic_attributes(cls, seq: str, predecessor_attrs: Set[PhoneticAttribute] = None) -> \
            Set[PhoneticAttribute]:

        if predecessor_attrs is None:
            predecessor_attrs = set()

        if not seq:
            return deepcopy(predecessor_attrs)
        else:
            attrs = set()
            if cls.alphabet.contains_vowel(seq):
                last = cls.alphabet.get_last_letter(seq)
                if last.is_vowel():
                    attrs.add(PhoneticAttribute.LastLetterVowel)
                else:
                    attrs.add(PhoneticAttribute.LastLetterConsonant)

                last_vowel = last if last.is_vowel() else cls.alphabet.get_last_vowel(seq)
                if last_vowel.is_frontal():
                    attrs.add(PhoneticAttribute.LastVowelFrontal)
                else:
                    attrs.add(PhoneticAttribute.LastVowelBack)

                if last.is_rounded():
                    attrs.add(PhoneticAttribute.LastVowelRounded)
                else:
                    attrs.add(PhoneticAttribute.LastVowelUnrounded)

                if cls.alphabet.get_first_letter(seq).is_vowel():
                    attrs.add(PhoneticAttribute.FirstLetterVowel)
                else:
                    attrs.add(PhoneticAttribute.FirstLetterConsonant)
            else:
                attrs = deepcopy(predecessor_attrs)
                attrs.update(cls.NO_VOWEL_ATTRIBUTES)
                try:
                    attrs.remove(PhoneticAttribute.LastLetterVowel)
                except KeyError:
                    pass

                try:
                    attrs.remove(PhoneticAttribute.ExpectsConsonant)
                except KeyError:
                    pass

            last = cls.alphabet.get_last_letter(seq)
            if last.is_voiceless():
                attrs.add(PhoneticAttribute.LastLetterVoiceless)
                if last.is_stop_consonant():
                    attrs.add(PhoneticAttribute.LastLetterVoicelessStop)
            else:
                attrs.add(PhoneticAttribute.LastLetterVoiced)

            return attrs
