import pickle
import os

from pkg_resources import resource_filename
from typing import Dict


class Deasciifier:
    turkish_context_size = 10
    with open(
            resource_filename("zemberek", os.path.join("resources", "normalization", "turkish_pattern_table.pickle")),
            "rb"
    ) as f:
        turkish_pattern_table: Dict[str, Dict] = pickle.load(f)
    del f
    turkish_asciify_table = {u'ç': u'c', u'Ç': u'C', u'ğ': u'g', u'Ğ': u'G', u'ö': u'o',
                             u'Ö': u'O', u'ı': u'i', u'İ': u'I', u'ş': u's', u'Ş': u'S'}
    uppercase_letters = (u"A", u"B", u"C", u"D", u"E", u"F", u"G", u"H", u"I", u"J", u"K", u"L", u"M", u"N", u"O",
                         u"P", u"Q", u"R", u"S", u"T", u"U", u"V", u"W", u"X", u"Y", u"Z")

    turkish_downcase_asciify_table: Dict[str, str] = {u'ç': u'c', u"Ç": u"c", u"ğ": u"g", u"Ğ": u"g", u"ö": u"o",
                                                      u"Ö": u"o", u"ı": u"i", u"İ": u"i", u"ş": u"s", u"Ş": u"s",
                                                      u"ü": u"u", u"Ü": u"u"}
    for c in uppercase_letters:
        turkish_downcase_asciify_table[c] = c.lower()
        turkish_downcase_asciify_table[c.lower()] = c.lower()

    turkish_upcase_accents_table: Dict[str, str] = {}
    for c in uppercase_letters:
        turkish_upcase_accents_table[c] = c.lower()
        turkish_upcase_accents_table[c.lower()] = c.lower()

    turkish_upcase_accents_table[u'ç'] = u'C'
    turkish_upcase_accents_table[u'Ç'] = u'C'
    turkish_upcase_accents_table[u'ğ'] = u'G'
    turkish_upcase_accents_table[u'Ğ'] = u'G'
    turkish_upcase_accents_table[u'ö'] = u'O'
    turkish_upcase_accents_table[u'Ö'] = u'O'
    turkish_upcase_accents_table[u'ı'] = u'I'
    turkish_upcase_accents_table[u'İ'] = u'i'
    turkish_upcase_accents_table[u'ş'] = u'S'
    turkish_upcase_accents_table[u'Ş'] = u'S'
    turkish_upcase_accents_table[u'ü'] = u'U'
    turkish_upcase_accents_table[u'Ü'] = u'U'

    turkish_toggle_accent_table = {u'c': u'ç', u'C': u'Ç', u'g': u'ğ', u'G': u'Ğ', u'o': u'ö', u'O': u'Ö', u'u': u'ü',
                                   u'U': u'Ü', u'i': u'ı', u'I': u'İ', u's': u'ş', u'S': u'Ş', u'ç': u'c', u'Ç': u'C',
                                   u'ğ': u'g', u'Ğ': u'G', u'ö': u'o', u'Ö': u'O', u'ü': u'u', u'Ü': u'U', u'ı': u'i',
                                   u'İ': u'I', u'ş': u's', u'Ş': u'S'}

    def __init__(self, ascii_string: str):
        self.ascii_string = ascii_string
        self.turkish_string = ascii_string

    def convert_to_turkish(self) -> str:
        for i, c in enumerate(self.turkish_string):
            if self.turkish_need_correction(c, i):
                self.turkish_string = self.turkish_string[:i] + self.turkish_toggle_accent_table.get(c, c) + \
                                      self.turkish_string[i+1:]
            else:
                self.turkish_string = self.turkish_string[:i] + c + self.turkish_string[i+1:]
        return self.turkish_string

    def turkish_need_correction(self, c: str, point: int) -> bool:
        tr = self.turkish_asciify_table.get(c)
        if not tr:
            tr = c

        pl: Dict[str, int] = self.turkish_pattern_table.get(tr.lower())

        m = False
        if pl:
            m = self.turkish_match_pattern(pl, point)

        if tr == u'I':
            if c == tr:
                return not m
            else:
                return m
        else:
            if c == tr:
                return m
            else:
                return not m

    def turkish_match_pattern(self, dlist: Dict[str, int], point: int) -> bool:
        rank = len(dlist) * 2
        string = self.turkish_get_context(self.turkish_context_size, point)

        start = 0
        _len = len(string)
        while start <= self.turkish_context_size:
            end = self.turkish_context_size + 1
            while end <= _len:
                s = string[start:end]
                r = dlist.get(s)
                if r is not None and abs(r) < abs(rank):
                    rank = r
                end += 1
            start += 1

        return rank > 0

    def turkish_get_context(self, size: int, point: int):
        s = ' ' * (1 + (2 * size))
        s = s[:size] + 'X' + s[size + 1:]
        i = size + 1
        space = False
        index = point + 1

        while i < len(s) and not space and index < len(self.ascii_string):
            current_char = self.turkish_string[index]
            x = self.turkish_downcase_asciify_table.get(current_char, False)

            if not x:
                if not space:
                     i = i + 1
                     space = True
            else:
                s = s[:i] + x + s[i+1:]
                i = i + 1
                space = False

            index = index + 1

        s = s[:i]
        index = point - 1
        i = size - 1
        space = False

        while i >= 0 and index >= 0:
            current_char = self.turkish_string[index]
            x = self.turkish_upcase_accents_table.get(current_char, False)
            if not x:
                if not space:
                    i = i - 1
                    space = True
            else:
                s = s[:i] + x + s[i+1:]
                i = i - 1
                space = False
            index = index - 1

        return s
