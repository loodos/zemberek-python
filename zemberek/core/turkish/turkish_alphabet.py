from typing import List, Dict

from zemberek.core.text import TextUtil
from zemberek.core.turkish.turkic_letter import TurkicLetter


class TurkishAlphabet:
    r"""
        The class that represents Turkish alphabet. It stores all the letters and
        special characters in Turkish.

        Attributes:
            lower_map Dict[str, str]:
                A dictionary to map capital "I" and "İ" to their correct lowers.
            upper_map Dict[str, str]:
                A dictionary to map "i" to its correct capital

    """
    INSTANCE: 'TurkishAlphabet'
    lower_map = {ord(u'I'): u'ı', ord(u"İ"): u"i"}
    upper_map = {ord(u'i'): u'İ'}

    def __init__(self):
        self.lowercase = "abcçdefgğhıijklmnoöprsştuüvyzxwqâîû"
        self.uppercase = self.lowercase.translate(self.upper_map).upper()
        self.all_letters = self.lowercase + self.uppercase
        self.vowels_lowercase = "aeıioöuüâîû"
        self.vowels_uppercase = self.vowels_lowercase.translate(self.upper_map).upper()
        self.vowels = set(self.vowels_lowercase + self.vowels_uppercase)
        self.circumflex = "âîû"
        self.circumflex_upper = "ÂÎÛ"
        self.circumflexes = set(self.circumflex + self.circumflex_upper)
        self.apostrophe = set("′´`’‘'")
        self.stop_consonants = "çkptÇKPT"
        self.voiceless_consonants = "çfhkpsştÇFHKPSŞT"
        self.turkish_specific = "çÇğĞıİöÖşŞüÜâîûÂÎÛ"
        self.turkish_specific_lookup = set("çÇğĞıİöÖşŞüÜâîûÂÎÛ")
        self.turkish_ascii = "cCgGiIoOsSuUaiuAIU"
        self.ascii_eq_tr = "cCgGiIoOsSuUçÇğĞıİöÖşŞüÜ"
        self.ascii_eq_tr_set = set(self.ascii_eq_tr)
        self.ascii_eq = "çÇğĞıİöÖşŞüÜcCgGiIoOsSuU"
        self.foreign_diacritics = "ÀÁÂÃÄÅÈÉÊËÌÍÎÏÑÒÓÔÕÙÚÛàáâãäåèéêëìíîïñòóôõùúû"
        self.diacritics_to_turkish = "AAAAAAEEEEIIIINOOOOUUUaaaaaaeeeeiiiinoooouuu"

        self.voicing_map = {}
        self.devoicing_map = {}
        self.circumflex_map = {}

        self.letter_map = {}
        letters = self.generate_letters()
        for letter in letters:
            self.letter_map[letter.char_value] = letter

        self.ascii_equal_map: Dict[str, str] = {}
        for in_, out_ in zip(self.ascii_eq_tr, self.ascii_eq):
            self.ascii_equal_map[in_] = out_

        self.turkish_to_ascii_map = {}
        self.foreign_diacritics_map = {}

        self.generate_voicing_devoicing_lookups()
        self.populate_dict(self.turkish_to_ascii_map, self.turkish_specific, self.turkish_ascii)
        self.populate_dict(self.foreign_diacritics_map, self.foreign_diacritics, self.diacritics_to_turkish)

    def is_turkish_specific(self, c: str) -> bool:
        return c in self.turkish_specific_lookup

    def contains_ascii_related(self, s: str) -> bool:
        for c in s:
            if c in self.ascii_eq_tr_set:
                return True
        return False

    def to_ascii(self, inp: str) -> str:
        sb = []
        for c in inp:
            res = self.turkish_to_ascii_map.get(c)
            map_ = c if res is None else res
            sb.append(map_)
        return ''.join(sb)

    def is_ascii_equal(self, c1: str, c2: str) -> bool:
        if c1 == c2:
            return True
        a1 = self.ascii_equal_map.get(c1)
        if a1 is None:
            return False
        return a1 == c2

    def equals_ignore_diacritics(self, s1: str, s2: str) -> bool:
        if s1 is None or s2 is None:
            return False
        if len(s1) != len(s2):
            return False
        for c1, c2 in zip(s1, s2):
            if not self.is_ascii_equal(c1, c2):
                return False
        return True

    def starts_with_ignore_diacritics(self, s1: str, s2: str) -> bool:
        if s1 is None or s2 is None:
            return False
        if len(s1) < len(s2):
            return False

        for c1, c2 in zip(s1, s2):
            if not self.is_ascii_equal(c1, c2):
                return False
        return True

    @staticmethod
    def contains_digit(s: str) -> bool:
        if len(s) == 0:
            return False
        else:
            for c in s:
                if "0" <= c <= "9":
                    return True
            return False

    def contains_apostrophe(self, s: str) -> bool:
        for c in s:
            if c in self.apostrophe:
                return True
        return False

    def normalize_apostrophe(self, s: str) -> str:
        if not self.contains_apostrophe(s):
            return s
        else:
            sb = []
            for c in s:
                if c in self.apostrophe:
                    sb.append("\'")
                else:
                    sb.append(c)
            return ''.join(sb)

    def contains_foreign_diacritics(self, s: str) -> bool:
        for c in s:
            if c in self.foreign_diacritics:
                return True
        return False

    def foreign_diacritics_to_turkish(self, inp: str) -> str:
        sb = ""

        for c in inp:
            res = self.foreign_diacritics_map.get(c)
            map_ = c if res is None else res
            sb += map_
        return sb

    def contains_circumflex(self, s: str) -> bool:
        for c in s:
            if c in self.circumflexes:
                return True
        return False

    def normalize_circumflex(self, s: str) -> str:
        if len(s) == 1:
            res = self.circumflex_map.get(s)
            return s if res is None else res
        else:
            if not self.contains_circumflex(s):
                return s
            else:
                sb = []
                for c in s:
                    if c in self.circumflexes:
                        sb.append(self.circumflex_map.get(c))
                    else:
                        sb.append(c)

                return ''.join(sb)

    def normalize(self, inp: str) -> str:
        inp = TextUtil.normalize_apostrophes(inp.translate(self.lower_map).lower())
        sb = []
        for c in inp:
            if c in self.letter_map.keys() or c == '.' or c == '-':
                sb.append(c)
            else:
                sb.append("?")
        return ''.join(sb)

    def is_vowel(self, c: str) -> bool:
        return c in self.vowels

    def contains_vowel(self, s: str) -> bool:
        if len(s) == 0:
            return False
        for c in s:
            if self.is_vowel(c):
                return True
        return False

    def generate_voicing_devoicing_lookups(self):
        voicing_in = "çgkpt"
        voicing_out = "cğğbd"
        devoicing_in = "bcdgğ"
        devoicing_out = "pçtkk"
        self.populate_dict(self.voicing_map, voicing_in + voicing_in.upper(), voicing_out + voicing_out.upper())
        self.populate_dict(self.devoicing_map, devoicing_in + devoicing_in.upper(),
                           devoicing_out + devoicing_out.upper())
        circumflex_normalized = "aiu"
        self.populate_dict(self.circumflex_map, self.circumflex + self.circumflex.upper(),
                           circumflex_normalized + circumflex_normalized.translate(self.upper_map).upper())

    @staticmethod
    def populate_dict(dictionary: Dict, in_str: str, out_str: str):
        for in_, out in zip(in_str, out_str):
            dictionary[in_] = out

    @staticmethod
    def generate_letters() -> List[TurkicLetter]:
        letters = [TurkicLetter('a', vowel=True), TurkicLetter('e', vowel=True, frontal=True),
                   TurkicLetter('ı', vowel=True), TurkicLetter('i', vowel=True, frontal=True),
                   TurkicLetter('o', vowel=True, rounded=True),
                   TurkicLetter('ö', vowel=True, frontal=True, rounded=True),
                   TurkicLetter('u', vowel=True, rounded=True),
                   TurkicLetter('ü', vowel=True, rounded=True, frontal=True), TurkicLetter('â', vowel=True),
                   TurkicLetter('î', vowel=True, frontal=True),
                   TurkicLetter('û', vowel=True, frontal=True, rounded=True), TurkicLetter('b'), TurkicLetter('c'),
                   TurkicLetter('ç', voiceless=True), TurkicLetter('d'),
                   TurkicLetter('f', continuant=True, voiceless=True), TurkicLetter('g'),
                   TurkicLetter('ğ', continuant=True), TurkicLetter('h', continuant=True, voiceless=True),
                   TurkicLetter('j', continuant=True), TurkicLetter('k', voiceless=True),
                   TurkicLetter('l', continuant=True), TurkicLetter('m', continuant=True),
                   TurkicLetter('n', continuant=True), TurkicLetter('p', voiceless=True),
                   TurkicLetter('r', continuant=True), TurkicLetter('s', continuant=True, voiceless=True),
                   TurkicLetter('ş', continuant=True, voiceless=True), TurkicLetter('t', voiceless=True),
                   TurkicLetter('v', continuant=True), TurkicLetter('y', continuant=True),
                   TurkicLetter('z', continuant=True), TurkicLetter('q'), TurkicLetter('w'), TurkicLetter('x')]

        capitals = []
        for letter in letters:
            upper = 'İ' if letter.char_value == 'i' else letter.char_value.upper()
            capitals.append(letter.copy_for(upper))

        letters.extend(capitals)
        return letters

    def get_last_letter(self, s: str) -> TurkicLetter:
        """
        Returns the last letter of the input as "TurkicLetter". If input is empty or the last character
        does not belong to alphabet, returns TurkicLetter.UNDEFINED.

        :param str s: input string
        :return: last letter of input as TurkicLetter
        """
        return TurkicLetter.UNDEFINED if len(s) == 0 else self.get_letter(s[-1])

    def get_letter(self, c: str) -> TurkicLetter:
        letter = self.letter_map.get(c)
        return TurkicLetter.UNDEFINED if letter is None else letter

    def get_last_vowel(self, s: str) -> TurkicLetter:
        if len(s) == 0:
            return TurkicLetter.UNDEFINED
        else:
            for c in reversed(s):
                if self.is_vowel(c):
                    return self.get_letter(c)
            return TurkicLetter.UNDEFINED

    def get_first_letter(self, s: str) -> TurkicLetter:
        """
        Returns the first letter of the input as "TurkicLetter". If input is empty or the first
        character does not belong to alphabet, returns TurkicLetter.UNDEFINED.

        :param str s: input string
        :return: first letter of input as TurkicLetter
        """
        if not s:
            return TurkicLetter.UNDEFINED
        else:
            return self.get_letter(s[0])

    @staticmethod
    def last_char(s: str) -> str:
        return s[-1]

    def voice(self, c: str) -> str:
        res = self.voicing_map.get(c)
        return c if res is None else res

    def devoice(self, c: str) -> str:
        res = self.devoicing_map.get(c)
        return c if res is None else res


TurkishAlphabet.INSTANCE = TurkishAlphabet()
