from typing import List, Union, Tuple
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ConsoleErrorListener
from antlr4.Token import Token as Token_

from zemberek.tokenization.token import Token
from zemberek.tokenization.antlr.turkish_lexer import TurkishLexer


class TurkishTokenizer:

    DEFAULT: Union['TurkishTokenizer', None] = None
    IGNORING_ERROR_LISTENER = ConsoleErrorListener()

    def __init__(self, accepted_type_bits: int):
        self.accepted_type_bits = accepted_type_bits

    def tokenize(self, word: str) -> Tuple[Token, ...]:
        return self.get_all_tokens(self.lexer_instance(InputStream(word)))

    def get_all_tokens(self, lexer: TurkishLexer) -> Tuple[Token, ...]:
        tokens = []

        token: Token_ = lexer.nextToken()
        while token.type != -1:
            type_: Token.Type = self.convert_type(token)
            if not self.type_ignored(type_):
                tokens.append(self.convert(token))
            token = lexer.nextToken()
        return tuple(tokens)

    @staticmethod
    def convert(token: Token_) -> Token:
        return Token(token.text, TurkishTokenizer.convert_type(token), token.start, token.stop)

    def type_ignored(self, i: Token.Type) -> bool:
        return (self.accepted_type_bits & 1 << (i.value - 1)) == 0

    @staticmethod
    def convert_type(token: Token_) -> Token.Type:
        if token.type == 1:
            return Token.Type.Abbreviation
        elif token.type == 2:
            return Token.Type.SpaceTab
        elif token.type == 3:
            return Token.Type.NewLine
        elif token.type == 4:
            return Token.Type.Time
        elif token.type == 5:
            return Token.Type.Date
        elif token.type == 6:
            return Token.Type.PercentNumeral
        elif token.type == 7:
            return Token.Type.Number
        elif token.type == 8:
            return Token.Type.URL
        elif token.type == 9:
            return Token.Type.Email
        elif token.type == 10:
            return Token.Type.HashTag
        elif token.type == 11:
            return Token.Type.Mention
        elif token.type == 12:
            return Token.Type.MetaTag
        elif token.type == 13:
            return Token.Type.Emoticon
        elif token.type == 14:
            return Token.Type.RomanNumeral
        elif token.type == 15:
            return Token.Type.AbbreviationWithDots
        elif token.type == 16:
            return Token.Type.Word
        elif token.type == 17:
            return Token.Type.WordAlphanumerical
        elif token.type == 18:
            return Token.Type.WordWithSymbol
        elif token.type == 19:
            return Token.Type.Punctuation
        elif token.type == 20:
            return Token.Type.UnknownWord
        elif token.type == 21:
            return Token.Type.Unknown
        else:
            raise TypeError("Unidentified token type = " + token.text)

    @staticmethod
    def lexer_instance(input_stream: InputStream) -> TurkishLexer:
        lexer = TurkishLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(TurkishTokenizer.IGNORING_ERROR_LISTENER)
        return lexer

    @staticmethod
    def builder() -> 'TurkishTokenizer.Builder':
        return TurkishTokenizer.Builder()

    class Builder:
        def __init__(self):
            self.accepted_type_bits = -1

        def accept_all(self) -> 'TurkishTokenizer.Builder':
            self.accepted_type_bits = -1
            return self

        def ignore_types(self, types: List[Token.Type]) -> 'TurkishTokenizer.Builder':
            for i in types:
                ordinal = i.value - 1
                self.accepted_type_bits &= ~(1 << ordinal)
            return self

        def build(self) -> 'TurkishTokenizer':
            return TurkishTokenizer(self.accepted_type_bits)


TurkishTokenizer.DEFAULT = TurkishTokenizer.builder().accept_all().ignore_types([Token.Type.NewLine,
                                                                                 Token.Type.SpaceTab]).build()
