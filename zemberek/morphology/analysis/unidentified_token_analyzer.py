from __future__ import annotations

import re

from enum import Enum
from typing import List, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .rule_based_analyzer import RuleBasedAnalyzer

from zemberek.core.turkish import PrimaryPos, SecondaryPos, TurkishAlphabet, StemAndEnding, RootAttribute, Turkish
from zemberek.tokenization.token import Token
from zemberek.morphology.lexicon import DictionaryItem
from zemberek.morphology.analysis.tr import TurkishNumbers, TurkishNumeralEndingMachine, PronunciationGuesser
from zemberek.morphology.analysis.single_analysis import SingleAnalysis


class UnidentifiedTokenAnalyzer:
    ALPHABET = TurkishAlphabet.INSTANCE
    non_letter_pattern = re.compile("[^" + ALPHABET.all_letters + "]")
    ordinal_map: Dict[str, str] = TurkishNumbers.ordinal_map

    def __init__(self, analyzer: RuleBasedAnalyzer):
        self.analyzer = analyzer
        self.numeral_ending_machine = TurkishNumeralEndingMachine()
        self.guesser = PronunciationGuesser()
        self.lexicon = analyzer.lexicon

    def analyze(self, token: Token) -> Tuple[SingleAnalysis, ...]:
        s_pos: SecondaryPos = self.guess_secondary_pos_type(token)
        word = token.content
        if s_pos == SecondaryPos.None_:
            if "?" in word:
                return ()
            else:
                return self.try_numeral(token) if self.ALPHABET.contains_digit(word) else \
                    self.analyze_word(word, SecondaryPos.Abbreviation if "." in word else SecondaryPos.ProperNoun)
        elif s_pos == SecondaryPos.RomanNumeral:
            return self.get_for_roman_numeral(token)
        elif s_pos != SecondaryPos.Date and s_pos != SecondaryPos.Clock:
            normalized = re.sub(self.non_letter_pattern, "", word)
            item = DictionaryItem(word, word, PrimaryPos.Noun, s_pos, pronunciation=normalized)
            if s_pos != SecondaryPos.HashTag and s_pos != SecondaryPos.Email and s_pos != SecondaryPos.Url and \
                    s_pos != SecondaryPos.Mention:
                item_does_not_exist = item not in self.lexicon
                if item_does_not_exist:
                    item.attributes.add(RootAttribute.Runtime)
                    self.analyzer.stem_transitions.add_dictionary_item(item)

                results: Tuple[SingleAnalysis] = self.analyzer.analyze(word)
                if item_does_not_exist:
                    self.analyzer.stem_transitions.remove_dictionary_item(item)

                return results
            else:
                return self.analyze_word(word, s_pos)
        else:
            return self.try_numeral(token)

    def get_for_roman_numeral(self, token: Token) -> Tuple[SingleAnalysis, ...]:
        content = token.content
        if "'" in content:
            i = content.find(chr(39))
            se = StemAndEnding(content[0:i], content[i + 1:])
        else:
            se = StemAndEnding(content, "")

        ss = se.stem
        if se.stem.endswith("."):
            ss = se.stem[:-1]

        decimal = TurkishNumbers.roman_to_decimal(ss)
        if decimal == -1:
            return ()
        else:
            if se.stem.endswith("."):
                lemma = self.numeral_ending_machine.find(str(decimal))
                lemma = self.ordinal_map.get(lemma)
            else:
                lemma = self.numeral_ending_machine.find(str(decimal))

            results: List[SingleAnalysis] = []
            if len(se.ending) > 0 and lemma == "dört" and self.ALPHABET.is_vowel(se.ending[0]):
                to_parse = "dörd" + se.ending
            else:
                to_parse = lemma + se.ending

            res = self.analyzer.analyze(to_parse)
            for re_ in res:
                if re_.item.primary_pos == PrimaryPos.Numeral:
                    run_time_item = DictionaryItem(se.stem, se.stem, PrimaryPos.Numeral, SecondaryPos.RomanNumeral,
                                                   pronunciation=content + lemma)
                    run_time_item.attributes.add(RootAttribute.Runtime)
                    results.append(re_.copy_for(run_time_item, se.stem))
            return tuple(results)

    def analyze_word(self, word: str, secondary_pos: SecondaryPos) -> Tuple[SingleAnalysis, ...]:
        if word.find(chr(39)) >= 0:
            return self.try_word_with_apostrophe(word, secondary_pos)
        else:
            return self.try_without_apostrophe(word,
                                               secondary_pos) if secondary_pos != SecondaryPos.ProperNoun and \
                                                                 secondary_pos != SecondaryPos.Abbreviation else []

    def try_without_apostrophe(self, word: str, secondary_pos: SecondaryPos) -> Tuple[SingleAnalysis]:
        normalized = None
        if self.ALPHABET.contains_foreign_diacritics(word):
            normalized = self.ALPHABET.foreign_diacritics_to_turkish(word)

        normalized = self.ALPHABET.normalize(word) if normalized is None else self.ALPHABET.normalize(normalized)
        capitalize: bool = secondary_pos == SecondaryPos.ProperNoun or secondary_pos == SecondaryPos.Abbreviation
        pronunciation = self.guess_pronunciation(normalized.replace(".", ""))
        item = DictionaryItem(Turkish.capitalize(normalized) if capitalize else normalized, normalized, PrimaryPos.Noun,
                              secondary_pos, pronunciation=pronunciation)
        if self.ALPHABET.contains_vowel(pronunciation):
            result = (SingleAnalysis.dummy(word, item),)
            return result
        else:
            item_does_not_exist: bool = item not in self.lexicon
            if item_does_not_exist:
                item.attributes.add(RootAttribute.Runtime)
                self.analyzer.stem_transitions.add_dictionary_item(item)

            results: Tuple[SingleAnalysis] = self.analyzer.analyze(normalized)
            if item_does_not_exist:
                self.analyzer.stem_transitions.remove_dictionary_item(item)

            return results

    def try_word_with_apostrophe(self, word: str, secondary_pos: SecondaryPos) -> Tuple[SingleAnalysis, ...]:
        normalized = self.ALPHABET.normalize_apostrophe(word)

        index = normalized.find(chr(39))
        if index > 0 and index != len(normalized) - 1:
            stem = normalized[0: index]
            ending = normalized[index + 1:]
            se = StemAndEnding(stem, ending)
            stem_normalized = self.ALPHABET.normalize(se.stem).replace(".", "")
            ending_normalized = self.ALPHABET.normalize(se.ending)
            pronunciation = self.guess_pronunciation(stem_normalized)
            capitalize: bool = secondary_pos == SecondaryPos.ProperNoun or secondary_pos == SecondaryPos.Abbreviation
            pronunciation_possible: bool = self.ALPHABET.contains_vowel(pronunciation)
            item = DictionaryItem(
                Turkish.capitalize(normalized) if capitalize else stem if pronunciation_possible else word,
                stem_normalized, PrimaryPos.Noun, secondary_pos, pronunciation=pronunciation)
            if not pronunciation_possible:
                result = (SingleAnalysis.dummy(word, item),)
                return result
            else:
                item_does_not_exist: bool = item not in self.lexicon
                if item_does_not_exist:
                    item.attributes.add(RootAttribute.Runtime)
                    self.analyzer.stem_transitions.add_dictionary_item(item)

                to_parse = stem_normalized + ending_normalized
                no_quotes_parses: Tuple[SingleAnalysis] = self.analyzer.analyze(to_parse)
                if item_does_not_exist:
                    self.analyzer.stem_transitions.remove_dictionary_item(item)

                analyses: Tuple[SingleAnalysis] = tuple(no_quotes_parse for no_quotes_parse in no_quotes_parses if
                                                        no_quotes_parse.get_stem() == stem_normalized)
                return analyses
        else:
            return ()

    def guess_pronunciation(self, stem: str) -> str:
        return self.guesser.to_turkish_letter_pronunciations(stem) if not self.ALPHABET.contains_vowel(stem) else stem

    def try_numeral(self, token: Token) -> Tuple[SingleAnalysis]:
        s = token.content
        s = s.translate(self.ALPHABET.lower_map).lower()
        se: StemAndEnding = self.get_from_numeral(s)

        if se.stem.endswith("."):
            ss = se.stem[:-1]
            lemma = self.numeral_ending_machine.find(ss)
            lemma = self.ordinal_map.get(lemma)
        else:
            lemma = self.numeral_ending_machine.find(se.stem)

        results: List[SingleAnalysis] = []

        for numerals in UnidentifiedTokenAnalyzer.Numerals:
            m = numerals.pattern.search(se.stem)
            if m:
                if len(se.ending) > 0 and lemma == "dört" and self.ALPHABET.is_vowel(se.ending[0]):
                    to_parse = "dört" + se.ending
                else:
                    to_parse = lemma + se.ending

                res: Tuple[SingleAnalysis] = self.analyzer.analyze(to_parse)
                for re_ in res:
                    if re_.item.primary_pos == PrimaryPos.Numeral:
                        run_time_item = DictionaryItem(se.stem, se.stem, pronunciation=s + lemma,
                                                       primary_pos=PrimaryPos.Numeral,
                                                       secondary_pos=numerals.secondary_pos)
                        run_time_item.attributes.add(RootAttribute.Runtime)
                        results.append(re_.copy_for(run_time_item, se.stem))

        return tuple(results)

    @staticmethod
    def get_from_numeral(s: str) -> StemAndEnding:
        if "'" in s:
            j = s.find("'")
            return StemAndEnding(s[0:j], s[j + 1:])
        else:
            j = 0
            for cut_point in range(len(s) - 1, -1, -1):
                c = s[cut_point]
                k = ord(c) - 48
                if c == '.' or 0 <= k <= 9:
                    break
                j += 1

            cut_point = len(s) - j
            return StemAndEnding(s[0: cut_point], s[cut_point:])  # BURASI YANLIŞ OLABILIR DIKKAT ET

    @staticmethod
    def guess_secondary_pos_type(token: Token) -> SecondaryPos:
        if token.type_ == Token.Type.Email:
            return SecondaryPos.Email
        elif token.type_ == Token.Type.URL:
            return SecondaryPos.Url
        elif token.type_ == Token.Type.HashTag:
            return SecondaryPos.HashTag
        elif token.type_ == Token.Type.Mention:
            return SecondaryPos.Mention
        elif token.type_ == Token.Type.Emoticon:
            return SecondaryPos.Emoticon
        elif token.type_ == Token.Type.RomanNumeral:
            return SecondaryPos.RomanNumeral
        elif token.type_ == Token.Type.Abbreviation:
            return SecondaryPos.Abbreviation
        elif token.type_ == Token.Type.Date:
            return SecondaryPos.Date
        elif token.type_ == Token.Type.Time:
            return SecondaryPos.Clock
        else:
            return SecondaryPos.None_

    class Numerals(Enum):
        CARDINAL = ("#", "^[+\\-]?\\d+$", SecondaryPos.Cardinal)
        ORDINAL = ("#.", "^[+\\-]?[0-9]+[.]$", SecondaryPos.Ordinal)
        RANGE = ("#-#", "^[+\\-]?[0-9]+-[0-9]+$", SecondaryPos.Range)
        RATIO = ("#/#", "^[+\\-]?[0-9]+/[0-9]+$", SecondaryPos.Ratio)
        REAL = ("#,#", "^[+\\-]?[0-9]+[,][0-9]+$|^[+\\-]?[0-9]+[.][0-9]+$", SecondaryPos.Real)
        DISTRIB = ("#DIS", "^\\d+[^0-9]+$", SecondaryPos.Distribution)
        PERCENTAGE_BEFORE = ("%#", "(^|[+\\-])(%)(\\d+)((([.]|[,])(\\d+))|)$", SecondaryPos.Percentage)
        TIME = ("#:#", "^([012][0-9]|[1-9])([.]|[:])([0-5][0-9])$", SecondaryPos.Clock)
        DATE = ("##.##.####", "^([0-3][0-9]|[1-9])([.]|[/])([01][0-9]|[1-9])([.]|[/])(\\d{4})$", SecondaryPos.Date)

        def __init__(self, lemma: str, pattern_str: str, secondary_pos: SecondaryPos):
            self.lemma = lemma
            self.pattern: re.Pattern = re.compile(pattern_str)
            self.secondary_pos = secondary_pos
