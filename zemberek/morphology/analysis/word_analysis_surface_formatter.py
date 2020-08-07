from enum import Enum, auto

from zemberek.core.turkish import PrimaryPos, SecondaryPos, RootAttribute, TurkishAlphabet, Turkish
from zemberek.morphology.analysis.single_analysis import SingleAnalysis


class WordAnalysisSurfaceFormatter:
    ALPHABET = TurkishAlphabet.INSTANCE

    def format_(self, analysis: SingleAnalysis, apostrophe: str) -> str:
        item = analysis.item
        ending = analysis.get_ending()
        if apostrophe is None and not self.apostrophe_required(analysis):
            return item.normalized_lemma() + ending if RootAttribute.NoQuote in item.attributes else \
                analysis.get_stem() + ending
        else:
            if apostrophe is None:
                apostrophe = "'"

            return item.normalized_lemma() + apostrophe + ending if len(ending) > 0 else item.normalized_lemma()

    def format_to_case(self, analysis: SingleAnalysis, type_: 'WordAnalysisSurfaceFormatter.CaseType',
                       apostrophe: str) -> str:
        formatted = self.format_(analysis, apostrophe)

        if type_ == WordAnalysisSurfaceFormatter.CaseType.DEFAULT_CASE:
            return formatted
        if type_ == WordAnalysisSurfaceFormatter.CaseType.LOWER_CASE:
            return formatted.translate(self.ALPHABET.lower_map).lower()
        if type_ == WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE:
            return formatted.translate(self.ALPHABET.upper_map).upper()
        if type_ == WordAnalysisSurfaceFormatter.CaseType.TITLE_CASE:
            return Turkish.capitalize(formatted)
        if type_ == WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE_ROOT_LOWER_CASE_ENDING:
            ending = analysis.get_ending()
            lemma_upper = analysis.item.normalized_lemma().translate(self.ALPHABET.upper_map).upper()

            if len(ending) == 0:
                return lemma_upper
            else:
                if apostrophe is None and not self.apostrophe_required(analysis):
                    return lemma_upper + ending

                if apostrophe is None:
                    apostrophe = "'"

                return lemma_upper + apostrophe + ending
        return ""

    @staticmethod
    def apostrophe_required(analysis: SingleAnalysis) -> bool:
        item = analysis.item
        return (item.secondary_pos == SecondaryPos.ProperNoun and RootAttribute.NoQuote not in item.attributes) \
               or (item.primary_pos == PrimaryPos.Numeral and item.has_attribute(RootAttribute.Runtime)) \
               or item.secondary_pos == SecondaryPos.Date

    def guess_case(self, inp: str) -> 'WordAnalysisSurfaceFormatter.CaseType':
        first_letter_upper_case = False
        lower_case_count = 0
        upper_case_count = 0
        letter_count = 0

        for apostrophe_index, c in enumerate(inp):
            if c.isalpha():
                if apostrophe_index == 0:
                    first_letter_upper_case = c.isupper()
                    if first_letter_upper_case:
                        upper_case_count += 1
                    else:
                        lower_case_count += 1
                elif c.isupper():
                    upper_case_count += 1
                elif c.islower():
                    lower_case_count += 1

                letter_count += 1

        if letter_count == 0:
            return WordAnalysisSurfaceFormatter.CaseType.DEFAULT_CASE
        elif letter_count == lower_case_count:
            return WordAnalysisSurfaceFormatter.CaseType.LOWER_CASE
        elif letter_count == upper_case_count:
            return WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE
        elif first_letter_upper_case and letter_count == lower_case_count + 1:
            return WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE if letter_count == 1 else \
                WordAnalysisSurfaceFormatter.CaseType.TITLE_CASE
        else:
            apostrophe_index = inp.find(chr(39))  # chr(39) = "'"
            if 0 < apostrophe_index < len(inp) - 1 and self.guess_case(inp[0:apostrophe_index]) == \
                    WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE and self.guess_case(inp[apostrophe_index + 1:]) == \
                    WordAnalysisSurfaceFormatter.CaseType.LOWER_CASE:
                return WordAnalysisSurfaceFormatter.CaseType.UPPER_CASE_ROOT_LOWER_CASE_ENDING
            else:
                return WordAnalysisSurfaceFormatter.CaseType.MIXED_CASE

    class CaseType(Enum):
        DEFAULT_CASE = auto()
        LOWER_CASE = auto()
        UPPER_CASE = auto()
        TITLE_CASE = auto()
        UPPER_CASE_ROOT_LOWER_CASE_ENDING = auto()
        MIXED_CASE = auto()
