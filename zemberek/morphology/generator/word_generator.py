from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.morphotactics import TurkishMorphotactics
    from zemberek.morphology.morphotactics.stem_transition import StemTransition
    from zemberek.morphology.morphotactics.suffix_transition import SuffixTransition
    from zemberek.morphology.morphotactics.morpheme import Morpheme
    from zemberek.morphology.lexicon import DictionaryItem

from zemberek.core.turkish import PhoneticAttribute
from zemberek.morphology.analysis.single_analysis import SingleAnalysis
from zemberek.morphology.analysis.search_path import SearchPath
from zemberek.morphology.analysis.surface_transitions import SurfaceTransition
from zemberek.morphology.analysis.attributes_helper import AttributesHelper


class WordGenerator:

    def __init__(self, morphotactics: TurkishMorphotactics):
        self.morphotactics = morphotactics
        self.stem_transitions = morphotactics.stem_transitions

    def generate(self, item: DictionaryItem = None, morphemes: Tuple[Morpheme, ...] = None,
                 candidates: Tuple[StemTransition, ...] = None) -> Tuple['WordGenerator.Result', ...]:
        if item:
            candidates_st: Tuple[StemTransition, ...] = self.stem_transitions.get_transitions_for_item(item)
            return self.generate(candidates=candidates_st, morphemes=morphemes)
        # no item means generate(List<StemTransition> candidates, List<Morpheme> morphemes) is called
        paths: List['WordGenerator.GenerationPath'] = []

        for candidate in candidates:
            search_path: SearchPath = SearchPath.initial_path(candidate, " ")
            # morphemes_in_path: Tuple[Morpheme]
            if len(morphemes) > 0:
                if morphemes[0] == search_path.current_state.morpheme:
                    morphemes_in_path = morphemes[1:]
                else:
                    morphemes_in_path = morphemes
            else:
                morphemes_in_path = ()

            paths.append(WordGenerator.GenerationPath(search_path, morphemes_in_path))

        # search graph
        result_paths: Tuple['WordGenerator.GenerationPath'] = self.search(paths)
        result: List['WordGenerator.Result'] = []

        for path in result_paths:
            analysis = SingleAnalysis.from_search_path(path.path)
            result.append(WordGenerator.Result(analysis.surface_form(), analysis))

        return tuple(result)

    def search(self, current_paths: List['WordGenerator.GenerationPath']) -> Tuple['WordGenerator.GenerationPath', ...]:
        result: List['WordGenerator.GenerationPath'] = []

        while len(current_paths) > 0:
            all_new_paths: List['WordGenerator.GenerationPath'] = []

            for path in current_paths:
                if len(path.morphemes) == 0:
                    if path.path.terminal and PhoneticAttribute.CannotTerminate not in path.path.phonetic_attributes:
                        result.append(path)
                        continue

                new_paths: List['WordGenerator.GenerationPath'] = self.advance(path)
                all_new_paths.extend(new_paths)
            current_paths = all_new_paths

        return tuple(result)

    @staticmethod
    def advance(g_path: 'WordGenerator.GenerationPath') -> List['WordGenerator.GenerationPath']:
        new_paths: List['WordGenerator.GenerationPath'] = []
        for transition in g_path.path.current_state.outgoing:
            suffix_transition = transition
            if len(g_path.morphemes) == 0 and suffix_transition.has_surface_form():
                continue

            if not g_path.matches(suffix_transition):
                continue

            if not suffix_transition.can_pass(g_path.path):
                continue

            if not suffix_transition.has_surface_form():
                p_copy: SearchPath = g_path.path.get_copy_for_generation(SurfaceTransition("", suffix_transition),
                                                                         g_path.path.phonetic_attributes)
                new_paths.append(g_path.copy_(p_copy))
                continue

            surface = SurfaceTransition.generate_surface(suffix_transition, g_path.path.phonetic_attributes)
            surface_transition = SurfaceTransition(surface, suffix_transition)
            attributes = AttributesHelper.get_morphemic_attributes(surface, g_path.path.phonetic_attributes)

            attributes.discard(PhoneticAttribute.CannotTerminate)

            last_token: SurfaceTransition.SuffixTemplateToken = suffix_transition.get_last_template_token()
            if last_token.type_ == SurfaceTransition.TemplateTokenType.LAST_VOICED:
                attributes.add(PhoneticAttribute.ExpectsConsonant)
            elif last_token.type_ == SurfaceTransition.TemplateTokenType.LAST_NOT_VOICED:
                attributes.add(PhoneticAttribute.ExpectsVowel)
                attributes.add(PhoneticAttribute.CannotTerminate)

            p: SearchPath = g_path.path.get_copy_for_generation(surface_transition, attributes)
            new_paths.append(g_path.copy_(p))
        return new_paths

    class Result:
        def __init__(self, surface: str, analysis: SingleAnalysis):
            self.surface = surface
            self.analysis = analysis

        def __str__(self):
            return self.surface + "-" + str(self.analysis)

    class GenerationPath:
        def __init__(self, path: SearchPath, morphemes: Tuple[Morpheme]):
            self.path = path
            self.morphemes = morphemes

        def copy_(self, path: SearchPath) -> 'WordGenerator.GenerationPath':
            last_transition: SurfaceTransition = path.get_last_transition()
            m: Morpheme = last_transition.get_morpheme()

            if len(last_transition.surface) == 0:
                if len(self.morphemes) == 0:
                    return WordGenerator.GenerationPath(path, self.morphemes)
                if m == self.morphemes[0]:
                    return WordGenerator.GenerationPath(path, self.morphemes[1:])
                else:
                    return WordGenerator.GenerationPath(path, self.morphemes)

            if m != self.morphemes[0]:
                raise Exception("Cannot generate Generation copy because transition morpheme and first morpheme to "
                                "consume does not match.")
            return WordGenerator.GenerationPath(path, self.morphemes[1:])

        def matches(self, transition: SuffixTransition):
            if not transition.has_surface_form():
                return True
            if len(self.morphemes) > 0 and transition.to.morpheme == self.morphemes[0]:
                return True
            return False
