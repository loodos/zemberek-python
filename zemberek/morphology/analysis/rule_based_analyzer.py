from __future__ import annotations

import logging

from copy import deepcopy
from typing import List, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.morphotactics import TurkishMorphotactics

from zemberek.core.turkish import PhoneticAttribute, TurkishAlphabet
from zemberek.morphology.analysis.surface_transitions import SurfaceTransition
from zemberek.morphology.analysis.single_analysis import SingleAnalysis
from zemberek.morphology.analysis.search_path import SearchPath
from zemberek.morphology.analysis.attributes_helper import AttributesHelper

logger = logging.getLogger(__name__)


class RuleBasedAnalyzer:

    def __init__(self, morphotactics: TurkishMorphotactics):
        self.lexicon = morphotactics.get_root_lexicon()
        self.stem_transitions = morphotactics.get_stem_transitions()
        self.morphotactics = morphotactics
        self.debug_mode = False
        self.ascii_tolerant = False

    @staticmethod
    def instance(morphotactics: TurkishMorphotactics) -> 'RuleBasedAnalyzer':
        return RuleBasedAnalyzer(morphotactics)

    @staticmethod
    def ignore_diacritics_instance(morphotactics: TurkishMorphotactics) -> 'RuleBasedAnalyzer':
        analyzer = RuleBasedAnalyzer.instance(morphotactics)
        analyzer.ascii_tolerant = True
        return analyzer

    def analyze(self, inp: str) -> Tuple[SingleAnalysis, ...]:
        if self.debug_mode:
            raise NotImplementedError("Debug mode is not implemented")

        candidates = self.stem_transitions.get_prefix_matches(inp, self.ascii_tolerant)
        if self.debug_mode:
            raise NotImplementedError("Debug mode is not implemented")

        paths: List[SearchPath] = []

        for candidate in candidates:
            length = len(candidate.surface)
            tail = inp[length:]
            paths.append(SearchPath.initial_path(candidate, tail))

        result_paths: Tuple[SearchPath] = self.search(paths)
        result: List[SingleAnalysis] = []

        for path in result_paths:
            analysis: SingleAnalysis = SingleAnalysis.from_search_path(path)
            result.append(analysis)

        return tuple(result)

    def search(self, current_paths: List[SearchPath]) -> Tuple[SearchPath, ...]:
        if len(current_paths) > 30:
            current_paths = self.prune_cyclic_paths(current_paths)
        result = []

        while len(current_paths) > 0:
            all_new_paths = []
            for path in current_paths:

                if len(path.tail) == 0:
                    if path.terminal and PhoneticAttribute.CannotTerminate not in path.phonetic_attributes:
                        result.append(path)
                        continue
                    if self.debug_mode:
                        raise NotImplementedError

                new_paths = self.advance(path)
                all_new_paths.extend(new_paths)

            current_paths = all_new_paths

        return tuple(result)

    def advance(self, path: SearchPath) -> List[SearchPath]:
        new_paths: List[SearchPath] = []

        for transition in path.current_state.outgoing:
            # assert transition.__class__ == SuffixTransition
            suffix_transition = transition
            if len(path.tail) == 0 and suffix_transition.has_surface_form():
                # NO DEBUG
                continue
            else:
                surface = SurfaceTransition.generate_surface(suffix_transition, path.phonetic_attributes)
                tail_starts_with = TurkishAlphabet.INSTANCE.starts_with_ignore_diacritics(path.tail, surface) if\
                    self.ascii_tolerant else path.tail.startswith(surface)
                if not tail_starts_with:
                    if self.debug_mode:
                        raise NotImplementedError("Not implemented debug_mode")
                else:
                    if self.debug_mode:
                        raise NotImplementedError("Not implemented debug_mode")
                    if suffix_transition.can_pass(path):
                        if not suffix_transition.has_surface_form():
                            new_paths.append(path.get_copy(SurfaceTransition("", suffix_transition),
                                                           path.phonetic_attributes))
                        else:
                            surface_transition = SurfaceTransition(surface, suffix_transition)
                            tail_equals_surface = TurkishAlphabet.INSTANCE.equals_ignore_diacritics(path.tail, surface)\
                                if self.ascii_tolerant else path.tail == surface

                            attributes = deepcopy(path.phonetic_attributes) if tail_equals_surface else \
                                AttributesHelper.get_morphemic_attributes(surface, path.phonetic_attributes)
                            try:
                                attributes.remove(PhoneticAttribute.CannotTerminate)
                            except KeyError:
                                logger.debug("There is no CannotTerminate element in the set")
                            last_token = suffix_transition.get_last_template_token()
                            if last_token.type_ == SurfaceTransition.TemplateTokenType.LAST_VOICED:
                                attributes.add(PhoneticAttribute.ExpectsConsonant)
                            elif last_token.type_ == SurfaceTransition.TemplateTokenType.LAST_NOT_VOICED:
                                attributes.add(PhoneticAttribute.ExpectsVowel)
                                attributes.add(PhoneticAttribute.CannotTerminate)

                            p: SearchPath = path.get_copy(surface_transition, attributes)
                            new_paths.append(p)
        return new_paths

    @staticmethod
    def prune_cyclic_paths(tokens: List[SearchPath]) -> List[SearchPath]:
        def add_or_increment(dict_: Dict[str, int], key: str):
            if key in dict_.keys():
                dict_[key] += 1
                return dict_[key]
            else:
                dict_[key] = 1
                return 1

        result: List[SearchPath] = []

        for token in tokens:
            remove = False
            type_counts: Dict[str, int] = {}

            for node in token.transitions:
                if add_or_increment(type_counts, node.get_state().id_) > 3:
                    remove = True
                    break

            if not remove:
                result.append(token)

        return result
