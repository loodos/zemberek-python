from __future__ import annotations

import time
import logging
import os

from typing import Tuple, TYPE_CHECKING, List, Optional
from functools import lru_cache
from pkg_resources import resource_filename

if TYPE_CHECKING:
    from zemberek.tokenization.token import Token
    from zemberek.morphology.analysis.single_analysis import SingleAnalysis
    from zemberek.morphology.ambiguity.ambiguity_resolver import AmbiguityResolver

from zemberek.tokenization import TurkishTokenizer
from zemberek.core.turkish import TurkishAlphabet, StemAndEnding, PrimaryPos
from zemberek.core.text import TextUtil
from zemberek.morphology.analysis.word_analysis import WordAnalysis
from zemberek.morphology.analysis.sentence_analysis import SentenceAnalysis
from zemberek.morphology.analysis.rule_based_analyzer import RuleBasedAnalyzer
from zemberek.morphology.analysis.unidentified_token_analyzer import UnidentifiedTokenAnalyzer
from zemberek.morphology.generator import WordGenerator
from zemberek.morphology.lexicon import RootLexicon
from zemberek.morphology.morphotactics import TurkishMorphotactics, InformalTurkishMorphotactics
from zemberek.morphology.ambiguity.perceptron_ambiguity_resolver import PerceptronAmbiguityResolver

logger = logging.getLogger(__name__)


class TurkishMorphology:

    def __init__(self, builder: 'TurkishMorphology.Builder'):
        self.lexicon = builder.lexicon
        self.morphotactics = InformalTurkishMorphotactics(self.lexicon) if builder.informal_analysis \
            else TurkishMorphotactics(self.lexicon)
        self.analyzer = RuleBasedAnalyzer.ignore_diacritics_instance(self.morphotactics) if \
            builder.ignore_diacritics_in_analysis else RuleBasedAnalyzer.instance(self.morphotactics)
        self.unidentified_token_analyzer = UnidentifiedTokenAnalyzer(self.analyzer)
        self.tokenizer = builder.tokenizer
        self.word_generator = WordGenerator(self.morphotactics)

        self.use_unidentified_token_analyzer = builder.use_unidentifiedTokenAnalyzer

        if builder.ambiguity_resolver is None:
            resource_path = resource_filename("zemberek", os.path.join("resources", "ambiguity", "model-compressed"))
            try:
                self.ambiguity_resolver = PerceptronAmbiguityResolver.from_resource(resource_path)
            except IOError as e:
                logger.error(e)
                raise RuntimeError(f"Cannot initialize PerceptronAmbiguityResolver from resource {resource_path}")
        else:
            self.ambiguity_resolver = builder.ambiguity_resolver

    @staticmethod
    def builder(lexicon: RootLexicon) -> 'TurkishMorphology.Builder':
        return TurkishMorphology.Builder(lexicon)

    @staticmethod
    def create_with_defaults() -> 'TurkishMorphology':
        start_time = time.time()
        instance = TurkishMorphology.Builder(RootLexicon.get_default()).build()
        logger.info(f"TurkishMorphology instance initialized in {time.time() - start_time}")
        return instance

    @lru_cache(maxsize=250)
    def analyze(self, word: str = None, token: Token = None) -> WordAnalysis:
        return self.analyze_without_cache(word=word, token=token)

    @staticmethod
    def normalize_for_analysis(word: str) -> str:
        s = word.translate(TurkishAlphabet.INSTANCE.lower_map).lower()
        s = TurkishAlphabet.INSTANCE.normalize_circumflex(s)
        no_dot = s.replace(".", "")
        if len(no_dot) == 0:
            no_dot = s

        return TextUtil.normalize_apostrophes(no_dot)

    def analyze_sentence(self, sentence: str) -> List[WordAnalysis]:

        normalized = TextUtil.normalize_quotes_hyphens(sentence)
        result = [
            self.analyze(token=t) for t in self.tokenizer.tokenize(normalized)
        ]

        return result

    def disambiguate(self, sentence: str, sentence_analysis: List[WordAnalysis]) -> SentenceAnalysis:
        return self.ambiguity_resolver.disambiguate(sentence, sentence_analysis)

    def analyze_and_disambiguate(self, sentence: str) -> SentenceAnalysis:
        return self.disambiguate(sentence, self.analyze_sentence(sentence))

    def analyze_without_cache(self, word: str = None, token: Token = None) -> WordAnalysis:
        if word:
            tokens: Tuple[Token] = self.tokenizer.tokenize(word)
            return WordAnalysis(word, (), normalized_input=word) if len(tokens) != 1 else \
                self.analyze_without_cache(token=tokens[0])
        else:  # token is not None
            word = token.content  # equal to token.getText()
            s = self.normalize_for_analysis(word)
            if len(s) == 0:
                return WordAnalysis.EMPTY_INPUT_RESULT
            else:
                if TurkishAlphabet.INSTANCE.contains_apostrophe(s):
                    s = TurkishAlphabet.INSTANCE.normalize_apostrophe(s)
                    result = self.analyze_words_with_apostrophe(s)
                else:
                    result = self.analyzer.analyze(s)

                if len(result) == 0 and self.use_unidentified_token_analyzer:
                    result = self.unidentified_token_analyzer.analyze(token)

                if len(result) == 1 and result[0].item.is_unknown():
                    result = ()

                return WordAnalysis(word, normalized_input=s, analysis_results=result)

    def analyze_words_with_apostrophe(self, word: str) -> Tuple[SingleAnalysis, ...]:
        index = word.find(chr(39))
        if index > 0 and index != len(word) - 1:
            se = StemAndEnding(word[0:index], word[index + 1:])
            stem = TurkishAlphabet.INSTANCE.normalize(se.stem)
            without_quote = word.replace("'", "")
            no_quotes_parses = self.analyzer.analyze(without_quote)
            return () if len(no_quotes_parses) == 0 else \
                tuple(p for p in no_quotes_parses if p.item.primary_pos == PrimaryPos.Noun and
                      (p.contains_morpheme(TurkishMorphotactics.p3sg) or p.get_stem() == stem))
        else:
            return ()

    class Builder:
        use_unidentifiedTokenAnalyzer = True

        def __init__(self, lexicon: RootLexicon):
            self.tokenizer = TurkishTokenizer.DEFAULT
            self.lexicon = lexicon
            self.informal_analysis = False
            self.ignore_diacritics_in_analysis = False
            self.ambiguity_resolver: Optional['AmbiguityResolver'] = None

        def set_lexicon(self, lexicon: RootLexicon) -> 'TurkishMorphology.Builder':
            self.lexicon = lexicon
            return self

        def use_informal_analysis(self) -> 'TurkishMorphology.Builder':
            self.informal_analysis = True
            return self

        def ignore_diacritics_in_analysis_(self) -> 'TurkishMorphology.Builder':
            self.ignore_diacritics_in_analysis = True
            return self

        def build(self) -> 'TurkishMorphology':
            return TurkishMorphology(self)
