import sys
import math
import numpy as np

from enum import Enum, auto
from struct import unpack
from math import log
from typing import List, Tuple, Optional

from zemberek.core.hash import Mphf, MultiLevelMphf, LargeNgramMphf
from zemberek.core.quantization import FloatLookup
from zemberek.lm import LmVocabulary
from zemberek.lm.compression.gram_data_array import GramDataArray


class SmoothLM:
    """
    SmoothLm is a compressed, optionally quantized, randomized back-off n-gram language model. It
    uses Minimal Perfect Hash functions for compression, This means actual n-gram values are not
    stored in the model.
    Detailed explanation can be found in original zemberek file
    """
    LOG_ZERO_FLOAT = -math.log(sys.float_info.max)

    def __init__(self, resource: str, log_base: float, unigram_weigth: float, unknown_backoff_penalty: float,
                 use_stupid_backoff: bool, stupid_backoff_alpha: float, ngram_key_file):
        with open(resource, "rb") as f:  # "zemberek/resources/lm-unigram.slm"
            self.version, = unpack('>i', f.read(4))
            self.type_int, = unpack('>i', f.read(4))
            self.log_base, = unpack('>d', f.read(8))
            self.order, = unpack('>i', f.read(4))

            if self.type_int == 0:
                self.type_ = SmoothLM.MphfType.SMALL
            else:
                self.type_ = SmoothLM.MphfType.LARGE

            self.counts = [0]
            for unigram_count in range(1, self.order + 1):
                count, = unpack('>i', f.read(4))
                self.counts.insert(unigram_count, count)
            self.counts = tuple(self.counts)

            self.probability_lookups = [FloatLookup(np.asarray([0.0], dtype=np.float32))]
            for unigram_count in range(1, self.order + 1):
                self.probability_lookups.insert(unigram_count, FloatLookup.get_lookup_from_double(f))
            self.probability_lookups = tuple(self.probability_lookups)

            self.backoff_lookups = [FloatLookup(np.asarray([0.0], dtype=np.float32))]
            for unigram_count in range(1, self.order):
                self.backoff_lookups.insert(unigram_count, FloatLookup.get_lookup_from_double(f))
            self.backoff_lookups = tuple(self.backoff_lookups)

            self.ngram_data = [None]
            for unigram_count in range(1, self.order + 1):
                self.ngram_data.insert(unigram_count, GramDataArray(f))
            self.ngram_data = tuple(self.ngram_data)

            unigram_count = self.ngram_data[1].count

            self.unigram_probs = np.zeros((unigram_count,), dtype=np.float32)
            if self.order > 1:
                self.unigram_backoffs = np.zeros((unigram_count,), dtype=np.float32)
            else:
                self.unigram_backoffs = np.zeros((1,), dtype=np.float32)

            for vocabulary_size in range(unigram_count):
                i = self.ngram_data[1].get_probability_rank(vocabulary_size)
                self.unigram_probs[vocabulary_size] = self.probability_lookups[1].get(i)
                if self.order > 1:
                    backoff = self.ngram_data[1].get_back_off_rank(vocabulary_size)
                    self.unigram_backoffs[vocabulary_size] = self.backoff_lookups[1].get(backoff)

            if self.type_ == SmoothLM.MphfType.LARGE:
                self.mphfs: List[Optional[Mphf]] = [None] * (self.order + 1)
                for i in range(2, self.order + 1):
                    self.mphfs.insert(i, LargeNgramMphf.deserialize(f))
                self.mphfs: Tuple[Optional[Mphf]] = tuple(self.mphfs)
            else:
                # this part doesn't work in default settings. It will be implemented if needed
                raise NotImplementedError

            self.vocabulary: LmVocabulary = LmVocabulary.load_from_data_input_stream(f)
            vocabulary_size = self.vocabulary.size()
            if vocabulary_size > unigram_count:
                self.ngram_data[1].count = vocabulary_size
                self.unigram_probs = self.unigram_probs[:vocabulary_size] if len(self.unigram_probs) >= vocabulary_size\
                    else np.pad(self.unigram_probs, (0, vocabulary_size - len(self.unigram_probs)))
                self.unigram_backoffs = self.unigram_backoffs[:vocabulary_size] \
                    if len(self.unigram_backoffs) >= vocabulary_size \
                    else np.pad(self.unigram_backoffs, (0, vocabulary_size - len(self.unigram_backoffs)))

                for i in range(unigram_count, vocabulary_size, 1):
                    self.unigram_probs[i] = -20.0
                    self.unigram_backoffs[i] = 0.0

        self.unigram_weight = unigram_weigth
        self.unknown_backoff_penalty = unknown_backoff_penalty
        self.use_stupid_backoff = use_stupid_backoff
        self.stupid_backoff_alpha = stupid_backoff_alpha

        if log_base != 10.0:
            self.change_log_base(log_base)
            self.stupid_backoff_log_alpha = (math.log(stupid_backoff_alpha) / math.log(log_base)) * 1.0
        else:
            self.stupid_backoff_log_alpha = float(log(stupid_backoff_alpha) / log(10.0))

        # self.log_base = log_base
        if unigram_weigth != 1.0:
            raise NotImplementedError("Unigram smoothing is not implemented, it will be if needed")

        self.ngram_ids = None
        if ngram_key_file:
            raise NotImplementedError("Loading n-gram id data is not implemented, it will be if needed")

    def change_log_base(self, new_base: float):
        FloatLookup.change_base(self.unigram_probs, self.log_base, new_base)
        FloatLookup.change_base(self.unigram_backoffs, self.log_base, new_base)

        for i in range(2, len(self.probability_lookups)):

            self.probability_lookups[i].change_self_base(self.log_base, new_base)
            if i < len(self.backoff_lookups) - 1:
                self.backoff_lookups[i].change_self_base(self.log_base, new_base)

        self.log_base = np.float32(new_base)

    def ngram_exists(self, word_indexes: Tuple[int, ...]) -> bool:
        if len(word_indexes) < 1 or len(word_indexes) > self.order:
            raise ValueError(f"Amount of tokens must be between 1 and {self.order} But it is {(len(word_indexes))}")
        order = len(word_indexes)
        if order == 1:
            return 0 <= word_indexes[0] < len(self.unigram_probs)
        quick_hash: int = MultiLevelMphf.hash_(word_indexes, -1)
        index = self.mphfs[order].get_(word_indexes, quick_hash)
        if self.ngram_ids is None:
            return self.ngram_data[order].check_finger_print(quick_hash, index)
        return self.ngram_ids.exists(word_indexes, index)

    def get_unigram_probability(self, id_: int) -> float:
        return self.get_probability((id_,))

    def get_probability(self, word_indexes: Tuple[int, ...]) -> float:
        n = len(word_indexes)
        if n == 1:
            return self.unigram_probs[word_indexes[0]]
        elif n == 2:
            return self.get_bigram_probability(word_indexes[0], word_indexes[1])
        elif n == 3:
            return self.get_tri_gram_probability(word_indexes)
        else:
            raise NotImplementedError()

    def get_tri_gram_probability(self, w: Tuple[int, ...]) -> float:
        finger_print = MultiLevelMphf.hash_(w, seed=-1)
        n_gram_index = self.mphfs[3].get_(w, finger_print)
        if not self.ngram_data[3].check_finger_print(finger_print, n_gram_index):
            return self.get_bigram_probability_value(w[0], w[1]) + self.get_bigram_probability_value(w[1], w[2])
        else:
            return self.probability_lookups[3].get(self.ngram_data[3].get_probability_rank(n_gram_index))

    def get_bigram_probability(self, w0: int, w1: int) -> float:
        prob = self.get_bigram_probability_value(w0, w1)
        if prob == self.LOG_ZERO_FLOAT:
            if self.use_stupid_backoff:
                return self.stupid_backoff_log_alpha + self.unigram_probs[w1]
            else:
                return self.unigram_backoffs[w0] + self.unigram_probs[w1]
        else:
            return prob

    def get_bigram_probability_value(self, w0: int, w1: int) -> float:
        quick_hash = MultiLevelMphf.hash_((w0, w1), -1)
        index = self.mphfs[2].get_((w0, w1), quick_hash)

        if self.ngram_data[2].check_finger_print(quick_hash, index):
            return self.probability_lookups[2].get(self.ngram_data[2].get_probability_rank(index))
        else:
            return self.LOG_ZERO_FLOAT

    @staticmethod
    def builder(resource: str) -> 'SmoothLM.Builder':
        return SmoothLM.Builder(resource)

    class Builder:
        def __init__(self, resource: str):
            self._log_base = 10.0
            self._unknown_backoff_penalty = 0.0
            self._unigram_weight = 1.0
            self._use_stupid_backoff = False
            self._stupid_backoff_alpha = 0.4
            self.resource = resource
            self.ngram_ids = None

        def log_base(self, log_base: float) -> 'SmoothLM.Builder':
            self._log_base = log_base
            return self

        def build(self) -> 'SmoothLM':
            return SmoothLM(self.resource, self._log_base, self._unigram_weight, self._unknown_backoff_penalty,
                            self._use_stupid_backoff, self._stupid_backoff_alpha, self.ngram_ids)

    class MphfType(Enum):
        SMALL = auto()
        LARGE = auto()
