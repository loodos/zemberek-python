import math

from pkg_resources import resource_filename
from typing import List, Tuple, Dict, FrozenSet, Set, Union, OrderedDict as ODict

import os
import numpy as np
from collections import OrderedDict

from zemberek.core.turkish import TurkishAlphabet, SecondaryPos
from zemberek.lm import SmoothLM
from zemberek.morphology import TurkishMorphology
from zemberek.morphology.analysis.word_analysis import WordAnalysis
from zemberek.morphology.analysis.informal_analysis_converter import InformalAnalysisConverter
from zemberek.morphology.generator import WordGenerator
from zemberek.tokenization.turkish_tokenizer import TurkishTokenizer
from zemberek.tokenization.token import Token
from zemberek.normalization.stem_ending_graph import StemEndingGraph
from zemberek.normalization.character_graph_decoder import CharacterGraphDecoder
from zemberek.normalization.turkish_spell_checker import TurkishSpellChecker
from zemberek.normalization.deasciifier.deasciifier import Deasciifier


def load_replacements() -> Dict[str, str]:
    with open(
            resource_filename("zemberek", os.path.join("resources", "normalization", "multi-word-replacements.txt")),
            "r",
            encoding="utf-8"
    ) as f:
        replacements: Dict[str, str] = {}
        for line in f:
            tokens = line.replace('\n', "").split("=")
            replacements[tokens[0].strip()] = tokens[1].strip()
    return replacements


def load_no_split() -> FrozenSet[str]:
    with open(
            resource_filename("zemberek", os.path.join("resources", "normalization", "no-split.txt")),
            "r",
            encoding="utf-8"
    ) as f:
        s = set()
        for line in f:
            if len(line.replace('\n', "").strip()) > 0:
                s.add(line.replace('\n', "").strip())
    return frozenset(s)


def load_common_split() -> Dict[str, str]:
    common_splits: Dict[str, str] = {}
    with open(
            resource_filename("zemberek", os.path.join("resources", "normalization", "split.txt")),
            "r",
            encoding="utf-8"
    ) as f:
        for line in f:
            tokens = line.replace('\n', "").split('-')
            common_splits[tokens[0].strip()] = tokens[1].strip()
    return common_splits


def load_multimap(resource: str) -> ODict[str, Tuple[str]]:
    with open(resource, "r", encoding="utf-8") as f:
        lines: List[str] = f.read().split('\n')
    multimap: OrderedDict[str, Tuple[str, ...]] = OrderedDict()
    for i, line in enumerate(lines):
        if len(line.strip()) == 0:
            continue
        index = line.find("=")
        if index < 0:
            raise Exception(f"Line needs to have `=` symbol. But it is: {i} - {line}")
        key, value = line[0:index].strip(), line[index + 1:].strip()
        if value.find(',') >= 0:
            if key in multimap.keys():
                multimap[key] = tuple(value.split(','))
        else:
            if key in multimap.keys():
                multimap[key] = multimap[key] + (value,)
            else:
                multimap[key] = (value,)
    return multimap


