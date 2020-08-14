from enum import Enum
from typing import List, Union


class TurkishNumeralEndingMachine:

    def __init__(self):
        self.ROOT = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.ROOT)
        self.states1 = (TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.SIFIR),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.BIR),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.IKI),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.UC),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.DORT),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.BES),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.ALTI),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.YEDI),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.SEKIZ),
                        TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.DOKUZ))
        self.states10 = (None, TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.ON),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.YIRMI),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.OTUZ),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.KIRK),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.ELLI),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.ALTMIS),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.YETMIS),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.SEKSEN),
                         TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.DOKSAN))
        self.SIFIR = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.SIFIR)
        self.YUZ = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.YUZ)
        self.BIN_1 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.BIN)
        self.BIN_2 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.BIN)
        self.BIN_3 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.BIN)
        self.MILYON_1 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYON)
        self.MILYON_2 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYON)
        self.MILYON_3 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYON)
        self.MILYAR_1 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYAR)
        self.MILYAR_2 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYAR)
        self.MILYAR_3 = TurkishNumeralEndingMachine.State(TurkishNumeralEndingMachine.StateId.MILYAR)
        self.zero_states = [self.SIFIR, self.YUZ, self.BIN_1, self.BIN_2, self.BIN_3, self.MILYON_1, self.MILYON_2,
                            self.MILYON_3, self.MILYAR_1, self.MILYAR_2, self.MILYAR_3]
        self.build()

    def build(self):
        self.SIFIR.zero_state = False

        for large_state in self.zero_states:
            large_state.zero_state = True

        for i, ten_state in enumerate(self.states1[1:], 1):
            self.ROOT.add_(i, ten_state)

        for i, ten_state in enumerate(self.states10[1:], 1):
            self.SIFIR.add_(i, ten_state)

        self.ROOT.add_(0, self.SIFIR)
        self.SIFIR.add_(0, self.YUZ)
        self.YUZ.add_(0, self.BIN_1)
        self.BIN_1.add_(0, self.BIN_2)
        self.BIN_2.add_(0, self.BIN_3)
        self.BIN_3.add_(0, self.MILYON_1)
        self.MILYON_1.add_(0, self.MILYON_2)
        self.MILYON_2.add_(0, self.MILYON_3)
        self.MILYON_3.add_(0, self.MILYAR_1)
        self.MILYAR_1.add_(0, self.MILYAR_2)
        self.MILYAR_2.add_(0, self.MILYAR_3)

    def find(self, num_str: str) -> str:
        current: 'TurkishNumeralEndingMachine.State' = self.ROOT

        for c in reversed(num_str):
            k = ord(c) - 48
            if k < 0 or k > 9:
                if current.zero_state:
                    return TurkishNumeralEndingMachine.StateId.SIFIR.lemma
                break

            if k > 0 and current.zero_state:
                if current == self.SIFIR:
                    return current.transitions[k].id_.lemma
                break

            current = current.transitions[k]
            if current is None:
                return TurkishNumeralEndingMachine.StateId.ERROR.lemma

            if not current.zero_state:
                break

        return current.id_.lemma

    class State:
        def __init__(self, id_: 'TurkishNumeralEndingMachine.StateId'):
            self.id_ = id_
            self.zero_state = None
            self.transitions: List[Union[None, 'TurkishNumeralEndingMachine.State']] = [None] * 10

        def add_(self, i: int, state: 'TurkishNumeralEndingMachine.State'):
            self.transitions[i] = state

    class StateId(Enum):
        ROOT = ""
        ERROR = ""
        SIFIR = "sıfır"
        BIR = "bir"
        IKI = "iki"
        UC = "üç"
        DORT = "dört"
        BES = "beş"
        ALTI = "altı"
        YEDI = "yedi"
        SEKIZ = "sekiz"
        DOKUZ = "dokuz"
        ON = "on"
        YIRMI = "yirmi"
        OTUZ = "otuz"
        KIRK = "kırk"
        ELLI = "elli"
        ALTMIS = "altmış"
        YETMIS = "yetmiş"
        SEKSEN = "seksen"
        DOKSAN = "doksan"
        YUZ = "yüz"
        BIN = "bin"
        MILYON = "milyon"
        MILYAR = "milyar"

        def __init__(self, lemma: str):
            self.lemma = lemma
