class TurkicLetter:
    """
    This class represents a Letter which contains Turkic language specific attributes, such as vowel type,
    English equivalent characters.
    """
    UNDEFINED: 'TurkicLetter'

    def __init__(self, char_value: str = False, vowel: bool = False, frontal: bool = False, rounded: bool = False,
                 voiceless: bool = False, continuant: bool = False):
        self.char_value = char_value
        self.vowel = vowel
        self.frontal = frontal
        self.rounded = rounded
        self.voiceless = voiceless
        self.continuant = continuant

    def is_vowel(self):
        return self.vowel

    def is_consonant(self):
        return not self.vowel

    def is_frontal(self):
        return self.frontal

    def is_rounded(self):
        return self.rounded

    def is_voiceless(self):
        return self.voiceless

    def is_stop_consonant(self):
        return self.voiceless and not self.continuant

    def copy_for(self, c: str) -> 'TurkicLetter':
        return TurkicLetter(c, self.vowel, self.frontal, self.rounded, self.voiceless, self.continuant)

    def __eq__(self, other):
        if self is other:
            return True
        elif other is not None and isinstance(other, TurkicLetter):
            return self.char_value == other.char_value
        else:
            return False

    def __hash__(self):
        return ord(self.char_value)


TurkicLetter.UNDEFINED = TurkicLetter('\u0000')