class TurkishSentenceNormalizer:
    START: 'TurkishSentenceNormalizer.Candidate'
    END: 'TurkishSentenceNormalizer.Candidate'
    END_CANDIDATES: 'TurkishSentenceNormalizer.Candidates'

    def __init__(self, morphology: TurkishMorphology):
        self.morphology = morphology
        self.analysis_converter: InformalAnalysisConverter = InformalAnalysisConverter(morphology.word_generator)
        self.lm: SmoothLM = SmoothLM.builder(resource_filename("zemberek", os.path.join("resources", "lm.2gram.slm"))). \
            log_base(np.e).build()

        graph = StemEndingGraph(morphology)
        decoder = CharacterGraphDecoder(graph.stem_graph)
        self.spell_checker = TurkishSpellChecker(morphology, decoder=decoder,
                                                 matcher=CharacterGraphDecoder.DIACRITICS_IGNORING_MATCHER)

        self.replacements: Dict[str, str] = load_replacements()
        self.no_split_words: FrozenSet[str] = load_no_split()
        self.common_splits = load_common_split()

        with open(
                resource_filename("zemberek", os.path.join("resources", "normalization", "question-suffixes.txt")),
                "r",
                encoding="utf-8"
        ) as f:
            lines = f.read().split('\n')
        del f

        self.common_connected_suffixes: FrozenSet[str] = frozenset(lines)
        self.always_apply_deasciifier = False

        self.lookup_manual: Dict[str, Tuple[str]] = load_multimap(
            resource_filename("zemberek", os.path.join("resources", "normalization", "candidates-manual.txt")))
        self.lookup_from_graph: Dict[str, Tuple[str]] = load_multimap(
            resource_filename("zemberek", os.path.join("resources", "normalization", "lookup-from-graph.txt"))
        )
        self.lookup_from_ascii: Dict[str, Tuple[str]] = load_multimap(
            resource_filename("zemberek", os.path.join("resources", "normalization", "ascii-map.txt")))
        for s in self.lookup_manual.keys():
            try:
                self.lookup_from_graph.pop(s)
            except KeyError:
                pass

        self.informal_ascii_tolerant_morphology = TurkishMorphology.builder(morphology.lexicon) \
            .use_informal_analysis().ignore_diacritics_in_analysis_().build()

    def normalize(self, sentence: str) -> str:
        processed = self.pre_process(sentence)

        tokens: Tuple[Token] = tuple(TurkishTokenizer.DEFAULT.tokenize(processed))

        candidates_list: List['TurkishSentenceNormalizer.Candidates'] = []

        candidates: List[str] = []
        candidates_set: Set[str] = set()

        for i, current_token in enumerate(tokens):
            current = current_token.content
            next_ = None if i == len(tokens) - 1 else tokens[i + 1].content
            previous = None if i == 0 else tokens[i - 1].content

            candidates.clear()
            candidates_set.clear()

            for c in self.lookup_manual.get(current, ()) + self.lookup_from_graph.get(current, ()) + \
                    self.lookup_from_ascii.get(current, ()):
                if c not in candidates_set:
                    candidates.append(c)
                    candidates_set.add(c)

            # candidates.update(self.lookup_manual.get(current, ()))
            # candidates.update(self.lookup_from_graph.get(current, ()))
            # candidates.update(self.lookup_from_ascii.get(current, ()))

            analyses: WordAnalysis = self.informal_ascii_tolerant_morphology.analyze(current)

            for analysis in analyses:
                if analysis.contains_informal_morpheme():
                    result: Union[WordGenerator.Result, TurkishSentenceNormalizer.Candidates]
                    result = self.analysis_converter.convert(current, analysis)
                    if result is not None and result.surface not in candidates_set:
                        candidates.append(result.surface)
                        candidates_set.add(result.surface)
                else:
                    results: Tuple[WordGenerator.Result] = self.morphology.word_generator.generate(
                        item=analysis.item, morphemes=analysis.get_morphemes()
                    )
                    for result in results:
                        if result.surface not in candidates_set:
                            candidates_set.add(result.surface)
                            candidates.append(result.surface)

            if len(analyses.analysis_results) == 0 and len(current) > 3:
                spell_candidates = self.spell_checker.suggest_for_word_for_normalization(
                    current, previous, next_, self.lm
                )
                if len(spell_candidates) > 3:
                    spell_candidates = spell_candidates[:3]

                candidates.extend([c for c in spell_candidates if c not in candidates_set])
                candidates_set.update(spell_candidates)

            if len(candidates) == 0 or self.morphology.analyze(current).is_correct():
                if current not in candidates_set:
                    candidates_set.add(current)
                    candidates.append(current)

            result = TurkishSentenceNormalizer.Candidates(current_token.content,
                                                          tuple(TurkishSentenceNormalizer.Candidate(s) for
                                                                s in candidates))
            candidates_list.append(result)

        return ' '.join(self.decode(candidates_list))

    def decode(self, candidates_list: List['TurkishSentenceNormalizer.Candidates']) -> Tuple[str]:

        current: List['TurkishSentenceNormalizer.Hypothesis'] = []
        next_: List['TurkishSentenceNormalizer.Hypothesis'] = []

        candidates_list.append(TurkishSentenceNormalizer.END_CANDIDATES)

        initial = TurkishSentenceNormalizer.Hypothesis()
        lm_order = self.lm.order
        initial.history = [TurkishSentenceNormalizer.START] * (lm_order - 1)
        initial.current = TurkishSentenceNormalizer.START
        initial.score = np.float32(0.)
        current.append(initial)

        for candidates in candidates_list:
            for h in current:
                for c in candidates.candidates:
                    new_hyp = TurkishSentenceNormalizer.Hypothesis()
                    hist = [None] * (lm_order - 1)
                    if lm_order > 2:
                        hist = h.history[1: lm_order]
                    hist[-1] = h.current
                    new_hyp.current = c
                    new_hyp.history = hist
                    new_hyp.previous = h

                    indexes = [0] * lm_order
                    for j in range(lm_order - 1):
                        indexes[j] = self.lm.vocabulary.index_of(hist[j].content)

                    indexes[-1] = self.lm.vocabulary.index_of(c.content)
                    score = self.lm.get_probability(tuple(indexes))

                    new_hyp.score = np.float32(h.score + score)

                    try:
                        idx = next_.index(new_hyp)
                        next_[idx] = new_hyp if new_hyp.score > next_[idx].score else next_[idx]
                    except ValueError:
                        next_.append(new_hyp)

            current = next_
            next_ = []

        best: 'TurkishSentenceNormalizer.Hypothesis' = self.get_best(current)
        seq: List[str] = []
        h = best
        h = h.previous
        while h and h.current != TurkishSentenceNormalizer.START:
            seq.append(h.current.content)
            h = h.previous

        return tuple(reversed(seq))

    @staticmethod
    def get_best(li: List['TurkishSentenceNormalizer.Hypothesis']) -> 'TurkishSentenceNormalizer.Hypothesis':
        best = None
        for t in li:
            if t:
                if not best or t.score > best.score:
                    best = t
        return best

    def pre_process(self, sentence: str) -> str:
        sentence = sentence.translate(TurkishAlphabet.lower_map).lower()
        tokens: Tuple[Token] = TurkishTokenizer.DEFAULT.tokenize(sentence)
        s: str = self.replace_common(tokens)
        tokens: Tuple[Token] = TurkishTokenizer.DEFAULT.tokenize(s)
        s = self.combine_necessary_words(tokens)
        tokens: Tuple[Token] = TurkishTokenizer.DEFAULT.tokenize(s)
        s = self.split_necessary_words(tokens, use_look_up=False)
        if self.always_apply_deasciifier or self.probably_requires_deasciifier(s):
            deasciifier = Deasciifier(s)
            s = deasciifier.convert_to_turkish()
        tokens: Tuple[Token] = TurkishTokenizer.DEFAULT.tokenize(s)
        s = self.combine_necessary_words(tokens)
        tokens: Tuple[Token] = TurkishTokenizer.DEFAULT.tokenize(s)
        return self.split_necessary_words(tokens, use_look_up=True)

    def split_necessary_words(self, tokens: Tuple[Token], use_look_up: bool) -> str:
        result: List[str] = []
        for token in tokens:
            text = token.content
            if self.is_word(token):
                result.append(self.separate_common(text, use_look_up))
            else:
                result.append(text)

        return ' '.join(result)

    def separate_common(self, inp: str, use_look_up: bool) -> str:
        if inp in self.no_split_words:
            return inp
        if use_look_up and inp in self.common_splits:
            return self.common_splits[inp]

        if not self.has_regular_analysis(inp):
            for i in range(len(inp)):
                tail = inp[i:]
                if tail in self.common_connected_suffixes:
                    head = inp[0:i]
                    if len(tail) < 3:
                        if not self.lm.ngram_exists(self.lm.vocabulary.to_indexes((head, tail))):
                            return inp

                    if self.has_regular_analysis(head):
                        return f"{head} {tail}"
                    else:
                        return inp
        return inp

    @staticmethod
    def probably_requires_deasciifier(sentence: str) -> bool:
        turkish_spec_count = 0
        for c in sentence:
            if c != 'ı' and c != 'I' and TurkishAlphabet.INSTANCE.is_turkish_specific(c):
                turkish_spec_count += 1
        ratio = turkish_spec_count * 1. / len(sentence)
        return ratio < 0.1

    def combine_necessary_words(self, tokens: Tuple[Token]) -> str:
        result: List[str] = []
        combined = False
        for i in range(len(tokens) - 1):
            first: Token = tokens[i]
            second: Token = tokens[i + 1]
            first_s = first.content
            second_s = second.content
            if self.is_word(first) and self.is_word(second):
                if combined:
                    combined = False
                else:
                    c = self.combine_common(first_s, second_s)
                    if len(c) > 0:
                        result.append(c)
                        combined = True
                    else:
                        result.append(first.content)
                        combined = False
            else:
                combined = False
                result.append(first_s)

        if not combined:
            result.append(tokens[-1].content)
        return ' '.join(result)

    def combine_common(self, i1: str, i2: str) -> str:
        combined = i1 + i2
        if i2.startswith("'") or i2.startswith("bil"):
            w: WordAnalysis = self.morphology.analyze(combined)
            if self.has_analysis(w):
                return combined

        if not self.has_regular_analysis(i2):
            w: WordAnalysis = self.morphology.analyze(combined)
            if self.has_analysis(w):
                return combined
        return ""

    def has_regular_analysis(self, s: str) -> bool:
        a: WordAnalysis = self.morphology.analyze(s)
        for s in a:
            if (not s.is_unknown()) and (not s.is_runtime()) and s.item.secondary_pos != SecondaryPos.ProperNoun \
                    and s.item.secondary_pos != SecondaryPos.Abbreviation:
                return True
        return False

    @staticmethod
    def has_analysis(w: WordAnalysis) -> bool:
        for s in w:
            if (not s.is_runtime()) and (not s.is_unknown()):
                return True
        return False

    @staticmethod
    def is_word(token: Token) -> bool:
        typ: Token.Type = token.type_
        return typ == Token.Type.Word or typ == Token.Type.WordWithSymbol or typ == Token.Type.WordAlphanumerical \
               or typ == Token.Type.UnknownWord

    def replace_common(self, tokens: Tuple[Token]) -> str:
        result: List[str] = []
        for token in tokens:
            text = token.content
            result.append(self.replacements.get(text, text))
        return ' '.join(result)

    class Hypothesis:
        def __init__(self):
            self.history: Union[List['TurkishSentenceNormalizer.Candidate'], None] = None
            self.current: Union['TurkishSentenceNormalizer.Candidate', None] = None
            self.previous: Union['TurkishSentenceNormalizer.Hypothesis', None] = None
            self.score: Union[np.float32, None] = None

        def __eq__(self, other):
            if self is other:
                return True
            if isinstance(other, TurkishSentenceNormalizer.Hypothesis):
                return False if self.history != other.history else self.current == other.current
            return False

        def __hash__(self):
            result = 0
            for c in self.history:
                result = 31 * result + (hash(c) if c else 0)
            result = 31 * result + hash(self.current)
            return result

        def __str__(self):
            return "Hypothesis{history=" + f"{' '.join([str(s) for s in self.history])}" + f", current={self.current}" \
                                                                                           f", score={self.score}" + '}'

    class Candidate:
        def __init__(self, content: str):
            self.content = content
            self.score = np.float32(1.0)

        def __eq__(self, other):
            if self is other:
                return True
            if isinstance(other, TurkishSentenceNormalizer.Candidate):
                return self.content == other.content
            return False

        def __hash__(self):
            return hash(self.content)

        def __str__(self):
            return "Candidate{content='" + self.content + f"', score={self.score}" + '}'

    class Candidates:
        def __init__(self, word: str, candidates: Tuple['TurkishSentenceNormalizer.Candidate']):
            self.word = word
            self.candidates = candidates

        def __str__(self):
            return "Candidates{word='" + self.word + "', candidates=" + ' '.join(str(self.candidates)) + '}'


TurkishSentenceNormalizer.START = TurkishSentenceNormalizer.Candidate(content="<s>")
TurkishSentenceNormalizer.END = TurkishSentenceNormalizer.Candidate(content="</s>")
TurkishSentenceNormalizer.END_CANDIDATES = TurkishSentenceNormalizer.Candidates(word="</s>",
                                                                                candidates=(
                                                                                    TurkishSentenceNormalizer.END,
                                                                                ))
