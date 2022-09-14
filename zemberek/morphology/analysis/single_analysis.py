from __future__ import annotations

import numpy as np

from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.analysis.search_path import SearchPath


from zemberek.core.turkish import RootAttribute, SecondaryPos
from zemberek.morphology.lexicon import DictionaryItem
from zemberek.morphology.morphotactics import TurkishMorphotactics
from zemberek.morphology.morphotactics.morpheme import Morpheme


class SingleAnalysis:

    empty_morpheme_cache: Dict[Morpheme, 'SingleAnalysis.MorphemeData'] = {}

    def __init__(self, item: DictionaryItem, morpheme_data_list: List['SingleAnalysis.MorphemeData'],
                 group_boundaries: np.ndarray):
        self.item = item
        self.morpheme_data_list = morpheme_data_list
        self.group_boundaries = group_boundaries
        self.hash_ = 0
        self.hash_ = hash(self)

    def __str__(self):
        return self.format_string()

    def format_string(self) -> str:
        sb = [f"[{self.item.lemma}:{self.item.primary_pos.short_form}"]
        if self.item.secondary_pos != SecondaryPos.None_:
            sb.append(", " + self.item.secondary_pos.short_form)
        sb.extend(["] "] + self.format_morpheme_string())
        return ''.join(sb)

    def format_morpheme_string(self):
        surfaces = self.morpheme_data_list
        sb = [f"{self.get_stem()}:{surfaces[0].morpheme.id_}"]
        if len(surfaces) > 1 and not surfaces[1].morpheme.derivational_:
            sb.append("+")

        for i in range(1, len(surfaces)):
            s = surfaces[i]
            morpheme = s.morpheme
            if morpheme.derivational_:
                sb.append("|")
            if len(s.surface) > 0:
                sb.append(s.surface + ':')
            sb += s.morpheme.id_
            if s.morpheme.derivational_:
                sb.append('→')
            elif i < len(surfaces) - 1 and not surfaces[i+1].morpheme.derivational_:
                sb.append('+')

        return sb

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, SingleAnalysis):
            if self.hash_ != other.hash_:
                return False
            else:
                return False if self.item != other.item else self.morpheme_data_list == other.morpheme_data_list
        else:
            return False

    def __hash__(self):
        if self.hash_ != 0:
            return self.hash_
        else:
            result = hash(self.item)
            for h in self.morpheme_data_list:
                result = 31 * result + (hash(h) if h is not None else 0)
            result = 31 * result + self.hash_
            return result

    def is_runtime(self) -> bool:
        return self.item.has_attribute(RootAttribute.Runtime)

    def is_unknown(self) -> bool:
        return self.item.is_unknown()

    def get_ending(self) -> str:
        return ''.join([m_surface.surface for m_surface in self.morpheme_data_list[1:]])

    def get_stem(self) -> str:
        return self.morpheme_data_list[0].surface

    def surface_form(self) -> str:
        return self.get_stem() + self.get_ending()

    def get_morphemes(self) -> List[Morpheme]:
        return [s.morpheme for s in self.morpheme_data_list]

    def contains_informal_morpheme(self) -> bool:
        for m in self.morpheme_data_list:
            if m.morpheme.informal:
                return True
        return False

    def get_group(self, group_index: int) -> 'SingleAnalysis.MorphemeGroup':
        if group_index < 0 or group_index > self.group_boundaries.shape[0]:
            raise ValueError(f"There are only {self.group_boundaries.shape[0]} morpheme groups. "
                             f"But input is {group_index}")

        end_index = len(self.morpheme_data_list) if group_index == self.group_boundaries.shape[0] - 1 else \
            self.group_boundaries[group_index + 1]
        return SingleAnalysis.MorphemeGroup(self.morpheme_data_list[self.group_boundaries[group_index]: end_index])

    def contains_morpheme(self, morpheme: Morpheme) -> bool:
        for morpheme_data in self.morpheme_data_list:
            if morpheme_data.morpheme == morpheme:
                return True
        return False

    def copy_for(self, item: DictionaryItem, stem: str) -> 'SingleAnalysis':
        data: List['SingleAnalysis.MorphemeData'] = self.morpheme_data_list.copy()
        data[0] = SingleAnalysis.MorphemeData(data[0].morpheme, stem)
        return SingleAnalysis(item, data, self.group_boundaries.copy())

    @classmethod
    def unknown(cls, input_: str) -> 'SingleAnalysis':
        item = DictionaryItem.UNKNOWN
        s = cls.MorphemeData(Morpheme.UNKNOWN, input_)
        boundaries = np.asarray([0], dtype=np.int32)
        return cls(item, [s], boundaries)

    @staticmethod
    def dummy(inp: str, item: DictionaryItem) -> 'SingleAnalysis':
        s = SingleAnalysis.MorphemeData(Morpheme.UNKNOWN, inp)
        boundaries: np.ndarray = np.zeros(1, dtype=np.int32)
        return SingleAnalysis(item, [s], boundaries)

    @staticmethod
    def from_search_path(search_path: SearchPath) -> 'SingleAnalysis':
        morphemes: List['SingleAnalysis.MorphemeData'] = []
        derivation_count = 0

        for transition in search_path.transitions:
            if transition.is_derivative():
                derivation_count += 1

            morpheme = transition.get_morpheme()
            if morpheme != TurkishMorphotactics.nom and morpheme != TurkishMorphotactics.pnon:
                if len(transition.surface) == 0:
                    morpheme_data = SingleAnalysis.empty_morpheme_cache.get(morpheme)
                    if morpheme_data is None:
                        morpheme_data = SingleAnalysis.MorphemeData(morpheme, "")
                        SingleAnalysis.empty_morpheme_cache[morpheme] = morpheme_data

                    morphemes.append(morpheme_data)
                else:
                    morpheme_data = SingleAnalysis.MorphemeData(morpheme, transition.surface)
                    morphemes.append(morpheme_data)

        group_boundaries: np.ndarray = np.zeros(derivation_count + 1, dtype=np.int32)
        morpheme_counter = 0
        derivation_counter = 1

        for morpheme_data in morphemes:
            if morpheme_data.morpheme.derivational_:
                group_boundaries[derivation_counter] = morpheme_counter
                derivation_counter += 1

            morpheme_counter += 1

        item = search_path.get_dictionary_item()
        if item.has_attribute(RootAttribute.Dummy):
            item = item.reference_item

        return SingleAnalysis(item, morphemes, group_boundaries)

    class MorphemeData:
        def __init__(self, morpheme: Morpheme, surface: str):
            self.morpheme = morpheme
            self.surface = surface

        def __str__(self):
            return self.to_morpheme_string()

        def to_morpheme_string(self) -> str:
            return f"{self.surface_string()}{self.morpheme.id_}"

        def surface_string(self) -> str:
            return "" if len(self.surface) == 0 else f"{self.surface}:"

        def __eq__(self, other):
            if self is other:
                return True
            elif isinstance(other, SingleAnalysis.MorphemeData):
                return False if self.morpheme != other.morpheme else self.surface == other.surface
            else:
                return False

        def __hash__(self):
            result = hash(self.morpheme)
            result = 31 * result + hash(self.surface)
            return result

    class MorphemeGroup:
        def __init__(self, morphemes: List['SingleAnalysis.MorphemeData']):
            self.morphemes = morphemes

        def lexical_form(self) -> str:
            sb = [m.morpheme.id_ for m in self.morphemes]
            return ''.join(sb)
