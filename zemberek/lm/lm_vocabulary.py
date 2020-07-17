import logging

from struct import unpack
from typing import List, Dict, Tuple, BinaryIO

from zemberek.core.turkish import TurkishAlphabet

logger = logging.getLogger(__name__)


class LmVocabulary:
    DEFAULT_SENTENCE_BEGIN_MARKER = "<s>"
    DEFAULT_SENTENCE_END_MARKER = "</s>"
    DEFAULT_UNKNOWN_WORD = "<unk>"

    def __init__(self, f: BinaryIO):
        vocabulary_length, = unpack(">i", f.read(4))

        vocab: List[str] = []
        for i in range(vocabulary_length):
            utf_length, = unpack(">H", f.read(2))
            vocab.append(f.read(utf_length).decode("utf-8"))

        self.vocabulary_index_map: Dict[str, int] = {}
        self.unknown_word = None
        self.sentence_start = None
        self.unknown_word_index = -1
        self.sentence_start_index = -1
        self.sentence_end_index = -1
        self.sentence_end = None
        self.vocabulary = ()

        self.generate_map(vocab)

    def index_of(self, word: str) -> int:
        k = self.vocabulary_index_map.get(word)
        return self.unknown_word_index if k is None else k

    def size(self) -> int:
        return len(self.vocabulary)

    def to_indexes(self, words: Tuple[str, str]) -> Tuple[int, ...]:
        indexes: List[int] = []
        for word in words:
            if word not in self.vocabulary_index_map:
                indexes.append(self.unknown_word_index)
            else:
                indexes.append(self.vocabulary_index_map[word])
        return tuple(indexes)

    def generate_map(self, input_vocabulary: List[str]):
        index_counter = 0
        clean_vocab: List[str] = []

        for word in input_vocabulary:
            if word in self.vocabulary_index_map.keys():
                logger.warning("Language model vocabulary has duplicate item: " + word)
            else:
                if word.translate(TurkishAlphabet.INSTANCE.lower_map).lower() == "<unk>":
                    if self.unknown_word_index != -1:
                        logger.warning('Unknown word was already defined as {} but another matching token exist in the '
                                       'input vocabulary: {}'.format(self.unknown_word, word))
                    else:
                        self.unknown_word = word
                        self.unknown_word_index = index_counter
                elif word.translate(TurkishAlphabet.INSTANCE.lower_map).lower() == "<s>":
                    if self.sentence_start_index != -1:
                        logger.warning(f"Sentence start index was already defined as {self.sentence_start} but another "
                                       f"matching token exist in the input vocabulary: {word}")
                    else:
                        self.sentence_start = word
                        self.sentence_start_index = index_counter
                elif word.translate(TurkishAlphabet.INSTANCE.lower_map).lower() == "</s>":
                    if self.sentence_end_index != -1:
                        logger.warning(f"Sentence end index was already defined as {self.sentence_end} but another "
                                       f"matching token exist in the input vocabulary: {word})")
                    else:
                        self.sentence_end = word
                        self.sentence_end_index = index_counter

                self.vocabulary_index_map[word] = index_counter
                clean_vocab.append(word)
                index_counter += 1

        if self.unknown_word_index == -1:
            self.unknown_word = "<unk>"
            clean_vocab.append(self.unknown_word)
            self.vocabulary_index_map[self.unknown_word] = index_counter
            index_counter += 1
            logger.debug("Necessary special token " + self.unknown_word + " was not found in the vocabulary, it is "
                                                                          "added explicitly")

        self.unknown_word_index = self.vocabulary_index_map[self.unknown_word]

        if self.sentence_start_index == -1:
            self.sentence_start = "<s>"
            clean_vocab.append(self.sentence_start)
            self.vocabulary_index_map[self.sentence_start] = index_counter
            index_counter += 1
            logger.debug("Vocabulary does not contain sentence start token, it is added explicitly.")

        self.sentence_start_index = self.vocabulary_index_map[self.sentence_start]

        if self.sentence_end_index == -1:
            self.sentence_end = "</s>"
            clean_vocab.append(self.sentence_end)
            self.vocabulary_index_map[self.sentence_end] = index_counter

        self.sentence_end_index = self.vocabulary_index_map[self.sentence_end]
        self.vocabulary = tuple(clean_vocab)

    @staticmethod
    def load_from_data_input_stream(f: BinaryIO) -> 'LmVocabulary':
        return LmVocabulary(f)
