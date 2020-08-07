from zemberek.core.turkish.turkish_alphabet import TurkishAlphabet


class Turkish:
    alphabet = TurkishAlphabet.INSTANCE

    @staticmethod
    def capitalize(word: str) -> str:
        if len(word) != 0:
            if word[0] == "i":
                word = word[0].translate(Turkish.alphabet.upper_map) + word[1:].translate(Turkish.alphabet.lower_map).\
                    lower()
            else:
                word = word[0].upper() + word[1:].translate(Turkish.alphabet.lower_map).lower()
        return word
