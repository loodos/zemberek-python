from __future__ import annotations

import os
import re
import logging

from pkg_resources import resource_filename
from operator import itemgetter
from typing import List, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology import TurkishMorphology

from zemberek.core.turkish import TurkishAlphabet, Turkish
from zemberek.morphology.analysis.word_analysis_surface_formatter import WordAnalysisSurfaceFormatter
from zemberek.lm import SmoothLM
from zemberek.normalization.stem_ending_graph import StemEndingGraph
from zemberek.normalization.character_graph_decoder import CharacterGraphDecoder

logger = logging.getLogger(__name__)


class TurkishSpellChecker:

    formatter = WordAnalysisSurfaceFormatter()

    def __init__(self, morphology: TurkishMorphology, matcher: CharacterGraphDecoder.CharMatcher = None,
                 decoder: CharacterGraphDecoder = None):
        self.morphology = morphology
        if not decoder:
            graph = StemEndingGraph(morphology)
            self.decoder = CharacterGraphDecoder(graph.stem_graph)
            self.unigram_model: SmoothLM = SmoothLM.builder(
                resource=resource_filename("zemberek", os.path.join("resources", "lm-unigram.slm"))).build()
            self.char_matcher = matcher
        else:
            self.decoder = decoder
            self.char_matcher = matcher

    def suggest_for_word(self, word: str, lm: SmoothLM = None) -> Tuple[str]:
        if not lm:
            lm = self.unigram_model
        unranked: Tuple[str] = self.get_unranked_suggestions(word)
        return self.rank_with_unigram_probability(unranked, lm)

    def suggest_for_word_for_normalization(self, word: str, left_context: str, right_context: str, lm: SmoothLM) -> \
            Tuple[str]:
        unranked: Tuple[str] = self.get_unranked_suggestions(word)
        if lm is None:
            logger.warning("No language model provided. Returning unraked results.")
            return unranked

        if lm.order < 2:
            logger.warning("Language model order is 1. For context ranking it should be at least 2. "
                           "Unigram ranking will be applied.")
            return self.suggest_for_word(word, lm)

        vocabulary = lm.vocabulary
        results: List[Tuple[str, float]] = []
        for string in unranked:
            if left_context is None:
                left_context = vocabulary.sentence_start
            else:
                left_context = self.normalize_for_lm(left_context)
            if right_context is None:
                right_context = vocabulary.sentence_end
            else:
                right_context = self.normalize_for_lm(right_context)

            w = self.normalize_for_lm(string)
            word_index = vocabulary.index_of(w)
            left_index = vocabulary.index_of(left_context)
            right_index = vocabulary.index_of(right_context)

            score: float
            if lm.order == 2:
                score = lm.get_probability((left_index, word_index)) + lm.get_probability((word_index, right_index))
            else:
                score = lm.get_probability((left_index, word_index, right_index))
            results.append((string, score))

        results.sort(key=itemgetter(1), reverse=True)
        return tuple(item for item, _ in results)

    def get_unranked_suggestions(self, word: str) -> Tuple[str]:

        normalized = TurkishAlphabet.INSTANCE.normalize(re.sub("['’]", "", word))
        strings: Tuple[str] = self.decoder.get_suggestions(normalized, self.char_matcher)
        case_type = self.formatter.guess_case(word)
        if case_type == WordAnalysisSurfaceFormatter.CaseType.MIXED_CASE or case_type == \
                WordAnalysisSurfaceFormatter.CaseType.LOWER_CASE:
            case_type = WordAnalysisSurfaceFormatter.CaseType.DEFAULT_CASE

        results: Set[str] = set()
        for string in strings:
            analyses = self.morphology.analyze(string)
            for analysis in analyses:
                if analysis.is_unknown():
                    continue

                formatted = self.formatter.format_to_case(analysis, case_type, self.get_apostrophe(word))
                results.add(formatted)

        return tuple(results)

    def rank_with_unigram_probability(self, strings: Tuple[str], lm: SmoothLM) -> Tuple[str]:
        if lm is None:
            logger.warning("No language model provided, returning unranked results.")
            return strings
        else:
            results: List[Tuple[str, float]] = []
            for string in strings:
                w = self.normalize_for_lm(string)
                word_index = lm.vocabulary.index_of(w)
                results.append((w, lm.get_unigram_probability(word_index)))

            results.sort(key=itemgetter(1), reverse=True)
            return tuple(word for word, _ in results)

    @staticmethod
    def normalize_for_lm(s: str) -> str:
        return Turkish.capitalize(s) if s.find(chr(39)) > 0 else s.translate(TurkishAlphabet.INSTANCE.lower_map).lower()

    @staticmethod
    def get_apostrophe(inp: str) -> str:
        if inp.find(chr(8217)) > 0:
            return "’"
        else:
            return "'" if inp.find(chr(39)) > 0 else None
