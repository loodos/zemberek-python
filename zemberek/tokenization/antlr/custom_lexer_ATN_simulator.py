from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from antlr4.atn.ATN import ATN
    from antlr4.Lexer import Lexer
    from antlr4.PredictionContext import PredictionContextCache

from antlr4.atn.LexerATNSimulator import LexerATNSimulator


class CustomLexerATNSimulator(LexerATNSimulator):

    MAX_DFA_EDGE = 368

    def __init__(self, recog: 'Lexer', atn: 'ATN', decisionToDFA: list, sharedContextCache: 'PredictionContextCache'):
        super().__init__(recog, atn, decisionToDFA, sharedContextCache)


