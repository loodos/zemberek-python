from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.lexicon import RootLexicon

from zemberek.core.turkish import PhoneticAttribute
from zemberek.morphology.morphotactics.morpheme import Morpheme
from zemberek.morphology.morphotactics.morpheme_state import MorphemeState
from zemberek.morphology.morphotactics.turkish_morphotactics import TurkishMorphotactics, StemTransitionsMapBased
from zemberek.morphology.morphotactics.conditions import Conditions


class InformalTurkishMorphotactics(TurkishMorphotactics):

    def __init__(self, lexicon: RootLexicon):
        super().__init__(lexicon)
        self.lexicon = lexicon

        self.a1plInformal = self.add_to_morpheme_map(
            Morpheme.builder("A1pl_Informal", "A1pl_Informal").informal_().mapped_morpheme_(self.a1pl).build())
        self.a1sgInformal = self.add_to_morpheme_map(
            Morpheme.builder("A1sg_Informal", "A1sg_Informal").informal_().mapped_morpheme_(self.a1sg).build())
        self.prog1Informal = self.add_to_morpheme_map(
            Morpheme.builder("Prog1_Informal", "Prog1_Informal").informal_().mapped_morpheme_(self.prog1).build())
        self.futInformal = self.add_to_morpheme_map(
            Morpheme.builder("Fut_Informal", "Fut_Informal").informal_().mapped_morpheme_(self.fut).build())
        self.quesSuffixInformal = self.add_to_morpheme_map(
            Morpheme.builder("QuesSuffix_Informal", "QuesSuffix_Informal").informal_().mapped_morpheme_(
                self.ques).build())
        self.negInformal = self.add_to_morpheme_map(
            Morpheme.builder("Neg_Informal", "Neg_Informal").informal_().mapped_morpheme_(self.neg).build())
        self.unableInformal = self.add_to_morpheme_map(
            Morpheme.builder("Unable_Informal", "Unable_Informal").informal_().mapped_morpheme_(self.unable).build())
        self.optInformal = self.add_to_morpheme_map(
            Morpheme.builder("Opt_Informal", "Opt_Informal").informal_().mapped_morpheme_(self.opt).build())

        self.vA1pl_ST_Inf = MorphemeState.terminal("vA1pl_ST_Inf", self.a1plInformal)
        self.vA1sg_ST_Inf = MorphemeState.terminal("vA1sg_ST_Inf", self.a1sgInformal)
        self.vProgYor_S_Inf = MorphemeState.non_terminal("vProgYor_S_Inf", self.prog1Informal)
        self.vFut_S_Inf = MorphemeState.non_terminal("vFut_S_Inf", self.futInformal)
        self.vFut_S_Inf2 = MorphemeState.non_terminal("vFut_S_Inf2", self.futInformal)
        self.vFut_S_Inf3 = MorphemeState.non_terminal("vFut_S_Inf3", self.futInformal)
        self.vQues_S_Inf = MorphemeState.non_terminal("vQues_S_Inf", self.quesSuffixInformal)
        self.vNeg_S_Inf = MorphemeState.non_terminal("vNeg_S_Inf", self.negInformal)
        self.vUnable_S_Inf = MorphemeState.non_terminal("vUnable_S_Inf", self.unableInformal)
        self.vOpt_S_Inf = MorphemeState.non_terminal("vOpt_S_Inf", self.optInformal)
        self.vOpt_S_Empty_Inf = MorphemeState.non_terminal("vOpt_S_Empty_Inf", self.optInformal)
        self.vOpt_S_Empty_Inf2 = MorphemeState.non_terminal("vOpt_S_Empty_Inf2", self.optInformal)

        # self.make_graph()
        self.add_graph()
        # self.stem_transitions = StemTransitionsMapBased(lexicon, self)

    def add_graph(self):
        self.verbRoot_S.add_(self.vProgYor_S_Inf, "Iyo",
                             Conditions.not_have(p_attribute=PhoneticAttribute.LastLetterVowel))
        self.verbRoot_VowelDrop_S.add_(self.vProgYor_S_Inf, "Iyo")
        self.vProgYor_S_Inf.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "sun").add_(self.vA2sg_ST, "n").add_empty(
            self.vA3sg_ST).add_(self.vA1pl_ST, "z").add_(self.vA2pl_ST, "sunuz").add_(self.vA2pl_ST, "nuz").add_(
            self.vA3pl_ST, "lar").add_(self.vCond_S, "sa").add_(self.vPastAfterTense_S, "du").add_(
            self.vNarrAfterTense_S, "muş").add_(self.vCopBeforeA3pl_S, "dur").add_(self.vWhile_S, "ken")
        self.vNegProg1_S.add_(self.vProgYor_S_Inf, "Iyo")
        self.vUnableProg1_S.add_(self.vProgYor_S_Inf, "Iyo")
        diYiCondition: Conditions.RootSurfaceIsAny = Conditions.RootSurfaceIsAny(("di", "yi"))
        self.vDeYeRoot_S.add_(self.vProgYor_S_Inf, "yo", diYiCondition)
        self.vOpt_S.add_(self.vA1pl_ST_Inf, "k")
        self.verbRoot_S.add_(self.vNeg_S_Inf, "mI")
        self.verbRoot_S.add_(self.vUnable_S_Inf, "+yAmI")
        self.verbRoot_S.add_(self.vFut_S_Inf, "+ycA~k").add_(self.vFut_S_Inf, "+ycA!ğ").add_(self.vFut_S_Inf2,
                                                                                             "+ycA").add_(
            self.vFut_S_Inf2, "+yIcA").add_(self.vFut_S_Inf2, "+yAcA")
        self.vNeg_S_Inf.add_(self.vFut_S, "yAcA~k").add_(self.vFut_S, "yAcA!ğ").add_(self.vFut_S_Inf, "ycA~k").add_(
            self.vFut_S_Inf, "ycA!ğ").add_(self.vFut_S_Inf2, "ycA")
        self.vUnable_S_Inf.add_(self.vFut_S, "yAcA~k").add_(self.vFut_S, "yAcA!ğ").add_(self.vFut_S_Inf, "ycA~k").add_(
            self.vFut_S_Inf, "ycA!ğ").add_(self.vFut_S_Inf2, "ycA")
        self.vNeg_S.add_(self.vFut_S_Inf, "yAcA").add_(self.vFut_S_Inf, "yAcAk")
        self.vUnable_S.add_(self.vFut_S_Inf, "yAcA").add_(self.vFut_S_Inf, "yAcAk")
        self.vFut_S_Inf.add_(self.vA1sg_ST, "+Im").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(
            self.vA1pl_ST, "Iz").add_(self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr")
        self.vFut_S_Inf2.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "n").add_(self.vA1pl_ST, "z").add_(self.vA1pl_ST,
                                                                                                         "nIz")
        self.vFut_S_Inf.add_(self.vCond_S, "sA")
        self.vFut_S_Inf.add_(self.vPastAfterTense_S, "tI")
        self.vFut_S_Inf.add_(self.vNarrAfterTense_S, "mIş")
        self.vFut_S_Inf.add_(self.vCopBeforeA3pl_S, "tIr")
        self.vFut_S_Inf.add_(self.vWhile_S, "ken")
        self.verbRoot_S.add_(self.vOpt_S_Inf, "I", Conditions.has(p_attribute=PhoneticAttribute.LastLetterConsonant))
        self.verbRoot_VowelDrop_S.add_(self.vOpt_S_Inf, "I")
        self.verbRoot_S.add_empty(self.vOpt_S_Empty_Inf, Conditions.has(p_attribute=PhoneticAttribute.LastLetterVowel))
        self.vOpt_S_Inf.add_(self.vA1sg_ST_Inf, "+yIm")
        self.vOpt_S_Inf.add_(self.vA1sg_ST_Inf, "+yim")
        self.vOpt_S_Empty_Inf.add_(self.vA1sg_ST_Inf, "+yim")
