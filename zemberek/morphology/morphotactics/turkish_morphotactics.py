from __future__ import annotations

import logging
from copy import deepcopy
from typing import Dict, Set, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.morphology.lexicon import RootLexicon

from zemberek.core.utils import ReadWriteLock
from zemberek.core.turkish import PrimaryPos, SecondaryPos, RootAttribute, PhoneticAttribute, TurkishAlphabet
from zemberek.morphology.analysis.attributes_helper import AttributesHelper
from zemberek.morphology.lexicon import DictionaryItem
from zemberek.morphology.morphotactics.morpheme import Morpheme
from zemberek.morphology.morphotactics.morpheme_state import MorphemeState
from zemberek.morphology.morphotactics.conditions import Conditions
from zemberek.morphology.morphotactics.stem_transition import StemTransition

logger = logging.getLogger(__name__)

morpheme_map: Dict[str, Morpheme] = dict()


def add_morpheme(morpheme: Morpheme) -> Morpheme:
    morpheme_map[morpheme.id_] = morpheme
    return morpheme


def get_morpheme_map() -> Dict[str, Morpheme]:
    return morpheme_map


class TurkishMorphotactics:
    root = add_morpheme(Morpheme.instance("Root", "Root"))
    noun = add_morpheme(Morpheme.instance("Noun", "Noun", PrimaryPos.Noun))
    adj = add_morpheme(Morpheme.instance("Adjective", "Adj", PrimaryPos.Adjective))
    verb = add_morpheme(Morpheme.instance("Verb", "Verb", PrimaryPos.Verb))
    pron = add_morpheme(Morpheme.instance("Pronoun", "Pron", PrimaryPos.Pronoun))
    adv = add_morpheme(Morpheme.instance("Adverb", "Adv", PrimaryPos.Adverb))
    conj = add_morpheme(Morpheme.instance("Conjunction", "Conj", PrimaryPos.Conjunction))
    punc = add_morpheme(Morpheme.instance("Punctuation", "Punc", PrimaryPos.Punctuation))
    ques = add_morpheme(Morpheme.instance("Question", "Ques", PrimaryPos.Question))
    postp = add_morpheme(Morpheme.instance("PostPositive", "Postp", PrimaryPos.PostPositive))
    det = add_morpheme(Morpheme.instance("Determiner", "Det", PrimaryPos.Determiner))
    num = add_morpheme(Morpheme.instance("Numeral", "Num", PrimaryPos.Numeral))
    dup = add_morpheme(Morpheme.instance("Duplicator", "Dup", PrimaryPos.Duplicator))
    interj = add_morpheme(Morpheme.instance("Interjection", "Interj", PrimaryPos.Interjection))
    a1sg = add_morpheme(Morpheme.instance("FirstPersonSingular", "A1sg"))
    a2sg = add_morpheme(Morpheme.instance("SecondPersonSingular", "A2sg"))
    a3sg = add_morpheme(Morpheme.instance("ThirdPersonSingular", "A3sg"))
    a1pl = add_morpheme(Morpheme.instance("FirstPersonPlural", "A1pl"))
    a2pl = add_morpheme(Morpheme.instance("SecondPersonPlural", "A2pl"))
    a3pl = add_morpheme(Morpheme.instance("ThirdPersonPlural", "A3pl"))
    pnon = add_morpheme(Morpheme.instance("NoPosession", "Pnon"))
    p1sg = add_morpheme(Morpheme.instance("FirstPersonSingularPossessive", "P1sg"))
    p2sg = add_morpheme(Morpheme.instance("SecondPersonSingularPossessive", "P2sg"))
    p3sg = add_morpheme(Morpheme.instance("ThirdPersonSingularPossessive", "P3sg"))
    p1pl = add_morpheme(Morpheme.instance("FirstPersonPluralPossessive", "P1pl"))
    p2pl = add_morpheme(Morpheme.instance("SecondPersonPluralPossessive", "P2pl"))
    p3pl = add_morpheme(Morpheme.instance("ThirdPersonPluralPossessive", "P3pl"))
    nom = add_morpheme(Morpheme.instance("Nominal", "Nom"))
    dat = add_morpheme(Morpheme.instance("Dative", "Dat"))
    acc = add_morpheme(Morpheme.instance("Accusative", "Acc"))
    abl = add_morpheme(Morpheme.instance("Ablative", "Abl"))
    loc = add_morpheme(Morpheme.instance("Locative", "Loc"))
    ins = add_morpheme(Morpheme.instance("Instrumental", "Ins"))
    gen = add_morpheme(Morpheme.instance("Genitive", "Gen"))
    equ = add_morpheme(Morpheme.instance("Equ", "Equ"))
    dim = add_morpheme(Morpheme.derivational("Diminutive", "Dim"))
    ness = add_morpheme(Morpheme.derivational("Ness", "Ness"))
    with_ = add_morpheme(Morpheme.derivational("With", "With"))
    without = add_morpheme(Morpheme.derivational("Without", "Without"))
    related = add_morpheme(Morpheme.derivational("Related", "Related"))
    justLike = add_morpheme(Morpheme.derivational("JustLike", "JustLike"))
    rel = add_morpheme(Morpheme.derivational("Relation", "Rel"))
    agt = add_morpheme(Morpheme.derivational("Agentive", "Agt"))
    become = add_morpheme(Morpheme.derivational("Become", "Become"))
    acquire = add_morpheme(Morpheme.derivational("Acquire", "Acquire"))
    ly = add_morpheme(Morpheme.derivational("Ly", "Ly"))
    caus = add_morpheme(Morpheme.derivational("Causative", "Caus"))
    recip = add_morpheme(Morpheme.derivational("Reciprocal", "Recip"))
    reflex = add_morpheme(Morpheme.derivational("Reflexive", "Reflex"))
    able = add_morpheme(Morpheme.derivational("Ability", "Able"))
    pass_ = add_morpheme(Morpheme.derivational("Passive", "Pass"))
    inf1 = add_morpheme(Morpheme.derivational("Infinitive1", "Inf1"))
    inf2 = add_morpheme(Morpheme.derivational("Infinitive2", "Inf2"))
    inf3 = add_morpheme(Morpheme.derivational("Infinitive3", "Inf3"))
    actOf = add_morpheme(Morpheme.derivational("ActOf", "ActOf"))
    pastPart = add_morpheme(Morpheme.derivational("PastParticiple", "PastPart"))
    narrPart = add_morpheme(Morpheme.derivational("NarrativeParticiple", "NarrPart"))
    futPart = add_morpheme(Morpheme.derivational("FutureParticiple", "FutPart"))
    presPart = add_morpheme(Morpheme.derivational("PresentParticiple", "PresPart"))
    aorPart = add_morpheme(Morpheme.derivational("AoristParticiple", "AorPart"))
    notState = add_morpheme(Morpheme.derivational("NotState", "NotState"))
    feelLike = add_morpheme(Morpheme.derivational("FeelLike", "FeelLike"))
    everSince = add_morpheme(Morpheme.derivational("EverSince", "EverSince"))
    repeat = add_morpheme(Morpheme.derivational("Repeat", "Repeat"))
    almost = add_morpheme(Morpheme.derivational("Almost", "Almost"))
    hastily = add_morpheme(Morpheme.derivational("Hastily", "Hastily"))
    stay = add_morpheme(Morpheme.derivational("Stay", "Stay"))
    start = add_morpheme(Morpheme.derivational("Start", "Start"))
    asIf = add_morpheme(Morpheme.derivational("AsIf", "AsIf"))
    while_ = add_morpheme(Morpheme.derivational("While", "While"))
    when = add_morpheme(Morpheme.derivational("When", "When"))
    sinceDoingSo = add_morpheme(Morpheme.derivational("SinceDoingSo", "SinceDoingSo"))
    asLongAs = add_morpheme(Morpheme.derivational("AsLongAs", "AsLongAs"))
    byDoingSo = add_morpheme(Morpheme.derivational("ByDoingSo", "ByDoingSo"))
    adamantly = add_morpheme(Morpheme.derivational("Adamantly", "Adamantly"))
    afterDoingSo = add_morpheme(Morpheme.derivational("AfterDoingSo", "AfterDoingSo"))
    withoutHavingDoneSo = add_morpheme(Morpheme.derivational("WithoutHavingDoneSo", "WithoutHavingDoneSo"))
    withoutBeingAbleToHaveDoneSo = add_morpheme(
        Morpheme.derivational("WithoutBeingAbleToHaveDoneSo", "WithoutBeingAbleToHaveDoneSo"))
    zero = add_morpheme(Morpheme.derivational("Zero", "Zero"))
    cop = add_morpheme(Morpheme.instance("Copula", "Cop"))
    neg = add_morpheme(Morpheme.instance("Negative", "Neg"))
    unable = add_morpheme(Morpheme.instance("Unable", "Unable"))
    pres = add_morpheme(Morpheme.instance("PresentTense", "Pres"))
    past = add_morpheme(Morpheme.instance("PastTense", "Past"))
    narr = add_morpheme(Morpheme.instance("NarrativeTense", "Narr"))
    cond = add_morpheme(Morpheme.instance("Condition", "Cond"))
    prog1 = add_morpheme(Morpheme.instance("Progressive1", "Prog1"))
    prog2 = add_morpheme(Morpheme.instance("Progressive2", "Prog2"))
    aor = add_morpheme(Morpheme.instance("Aorist", "Aor"))
    fut = add_morpheme(Morpheme.instance("Future", "Fut"))
    imp = add_morpheme(Morpheme.instance("Imparative", "Imp"))
    opt = add_morpheme(Morpheme.instance("Optative", "Opt"))
    desr = add_morpheme(Morpheme.instance("Desire", "Desr"))
    neces = add_morpheme(Morpheme.instance("Necessity", "Neces"))

    morpheme_map = get_morpheme_map()

    def __init__(self, lexicon: RootLexicon):
        self.root_S = MorphemeState.non_terminal("root_S", self.root)
        self.puncRoot_ST = MorphemeState.terminal("puncRoot_ST", self.punc, pos_root=True)
        self.noun_S = MorphemeState.builder("noun_S", self.noun, pos_root=True).build()
        self.nounCompoundRoot_S = MorphemeState.builder("nounCompoundRoot_S", self.noun, pos_root=True).build()
        self.nounSuRoot_S = MorphemeState.builder("nounSuRoot_S", self.noun, pos_root=True).build()
        self.nounInf1Root_S = MorphemeState.builder("nounInf1Root_S", self.noun, pos_root=True).build()
        self.nounActOfRoot_S = MorphemeState.builder("nounActOfRoot_S", self.noun, pos_root=True).build()
        self.a3sg_S = MorphemeState.non_terminal("a3sg_S", self.a3sg)
        self.a3sgSu_S = MorphemeState.non_terminal("a3sgSu_S", self.a3sg)
        self.a3sgCompound_S = MorphemeState.non_terminal("a3sgCompound_S", self.a3sg)
        self.a3sgInf1_S = MorphemeState.non_terminal("a3sgInf1_S", self.a3sg)
        self.a3sgActOf_S = MorphemeState.non_terminal("a3sgActOf_S", self.a3sg)
        self.a3pl_S = MorphemeState.non_terminal("a3pl_S", self.a3pl)
        self.a3plActOf_S = MorphemeState.non_terminal("a3plActOf_S", self.a3pl)
        self.a3plCompound_S = MorphemeState.non_terminal("a3plCompound_S", self.a3pl)
        self.a3plCompound2_S = MorphemeState.non_terminal("a3plCompound2_S", self.a3pl)
        self.pnon_S = MorphemeState.non_terminal("pnon_S", self.pnon)
        self.pnonCompound_S = MorphemeState.non_terminal("pnonCompound_S", self.pnon)
        self.pnonCompound2_S = MorphemeState.non_terminal("pnonCompound2_S", self.pnon)
        self.pnonInf1_S = MorphemeState.non_terminal("pnonInf1_S", self.pnon)
        self.pnonActOf = MorphemeState.non_terminal("pnonActOf", self.pnon)
        self.p1sg_S = MorphemeState.non_terminal("p1sg_S", self.p1sg)
        self.p2sg_S = MorphemeState.non_terminal("p2sg_S", self.p2sg)
        self.p3sg_S = MorphemeState.non_terminal("p3sg_S", self.p3sg)
        self.p1pl_S = MorphemeState.non_terminal("p1pl_S", self.p1pl)
        self.p2pl_S = MorphemeState.non_terminal("p2pl_S", self.p2pl)
        self.p3pl_S = MorphemeState.non_terminal("p3pl_S", self.p3pl)
        self.nom_ST = MorphemeState.terminal("nom_ST", self.nom)
        self.nom_S = MorphemeState.non_terminal("nom_S", self.nom)
        self.dat_ST = MorphemeState.terminal("dat_ST", self.dat)
        self.abl_ST = MorphemeState.terminal("abl_ST", self.abl)
        self.loc_ST = MorphemeState.terminal("loc_ST", self.loc)
        self.ins_ST = MorphemeState.terminal("ins_ST", self.ins)
        self.acc_ST = MorphemeState.terminal("acc_ST", self.acc)
        self.gen_ST = MorphemeState.terminal("gen_ST", self.gen)
        self.equ_ST = MorphemeState.terminal("equ_ST", self.equ)
        self.dim_S = MorphemeState.non_terminal_derivative("dim_S", self.dim)
        self.ness_S = MorphemeState.non_terminal_derivative("ness_S", self.ness)
        self.agt_S = MorphemeState.non_terminal_derivative("agt_S", self.agt)
        self.related_S = MorphemeState.non_terminal_derivative("related_S", self.related)
        self.rel_S = MorphemeState.non_terminal_derivative("rel_S", self.rel)
        self.relToPron_S = MorphemeState.non_terminal_derivative("relToPron_S", self.rel)
        self.with_S = MorphemeState.non_terminal_derivative("with_S", self.with_)
        self.without_S = MorphemeState.non_terminal_derivative("without_S", self.without)
        self.justLike_S = MorphemeState.non_terminal_derivative("justLike_S", self.justLike)
        self.nounZeroDeriv_S = MorphemeState.non_terminal_derivative("nounZeroDeriv_S", self.zero)
        self.become_S = MorphemeState.non_terminal_derivative("become_S", self.become)
        self.acquire_S = MorphemeState.non_terminal_derivative("acquire_S", self.acquire)
        self.nounLastVowelDropRoot_S = MorphemeState.builder("nounLastVowelDropRoot_S", self.noun, True).build()
        self.adjLastVowelDropRoot_S = MorphemeState.builder("adjLastVowelDropRoot_S", self.adj, True).build()
        self.postpLastVowelDropRoot_S = MorphemeState.builder("postpLastVowelDropRoot_S", self.postp, True).build()
        self.a3PlLastVowelDrop_S = MorphemeState.non_terminal("a3PlLastVowelDrop_S", self.a3pl)
        self.a3sgLastVowelDrop_S = MorphemeState.non_terminal("a3sgLastVowelDrop_S", self.a3sg)
        self.pNonLastVowelDrop_S = MorphemeState.non_terminal("pNonLastVowelDrop_S", self.pnon)
        self.zeroLastVowelDrop_S = MorphemeState.non_terminal_derivative("zeroLastVowelDrop_S", self.zero)
        self.nounProper_S = MorphemeState.builder("nounProper_S", self.noun, pos_root=True).build()
        self.nounAbbrv_S = MorphemeState.builder("nounAbbrv_S", self.noun, pos_root=True).build()
        self.puncProperSeparator_S = MorphemeState.non_terminal("puncProperSeparator_S", self.punc)
        self.nounNoSuffix_S = MorphemeState.builder("nounNoSuffix_S", self.noun, pos_root=True).build()
        self.nounA3sgNoSuffix_S = MorphemeState.non_terminal("nounA3sgNoSuffix_S", self.a3sg)
        self.nounPnonNoSuffix_S = MorphemeState.non_terminal("nounPnonNoSuffix_S", self.pnon)
        self.nounNomNoSuffix_ST = MorphemeState.terminal("nounNomNoSuffix_S", self.nom)
        self.adjectiveRoot_ST = MorphemeState.terminal("adjectiveRoot_ST", self.adj, pos_root=True)
        self.adjAfterVerb_S = MorphemeState.builder("adjAfterVerb_S", self.adj, pos_root=True).build()
        self.adjAfterVerb_ST = MorphemeState.terminal("adjAfterVerb_ST", self.adj, pos_root=True)
        self.adjZeroDeriv_S = MorphemeState.non_terminal_derivative("adjZeroDeriv_S", self.zero)
        self.aPnon_ST = MorphemeState.terminal("aPnon_ST", self.pnon)
        self.aP1sg_ST = MorphemeState.terminal("aP1sg_ST", self.p1sg)
        self.aP2sg_ST = MorphemeState.terminal("aP2sg_ST", self.p2sg)
        self.aP3sg_ST = MorphemeState.terminal("aP3sg_ST", self.p3sg)
        self.aP1pl_ST = MorphemeState.terminal("aP3sg_ST", self.p1pl)
        self.aP2pl_ST = MorphemeState.terminal("aP2pl_ST", self.p2pl)
        self.aP3pl_ST = MorphemeState.terminal("aP3pl_ST", self.p3pl)
        self.aLy_S = MorphemeState.non_terminal_derivative("aLy_S", self.ly)
        self.aAsIf_S = MorphemeState.non_terminal_derivative("aAsIf_S", self.asIf)
        self.aAgt_S = MorphemeState.non_terminal_derivative("aAgt_S", self.agt)
        self.numeralRoot_ST = MorphemeState.terminal("numeralRoot_ST", self.num, pos_root=True)
        self.numZeroDeriv_S = MorphemeState.non_terminal_derivative("numZeroDeriv_S", self.zero)
        self.nVerb_S = MorphemeState.builder("nVerb_S", self.verb, pos_root=True).build()
        self.nVerbDegil_S = MorphemeState.builder("nVerbDegil_S", self.verb, pos_root=True).build()
        self.nPresent_S = MorphemeState.non_terminal("nPresent_S", self.pres)
        self.nPast_S = MorphemeState.non_terminal("nPast_S", self.past)
        self.nNarr_S = MorphemeState.non_terminal("nNarr_S", self.narr)
        self.nCond_S = MorphemeState.non_terminal("nCond_S", self.cond)
        self.nA1sg_ST = MorphemeState.terminal("nA1sg_ST", self.a1sg)
        self.nA2sg_ST = MorphemeState.terminal("nA2sg_ST", self.a2sg)
        self.nA1pl_ST = MorphemeState.terminal("nA1pl_ST", self.a1pl)
        self.nA2pl_ST = MorphemeState.terminal("nA2pl_ST", self.a2pl)
        self.nA3sg_ST = MorphemeState.terminal("nA3sg_ST", self.a3sg)
        self.nA3sg_S = MorphemeState.non_terminal("nA3sg_S", self.a3sg)
        self.nA3pl_ST = MorphemeState.terminal("nA3pl_ST", self.a3pl)
        self.nCop_ST = MorphemeState.terminal("nCop_ST", self.cop)
        self.nCopBeforeA3pl_S = MorphemeState.non_terminal("nCopBeforeA3pl_S", self.cop)
        self.nNeg_S = MorphemeState.non_terminal("nNeg_S", self.neg)
        self.pronPers_S = MorphemeState.builder("pronPers_S", self.pron, pos_root=True).build()
        self.pronDemons_S = MorphemeState.builder("pronDemons_S", self.pron, pos_root=True).build()
        self.pronQuant_S = MorphemeState.builder("pronQuant_S", self.pron, pos_root=True).build()
        self.pronQuantModified_S = MorphemeState.builder("pronQuantModified_S", self.pron, pos_root=True).build()
        self.pronQues_S = MorphemeState.builder("pronQues_S", self.pron, pos_root=True).build()
        self.pronReflex_S = MorphemeState.builder("pronReflex_S", self.pron, pos_root=True).build()
        self.pronPers_Mod_S = MorphemeState.builder("pronPers_Mod_S", self.pron, pos_root=True).build()
        self.pronAfterRel_S = MorphemeState.builder("pronAfterRel_S", self.pron, pos_root=True).build()
        self.pA1sg_S = MorphemeState.non_terminal("pA1sg_S", self.a1sg)
        self.pA2sg_S = MorphemeState.non_terminal("pA2sg_S", self.a2sg)
        self.pA1sgMod_S = MorphemeState.non_terminal("pA1sgMod_S", self.a1sg)
        self.pA2sgMod_S = MorphemeState.non_terminal("pA2sgMod_S", self.a2sg)
        self.pA3sg_S = MorphemeState.non_terminal("pA3sg_S", self.a3sg)
        self.pA3sgRel_S = MorphemeState.non_terminal("pA3sgRel_S", self.a3sg)
        self.pA1pl_S = MorphemeState.non_terminal("pA1pl_S", self.a1pl)
        self.pA2pl_S = MorphemeState.non_terminal("pA2pl_S", self.a2pl)
        self.pA3pl_S = MorphemeState.non_terminal("pA3pl_S", self.a3pl)
        self.pA3plRel_S = MorphemeState.non_terminal("pA3plRel_S", self.a3pl)
        self.pQuantA3sg_S = MorphemeState.non_terminal("pQuantA3sg_S", self.a3sg)
        self.pQuantA3pl_S = MorphemeState.non_terminal("pQuantA3pl_S", self.a3pl)
        self.pQuantModA3pl_S = MorphemeState.non_terminal("pQuantModA3pl_S", self.a3pl)
        self.pQuantA1pl_S = MorphemeState.non_terminal("pQuantA1pl_S", self.a1pl)
        self.pQuantA2pl_S = MorphemeState.non_terminal("pQuantA2pl_S", self.a2pl)
        self.pQuesA3sg_S = MorphemeState.non_terminal("pQuesA3sg_S", self.a3sg)
        self.pQuesA3pl_S = MorphemeState.non_terminal("pQuesA3pl_S", self.a3pl)
        self.pReflexA3sg_S = MorphemeState.non_terminal("pReflexA3sg_S", self.a3sg)
        self.pReflexA3pl_S = MorphemeState.non_terminal("pReflexA3pl_S", self.a3pl)
        self.pReflexA1sg_S = MorphemeState.non_terminal("pReflexA1sg_S", self.a1sg)
        self.pReflexA2sg_S = MorphemeState.non_terminal("pReflexA2sg_S", self.a2sg)
        self.pReflexA1pl_S = MorphemeState.non_terminal("pReflexA1pl_S", self.a1pl)
        self.pReflexA2pl_S = MorphemeState.non_terminal("pReflexA2pl_S", self.a2pl)
        self.pPnon_S = MorphemeState.non_terminal("pPnon_S", self.pnon)
        self.pPnonRel_S = MorphemeState.non_terminal("pPnonRel_S", self.pnon)
        self.pPnonMod_S = MorphemeState.non_terminal("pPnonMod_S", self.pnon)
        self.pP1sg_S = MorphemeState.non_terminal("pP1sg_S", self.p1sg)
        self.pP2sg_S = MorphemeState.non_terminal("pP2sg_S", self.p2sg)
        self.pP3sg_S = MorphemeState.non_terminal("pP3sg_S", self.p3sg)
        self.pP1pl_S = MorphemeState.non_terminal("pP1pl_S", self.p1pl)
        self.pP2pl_S = MorphemeState.non_terminal("pP2pl_S", self.p2pl)
        self.pP3pl_S = MorphemeState.non_terminal("pP3pl_S", self.p3pl)
        self.pNom_ST = MorphemeState.terminal("pNom_ST", self.nom)
        self.pDat_ST = MorphemeState.terminal("pDat_ST", self.dat)
        self.pAcc_ST = MorphemeState.terminal("pAcc_ST", self.acc)
        self.pAbl_ST = MorphemeState.terminal("pAbl_ST", self.abl)
        self.pLoc_ST = MorphemeState.terminal("pLoc_ST", self.loc)
        self.pGen_ST = MorphemeState.terminal("pGen_ST", self.gen)
        self.pIns_ST = MorphemeState.terminal("pIns_ST", self.ins)
        self.pEqu_ST = MorphemeState.terminal("pEqu_ST", self.equ)
        self.pronZeroDeriv_S = MorphemeState.non_terminal_derivative("pronZeroDeriv_S", self.zero)
        self.pvPresent_S = MorphemeState.non_terminal("pvPresent_S", self.pres)
        self.pvPast_S = MorphemeState.non_terminal("pvPast_S", self.past)
        self.pvNarr_S = MorphemeState.non_terminal("pvNarr_S", self.narr)
        self.pvCond_S = MorphemeState.non_terminal("pvCond_S", self.cond)
        self.pvA1sg_ST = MorphemeState.terminal("pvA1sg_ST", self.a1sg)
        self.pvA2sg_ST = MorphemeState.terminal("pvA2sg_ST", self.a2sg)
        self.pvA3sg_ST = MorphemeState.terminal("pvA3sg_ST", self.a3sg)
        self.pvA3sg_S = MorphemeState.non_terminal("pvA3sg_S", self.a3sg)
        self.pvA1pl_ST = MorphemeState.terminal("pvA1pl_ST", self.a1pl)
        self.pvA2pl_ST = MorphemeState.terminal("pvA2pl_ST", self.a2pl)
        self.pvA3pl_ST = MorphemeState.terminal("pvA3pl_ST", self.a3pl)
        self.pvCopBeforeA3pl_S = MorphemeState.non_terminal("pvCopBeforeA3pl_S", self.cop)
        self.pvCop_ST = MorphemeState.terminal("pvCop_ST", self.cop)
        self.pvVerbRoot_S = MorphemeState.builder("pvVerbRoot_S", self.verb, pos_root=True).build()
        self.advRoot_ST = MorphemeState.terminal("advRoot_ST", self.adv, pos_root=True)
        self.advNounRoot_ST = MorphemeState.terminal("advRoot_ST", self.adv, pos_root=True)
        self.advForVerbDeriv_ST = MorphemeState.terminal("advForVerbDeriv_ST", self.adv, pos_root=True)
        self.avNounAfterAdvRoot_ST = MorphemeState.builder("advToNounRoot_ST", self.noun, pos_root=True).build()
        self.avA3sg_S = MorphemeState.non_terminal("avA3sg_S", self.a3sg)
        self.avPnon_S = MorphemeState.non_terminal("avPnon_S", self.pnon)
        self.avDat_ST = MorphemeState.terminal("avDat_ST", self.dat)
        self.avZero_S = MorphemeState.non_terminal_derivative("avZero_S", self.zero)
        self.avZeroToVerb_S = MorphemeState.non_terminal_derivative("avZeroToVerb_S", self.zero)
        self.conjRoot_ST = MorphemeState.terminal("conjRoot_ST", self.conj, pos_root=True)
        self.interjRoot_ST = MorphemeState.terminal("interjRoot_ST", self.interj, pos_root=True)
        self.detRoot_ST = MorphemeState.terminal("detRoot_ST", self.det, pos_root=True)
        self.dupRoot_ST = MorphemeState.terminal("dupRoot_ST", self.dup, pos_root=True)
        self.postpRoot_ST = MorphemeState.terminal("postpRoot_ST", self.postp, pos_root=True)
        self.postpZero_S = MorphemeState.non_terminal_derivative("postpZero_S", self.zero)
        self.po2nRoot_S = MorphemeState.non_terminal("po2nRoot_S", self.noun)
        self.po2nA3sg_S = MorphemeState.non_terminal("po2nA3sg_S", self.a3sg)
        self.po2nA3pl_S = MorphemeState.non_terminal("po2nA3pl_S", self.a3pl)
        self.po2nP3sg_S = MorphemeState.non_terminal("po2nP3sg_S", self.p3sg)
        self.po2nP1sg_S = MorphemeState.non_terminal("po2nP1sg_S", self.p1sg)
        self.po2nP2sg_S = MorphemeState.non_terminal("po2nP2sg_S", self.p2sg)
        self.po2nP1pl_S = MorphemeState.non_terminal("po2nP1pl_S", self.p1pl)
        self.po2nP2pl_S = MorphemeState.non_terminal("po2nP2pl_S", self.p2pl)
        self.po2nPnon_S = MorphemeState.non_terminal("po2nPnon_S", self.pnon)
        self.po2nNom_ST = MorphemeState.terminal("po2nNom_ST", self.nom)
        self.po2nDat_ST = MorphemeState.terminal("po2nDat_ST", self.dat)
        self.po2nAbl_ST = MorphemeState.terminal("po2nAbl_ST", self.abl)
        self.po2nLoc_ST = MorphemeState.terminal("po2nLoc_ST", self.loc)
        self.po2nIns_ST = MorphemeState.terminal("po2nIns_ST", self.ins)
        self.po2nAcc_ST = MorphemeState.terminal("po2nAcc_ST", self.acc)
        self.po2nGen_ST = MorphemeState.terminal("po2nGen_ST", self.gen)
        self.po2nEqu_ST = MorphemeState.terminal("po2nEqu_ST", self.equ)
        self.verbRoot_S = MorphemeState.builder("verbRoot_S", self.verb, pos_root=True).build()
        self.verbLastVowelDropModRoot_S = MorphemeState.builder("verbLastVowelDropModRoot_S",
                                                                self.verb, pos_root=True).build()
        self.verbLastVowelDropUnmodRoot_S = MorphemeState.builder("verbLastVowelDropUnmodRoot_S", self.verb,
                                                                  pos_root=True).build()
        self.vA1sg_ST = MorphemeState.terminal("vA1sg_ST", self.a1sg)
        self.vA2sg_ST = MorphemeState.terminal("vA2sg_ST", self.a2sg)
        self.vA3sg_ST = MorphemeState.terminal("vA3sg_ST", self.a3sg)
        self.vA1pl_ST = MorphemeState.terminal("vA1pl_ST", self.a1pl)
        self.vA2pl_ST = MorphemeState.terminal("vA2pl_ST", self.a2pl)
        self.vA3pl_ST = MorphemeState.terminal("vA3pl_ST", self.a3pl)
        self.vPast_S = MorphemeState.non_terminal("vPast_S", self.past)
        self.vNarr_S = MorphemeState.non_terminal("vNarr_S", self.narr)
        self.vCond_S = MorphemeState.non_terminal("vCond_S", self.cond)
        self.vCondAfterPerson_ST = MorphemeState.terminal("vCondAfterPerson_ST", self.cond)
        self.vPastAfterTense_S = MorphemeState.non_terminal("vPastAfterTense_S", self.past)
        self.vNarrAfterTense_S = MorphemeState.non_terminal("vNarrAfterTense_S", self.narr)
        self.vPastAfterTense_ST = MorphemeState.terminal("vPastAfterTense_ST", self.past)
        self.vNarrAfterTense_ST = MorphemeState.terminal("vNarrAfterTense_ST", self.narr)
        self.vCond_ST = MorphemeState.terminal("vCond_ST", self.cond)
        self.vProgYor_S = MorphemeState.non_terminal("vProgYor_S", self.prog1)
        self.vProgMakta_S = MorphemeState.non_terminal("vProgMakta_S", self.prog2)
        self.vFut_S = MorphemeState.non_terminal("vFut_S", self.fut)
        self.vCop_ST = MorphemeState.terminal("vCop_ST", self.cop)
        self.vCopBeforeA3pl_S = MorphemeState.non_terminal("vCopBeforeA3pl_S", self.cop)
        self.vNeg_S = MorphemeState.non_terminal("vNeg_S", self.neg)
        self.vUnable_S = MorphemeState.non_terminal("vUnable_S", self.unable)
        self.vNegProg1_S = MorphemeState.non_terminal("vNegProg1_S", self.neg)
        self.vUnableProg1_S = MorphemeState.non_terminal("vUnableProg1_S", self.unable)
        self.vImp_S = MorphemeState.non_terminal("vImp_S", self.imp)
        self.vImpYemekYi_S = MorphemeState.non_terminal("vImpYemekYi_S", self.imp)
        self.vImpYemekYe_S = MorphemeState.non_terminal("vImpYemekYe_S", self.imp)
        self.vCausT_S = MorphemeState.non_terminal_derivative("vCaus_S", self.caus)
        self.vCausTir_S = MorphemeState.non_terminal_derivative("vCausTır_S", self.caus)  # original is vCausTır_S
        self.vRecip_S = MorphemeState.non_terminal_derivative("vRecip_S", self.recip)
        self.vImplicitRecipRoot_S = MorphemeState.builder("vImplicitRecipRoot_S", self.verb, pos_root=True).build()
        self.vReflex_S = MorphemeState.non_terminal_derivative("vReflex_S", self.reflex)
        self.vImplicitReflexRoot_S = MorphemeState.builder("vImplicitReflexRoot_S", self.verb, pos_root=True).build()
        self.verbRoot_VowelDrop_S = MorphemeState.builder("verbRoot_VowelDrop_S", self.verb, pos_root=True).build()
        self.vAor_S = MorphemeState.non_terminal("vAor_S", self.aor)
        self.vAorNeg_S = MorphemeState.non_terminal("vAorNeg_S", self.aor)
        self.vAorNegEmpty_S = MorphemeState.non_terminal("vAorNegEmpty_S", self.aor)
        self.vAorPartNeg_S = MorphemeState.non_terminal_derivative("vAorPartNeg_S", self.aorPart)
        self.vAorPart_S = MorphemeState.non_terminal_derivative("vAorPart_S", self.aorPart)
        self.vAble_S = MorphemeState.non_terminal_derivative("vAble_S", self.able)
        self.vAbleNeg_S = MorphemeState.non_terminal_derivative("vAbleNeg_S", self.able)
        self.vAbleNegDerivRoot_S = MorphemeState.builder("vAbleNegDerivRoot_S", self.verb, pos_root=True).build()
        self.vPass_S = MorphemeState.non_terminal_derivative("vPass_S", self.pass_)
        self.vOpt_S = MorphemeState.non_terminal("vOpt_S", self.opt)
        self.vDesr_S = MorphemeState.non_terminal("vDesr_S", self.desr)
        self.vNeces_S = MorphemeState.non_terminal("vNeces_S", self.neces)
        self.vInf1_S = MorphemeState.non_terminal_derivative("vInf1_S", self.inf1)
        self.vInf2_S = MorphemeState.non_terminal_derivative("vInf2_S", self.inf2)
        self.vInf3_S = MorphemeState.non_terminal_derivative("vInf3_S", self.inf3)
        self.vAgt_S = MorphemeState.non_terminal_derivative("vAgt_S", self.agt)
        self.vActOf_S = MorphemeState.non_terminal_derivative("vActOf_S", self.actOf)
        self.vPastPart_S = MorphemeState.non_terminal_derivative("vPastPart_S", self.pastPart)
        self.vFutPart_S = MorphemeState.non_terminal_derivative("vFutPart_S", self.futPart)
        self.vPresPart_S = MorphemeState.non_terminal_derivative("vPresPart_S", self.presPart)
        self.vNarrPart_S = MorphemeState.non_terminal_derivative("vNarrPart_S", self.narrPart)
        self.vFeelLike_S = MorphemeState.non_terminal_derivative("vFeelLike_S", self.feelLike)
        self.vNotState_S = MorphemeState.non_terminal_derivative("vNotState_S", self.notState)
        self.vEverSince_S = MorphemeState.non_terminal_derivative("vEverSince_S", self.everSince)
        self.vRepeat_S = MorphemeState.non_terminal_derivative("vRepeat_S", self.repeat)
        self.vAlmost_S = MorphemeState.non_terminal_derivative("vAlmost_S", self.almost)
        self.vHastily_S = MorphemeState.non_terminal_derivative("vHastily_S", self.hastily)
        self.vStay_S = MorphemeState.non_terminal_derivative("vStay_S", self.stay)
        self.vStart_S = MorphemeState.non_terminal_derivative("vStart_S", self.start)
        self.vWhile_S = MorphemeState.non_terminal_derivative("vWhile_S", self.while_)
        self.vWhen_S = MorphemeState.non_terminal_derivative("vWhen_S", self.when)
        self.vAsIf_S = MorphemeState.non_terminal_derivative("vAsIf_S", self.asIf)
        self.vSinceDoingSo_S = MorphemeState.non_terminal_derivative("vSinceDoingSo_S", self.sinceDoingSo)
        self.vAsLongAs_S = MorphemeState.non_terminal_derivative("vAsLongAs_S", self.asLongAs)
        self.vByDoingSo_S = MorphemeState.non_terminal_derivative("vByDoingSo_S", self.byDoingSo)
        self.vAdamantly_S = MorphemeState.non_terminal_derivative("vAdamantly_S", self.adamantly)
        self.vAfterDoing_S = MorphemeState.non_terminal_derivative("vAfterDoing_S", self.afterDoingSo)
        self.vWithoutHavingDoneSo_S = MorphemeState.non_terminal_derivative("vWithoutHavingDoneSo_S",
                                                                            self.withoutHavingDoneSo)
        self.vWithoutBeingAbleToHaveDoneSo_S = MorphemeState.non_terminal_derivative("vWithoutBeingAbleToHaveDoneSo_S",
                                                                                     self.withoutBeingAbleToHaveDoneSo)
        self.vDeYeRoot_S = MorphemeState.builder("vDeYeRoot_S", self.verb, pos_root=True).build()
        self.qPresent_S = MorphemeState.non_terminal("qPresent_S", self.pres)
        self.qPast_S = MorphemeState.non_terminal("qPast_S", self.past)
        self.qNarr_S = MorphemeState.non_terminal("qNarr_S", self.narr)
        self.qA1sg_ST = MorphemeState.terminal("qA1sg_ST", self.a1sg)
        self.qA2sg_ST = MorphemeState.terminal("qA2sg_ST", self.a2sg)
        self.qA3sg_ST = MorphemeState.terminal("qA3sg_ST", self.a3sg)
        self.qA1pl_ST = MorphemeState.terminal("qA1pl_ST", self.a1pl)
        self.qA2pl_ST = MorphemeState.terminal("qA2pl_ST", self.a2pl)
        self.qA3pl_ST = MorphemeState.terminal("qA3pl_ST", self.a3pl)
        self.qCopBeforeA3pl_S = MorphemeState.non_terminal("qCopBeforeA3pl_S", self.cop)
        self.qCop_ST = MorphemeState.terminal("qCop_ST", self.cop)
        self.questionRoot_S = MorphemeState.builder("questionRoot_S", self.ques, pos_root=True).build()
        self.imekRoot_S = MorphemeState.builder("imekRoot_S", self.verb, pos_root=True).build()
        self.imekPast_S = MorphemeState.non_terminal("imekPast_S", self.past)
        self.imekNarr_S = MorphemeState.non_terminal("imekNarr_S", self.narr)
        self.imekCond_S = MorphemeState.non_terminal("imekCond_S", self.cond)
        self.imekA1sg_ST = MorphemeState.terminal("imekA1sg_ST", self.a1sg)
        self.imekA2sg_ST = MorphemeState.terminal("imekA2sg_ST", self.a2sg)
        self.imekA3sg_ST = MorphemeState.terminal("imekA3sg_ST", self.a3sg)
        self.imekA1pl_ST = MorphemeState.terminal("imekA1pl_ST", self.a1pl)
        self.imekA2pl_ST = MorphemeState.terminal("imekA2pl_ST", self.a2pl)
        self.imekA3pl_ST = MorphemeState.terminal("imekA3pl_ST", self.a3pl)
        self.imekCop_ST = MorphemeState.terminal("qCop_ST", self.cop)
        self.item_root_state_map = {}
        self.lexicon = lexicon
        self.make_graph()
        self.stem_transitions = StemTransitionsMapBased(lexicon, self)

    def get_stem_transitions(self) -> StemTransitionsMapBased:
        return self.stem_transitions

    def get_root_lexicon(self) -> RootLexicon:
        return self.lexicon

    def add_to_morpheme_map(self, morpheme: Morpheme) -> Morpheme:
        self.morpheme_map[morpheme.id_] = morpheme
        return morpheme

    def make_graph(self):
        self.map_special_items_to_root_state()
        self.connect_noun_states()
        self.connect_proper_nouns_and_abbreviations()
        self.connect_adjective_states()
        self.connect_numeral_states()
        self.connect_verb_after_noun_adj_states()
        self.connect_pronoun_states()
        self.connect_verb_after_pronoun()
        self.connect_verbs()
        self.connect_question()
        self.connect_adverbs()
        self.connect_last_vowel_drop_words()
        self.connect_postpositives()
        self.connect_imek()
        self.handle_post_processing_connections()

    def map_special_items_to_root_state(self):
        self.item_root_state_map["değil_Verb"] = self.nVerbDegil_S
        self.item_root_state_map["imek_Verb"] = self.imekRoot_S
        self.item_root_state_map["su_Noun"] = self.nounSuRoot_S
        self.item_root_state_map["akarsu_Noun"] = self.nounSuRoot_S
        self.item_root_state_map["öyle_Adv"] = self.advForVerbDeriv_ST
        self.item_root_state_map["böyle_Adv"] = self.advForVerbDeriv_ST
        self.item_root_state_map["şöyle_Adv"] = self.advForVerbDeriv_ST

    def connect_noun_states(self):
        self.noun_S.add_empty(self.a3sg_S, Conditions.not_have(r_attribute=RootAttribute.ImplicitPlural))
        self.noun_S.add_(self.a3pl_S, "lAr", Conditions.not_have(r_attribute=RootAttribute.ImplicitPlural).and_(
            Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg)))
        self.noun_S.add_empty(self.a3pl_S, Conditions.has(r_attribute=RootAttribute.ImplicitPlural))
        self.nounCompoundRoot_S.add_empty(self.a3sgCompound_S,
                                          Conditions.has(r_attribute=RootAttribute.CompoundP3sgRoot))
        self.a3sgCompound_S.add_empty(self.pnonCompound_S)
        self.a3sgCompound_S.add_(self.p3pl_S, "lArI")
        self.pnonCompound_S.add_empty(self.nom_S)
        self.nom_S.add_(self.become_S, "lAş")
        self.nom_S.add_(self.acquire_S, "lAn")
        self.nom_S.add_(self.with_S, "lI", (Conditions.ContainsMorpheme((self.with_, self.without))).not_())
        self.nom_S.add_(self.without_S, "sIz", (Conditions.ContainsMorpheme((self.with_, self.without))).not_())
        containsNess: Conditions.ContainsMorpheme = Conditions.ContainsMorpheme((self.ness,))
        self.nom_S.add_(self.ness_S, "lI~k", Conditions.not_(containsNess))
        self.nom_S.add_(self.ness_S, "lI!ğ", Conditions.not_(containsNess))
        self.nom_S.add_(self.agt_S, ">cI", Conditions.not_(Conditions.ContainsMorpheme((self.agt,))))
        self.nom_S.add_(self.justLike_S, "+msI", Conditions.not_(Conditions.ContainsMorpheme((self.justLike,))))
        self.nom_S.add_(self.dim_S, ">cI~k", Conditions.HAS_NO_SURFACE.and_not(
            Conditions.ContainsMorpheme((self.dim,))))
        self.nom_S.add_(self.dim_S, ">cI!ğ", Conditions.HAS_NO_SURFACE.and_not(
            Conditions.ContainsMorpheme((self.dim,))))
        self.nom_S.add_(self.dim_S, "cAğIz", Conditions.HAS_NO_SURFACE)
        self.nounCompoundRoot_S.add_(self.a3plCompound_S, "lAr",
                                     Conditions.has(r_attribute=RootAttribute.CompoundP3sgRoot))
        self.nounCompoundRoot_S.add_(self.a3plCompound2_S, "lArI",
                                     Conditions.has(r_attribute=RootAttribute.CompoundP3sgRoot))
        self.a3plCompound_S.add_(self.p3sg_S, "I").add_(self.p2sg_S, "In").add_(self.p1sg_S, "Im").add_(
            self.p1pl_S, "ImIz").add_(self.p2pl_S, "InIz").add_(self.p3pl_S, "I")
        self.a3plCompound2_S.add_empty(self.pnonCompound2_S)
        self.pnonCompound2_S.add_empty(self.nom_ST)
        rootIsAbbrv: Conditions.Condition = Conditions.SecondaryPosIs(SecondaryPos.Abbreviation)
        possessionCond: Conditions.Condition = Conditions.not_have(r_attribute=RootAttribute.FamilyMember).and_not(
            rootIsAbbrv)
        self.a3sg_S.add_empty(self.pnon_S,
                              Conditions.not_have(r_attribute=RootAttribute.FamilyMember)
                              ).add_(self.p1sg_S,
                                     "Im",
                                     possessionCond
                                     ).add_(self.p2sg_S,
                                            "In",
                                            possessionCond.and_not(
                                                Conditions.PreviousGroupContainsMorpheme((self.justLike,)))).add_(
            self.p3sg_S, "+sI", possessionCond).add_empty(self.p3sg_S,
                                                          Conditions.has(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.p1pl_S, "ImIz", possessionCond).add_(
            self.p2pl_S, "InIz",
            possessionCond.and_not(Conditions.PreviousGroupContainsMorpheme((self.justLike,)))).add_(
            self.p3pl_S, "lArI", possessionCond)
        self.a3pl_S.add_empty(self.pnon_S, Conditions.not_have(r_attribute=RootAttribute.FamilyMember))
        self.a3pl_S.add_(self.p1sg_S, "Im", possessionCond).add_(self.p2sg_S, "In", possessionCond).add_empty(
            self.p1sg_S, Conditions.has(r_attribute=RootAttribute.ImplicitP1sg)).add_empty(
            self.p2sg_S, Conditions.has(r_attribute=RootAttribute.ImplicitP2sg)).add_(self.p3sg_S, "I",
                                                                                      possessionCond).add_(
            self.p1pl_S, "ImIz", possessionCond).add_(self.p2pl_S, "InIz", possessionCond).add_(
            self.p3pl_S, "I", possessionCond)
        self.nounSuRoot_S.add_empty(self.a3sgSu_S)
        self.nounSuRoot_S.add_(self.a3pl_S, "lar")
        self.a3sgSu_S.add_empty(self.pnon_S).add_(self.p1sg_S, "yum").add_(self.p2sg_S, "yun").add_(self.p3sg_S,
                                                                                                    "yu").add_(
            self.p1pl_S, "yumuz").add_(self.p2pl_S, "yunuz").add_(self.p3pl_S, "lArI")
        self.pnon_S.add_empty(self.nom_ST, Conditions.not_have(r_attribute=RootAttribute.FamilyMember))
        equCond: Conditions.Condition = Conditions.prvious_morpheme_is(self.a3pl).or_(
            (Conditions.ContainsMorpheme(
                (self.adj, self.futPart, self.presPart, self.narrPart, self.pastPart))).not_()).or_(
            Conditions.ContainsMorphemeSequence((self.able, self.verb, self.pastPart)))
        self.pnon_S.add_(self.dat_ST, "+yA", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.abl_ST, ">dAn", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.loc_ST, ">dA", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.acc_ST, "+yI", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.gen_ST, "+nIn", Conditions.previous_state_is_not(self.a3sgSu_S)).add_(
            self.gen_ST, "yIn", Conditions.previous_state_is(self.a3sgSu_S)).add_(
            self.equ_ST, ">cA", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg).and_(equCond)).add_(
            self.ins_ST, "+ylA")
        self.pnon_S.add_(self.dat_ST, "+nA", Conditions.has(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.abl_ST, "+ndAn", Conditions.has(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.loc_ST, "+ndA", Conditions.has(r_attribute=RootAttribute.CompoundP3sg)).add_(
            self.equ_ST, "+ncA", Conditions.has(r_attribute=RootAttribute.CompoundP3sg).and_(equCond)).add_(
            self.acc_ST, "+nI", Conditions.has(r_attribute=RootAttribute.CompoundP3sg))
        self.pnon_S.add_empty(self.dat_ST, Conditions.has(r_attribute=RootAttribute.ImplicitDative))
        self.p1sg_S.add_empty(self.nom_ST).add_(self.dat_ST, "A").add_(self.loc_ST, "dA").add_(self.abl_ST, "dAn").add_(
            self.ins_ST, "lA").add_(self.gen_ST, "In").add_(
            self.equ_ST, "cA", equCond.or_(Conditions.ContainsMorpheme((self.pastPart,)))).add_(self.acc_ST, "I")
        self.p2sg_S.add_empty(self.nom_ST).add_(self.dat_ST, "A").add_(self.loc_ST, "dA").add_(self.abl_ST, "dAn").add_(
            self.ins_ST, "lA").add_(self.gen_ST, "In").add_(
            self.equ_ST, "cA", equCond.or_(Conditions.ContainsMorpheme((self.pastPart,)))).add_(self.acc_ST, "I")
        self.p3sg_S.add_empty(self.nom_ST).add_(self.dat_ST, "nA").add_(self.loc_ST, "ndA").add_(self.abl_ST,
                                                                                                 "ndAn").add_(
            self.ins_ST, "ylA").add_(self.gen_ST, "nIn").add_(
            self.equ_ST, "ncA", equCond.or_(Conditions.ContainsMorpheme((self.pastPart,)))).add_(self.acc_ST, "nI")
        self.p1pl_S.add_empty(self.nom_ST).add_(self.dat_ST, "A").add_(self.loc_ST, "dA").add_(self.abl_ST, "dAn").add_(
            self.ins_ST, "lA").add_(self.gen_ST, "In").add_(
            self.equ_ST, "cA", equCond.or_(Conditions.ContainsMorpheme((self.pastPart,)))).add_(self.acc_ST, "I")
        self.p2pl_S.add_empty(self.nom_ST).add_(self.dat_ST, "A").add_(self.loc_ST, "dA").add_(self.abl_ST, "dAn").add_(
            self.ins_ST, "lA").add_(self.gen_ST, "In").add_(
            self.equ_ST, "cA", equCond.or_(Conditions.ContainsMorpheme((self.pastPart,)))).add_(self.acc_ST, "I")
        self.p3pl_S.add_empty(self.nom_ST).add_(self.dat_ST, "nA").add_(self.loc_ST, "ndA").add_(self.abl_ST,
                                                                                                 "ndAn").add_(
            self.ins_ST, "ylA").add_(self.gen_ST, "nIn").add_(self.equ_ST, "+ncA").add_(self.acc_ST, "nI")
        self.nom_ST.add_(self.dim_S, ">cI~k", Conditions.HAS_NO_SURFACE.and_not(rootIsAbbrv))
        self.nom_ST.add_(self.dim_S, ">cI!ğ", Conditions.HAS_NO_SURFACE.and_not(rootIsAbbrv))
        self.nom_ST.add_(self.dim_S, "cAğIz", Conditions.HAS_NO_SURFACE.and_not(rootIsAbbrv))
        self.dim_S.add_empty(self.noun_S)
        emptyAdjNounSeq: Conditions.Condition = Conditions.ContainsMorphemeSequence(
            (self.adj, self.zero, self.noun, self.a3sg, self.pnon, self.nom))
        self.nom_ST.add_(self.ness_S, "lI~k", Conditions.CURRENT_GROUP_EMPTY.and_not(containsNess).and_not(
            emptyAdjNounSeq).and_not(rootIsAbbrv))
        self.nom_ST.add_(self.ness_S, "lI!ğ", Conditions.CURRENT_GROUP_EMPTY.and_not(containsNess).and_not(
            emptyAdjNounSeq).and_not(rootIsAbbrv))
        self.ness_S.add_empty(self.noun_S)
        self.nom_ST.add_(self.agt_S, ">cI",
                         Conditions.CURRENT_GROUP_EMPTY.and_not(Conditions.ContainsMorpheme((self.adj, self.agt))))
        self.agt_S.add_empty(self.noun_S)
        noun2VerbZeroDerivationCondition: Conditions.Condition = Conditions.HAS_TAIL.and_not(
            Conditions.CURRENT_GROUP_EMPTY.and_(Conditions.LastDerivationIs(self.adjZeroDeriv_S)))
        self.nom_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.dat_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.abl_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.loc_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.ins_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.gen_ST.add_empty(self.nounZeroDeriv_S, noun2VerbZeroDerivationCondition)
        self.nounZeroDeriv_S.add_empty(self.nVerb_S)
        noSurfaceAfterDerivation: Conditions.Condition = Conditions.NoSurfaceAfterDerivation()
        self.nom_ST.add_(self.with_S, "lI", noSurfaceAfterDerivation.and_not(
            Conditions.ContainsMorpheme((self.with_, self.without))).and_not(rootIsAbbrv))
        self.nom_ST.add_(self.without_S, "sIz", noSurfaceAfterDerivation.and_not(
            Conditions.ContainsMorpheme((self.with_, self.without, self.inf1))).and_not(rootIsAbbrv))
        self.nom_ST.add_(self.justLike_S, "+msI", noSurfaceAfterDerivation.and_not(
            Conditions.ContainsMorpheme((self.justLike, self.futPart, self.pastPart, self.presPart, self.adj))).and_not(
            rootIsAbbrv))
        self.nom_ST.add_(self.justLike_S, "ImsI",
                         Conditions.not_have(p_attribute=PhoneticAttribute.LastLetterVowel).and_(
                             noSurfaceAfterDerivation).and_not(
                             Conditions.ContainsMorpheme(
                                 (self.justLike, self.futPart, self.pastPart, self.presPart, self.adj))).and_not(
                             rootIsAbbrv))
        self.nom_ST.add_(self.related_S, "sAl", noSurfaceAfterDerivation.and_not(
            Conditions.ContainsMorpheme((self.with_, self.without, self.related))).and_not(rootIsAbbrv))
        self.with_S.add_empty(self.adjectiveRoot_ST)
        self.without_S.add_empty(self.adjectiveRoot_ST)
        self.related_S.add_empty(self.adjectiveRoot_ST)
        self.justLike_S.add_empty(self.adjectiveRoot_ST)
        notRelRepetition: Conditions.Condition = (Conditions.HasTailSequence((self.rel, self.adj, self.zero, self.noun,
                                                                              self.a3sg, self.pnon, self.loc))).not_()
        self.loc_ST.add_(self.rel_S, "ki", notRelRepetition)
        self.rel_S.add_empty(self.adjectiveRoot_ST)
        time: Conditions.Condition = Conditions.CURRENT_GROUP_EMPTY.and_(Conditions.SecondaryPosIs(SecondaryPos.Time))
        dun: DictionaryItem = self.lexicon.get_item_by_id("dün_Noun_Time")
        gun: DictionaryItem = self.lexicon.get_item_by_id("gün_Noun_Time")
        bugun: DictionaryItem = self.lexicon.get_item_by_id("bugün_Noun_Time")
        ileri: DictionaryItem = self.lexicon.get_item_by_id("ileri_Noun")
        geri: DictionaryItem = self.lexicon.get_item_by_id("geri_Noun")
        ote: DictionaryItem = self.lexicon.get_item_by_id("öte_Noun")
        beri: DictionaryItem = self.lexicon.get_item_by_id("beri_Noun")
        time2: Conditions.Condition = Conditions.root_is_any((dun, gun, bugun))
        self.nom_ST.add_(self.rel_S, "ki", time.and_not(time2))
        self.nom_ST.add_(self.rel_S, "ki", Conditions.root_is_any((ileri, geri, ote, beri)))
        self.nom_ST.add_(self.rel_S, "kü", time2.and_(time))
        self.gen_ST.add_(self.relToPron_S, "ki")
        self.relToPron_S.add_empty(self.pronAfterRel_S)
        verbDeriv: Conditions.ContainsMorpheme = Conditions.ContainsMorpheme((self.inf1, self.inf2, self.inf3,
                                                                              self.pastPart, self.futPart))
        self.nom_ST.add_(self.become_S, "lAş",
                         noSurfaceAfterDerivation.and_not(Conditions.ContainsMorpheme((self.adj,))).and_not(
                             verbDeriv).and_not(rootIsAbbrv))
        self.become_S.add_empty(self.verbRoot_S)
        self.nom_ST.add_(self.acquire_S, "lAn",
                         noSurfaceAfterDerivation.and_not(Conditions.ContainsMorpheme((self.adj,))).and_not(
                             verbDeriv).and_not(rootIsAbbrv))
        self.acquire_S.add_empty(self.verbRoot_S)
        self.nounInf1Root_S.add_empty(self.a3sgInf1_S)
        self.a3sgInf1_S.add_empty(self.pnonInf1_S)
        self.pnonInf1_S.add_empty(self.nom_ST)
        self.pnonInf1_S.add_(self.abl_ST, "tAn")
        self.pnonInf1_S.add_(self.loc_ST, "tA")
        self.pnonInf1_S.add_(self.ins_ST, "lA")
        self.nounActOfRoot_S.add_empty(self.a3sgActOf_S)
        self.nounActOfRoot_S.add_(self.a3plActOf_S, "lar")
        self.a3sgActOf_S.add_empty(self.pnonActOf)
        self.a3plActOf_S.add_empty(self.pnonActOf)
        self.pnonActOf.add_empty(self.nom_ST)

    def connect_proper_nouns_and_abbreviations(self):
        self.nounProper_S.add_empty(self.a3sg_S)
        self.nounProper_S.add_(self.a3pl_S, "lAr")
        self.puncProperSeparator_S.add_empty(self.a3sg_S)
        self.puncProperSeparator_S.add_(self.a3pl_S, "lAr")
        self.nounAbbrv_S.add_empty(self.a3sg_S)
        self.nounAbbrv_S.add_(self.a3pl_S, "lAr")
        self.nounNoSuffix_S.add_empty(self.nounA3sgNoSuffix_S)
        self.nounA3sgNoSuffix_S.add_empty(self.nounPnonNoSuffix_S)
        self.nounPnonNoSuffix_S.add_empty(self.nounNomNoSuffix_ST)

    def connect_adjective_states(self):
        self.adjectiveRoot_ST.add_empty(self.adjZeroDeriv_S, Conditions.HAS_TAIL)
        self.adjZeroDeriv_S.add_empty(self.noun_S)
        self.adjZeroDeriv_S.add_empty(self.nVerb_S)
        self.adjectiveRoot_ST.add_(self.aLy_S, ">cA")
        self.aLy_S.add_empty(self.advRoot_ST)
        self.adjectiveRoot_ST.add_(self.aAsIf_S, ">cA",
                                   (Conditions.ContainsMorpheme(
                                       (self.asIf, self.ly, self.agt, self.with_, self.justLike))).not_())
        self.aAsIf_S.add_empty(self.adjectiveRoot_ST)
        self.adjectiveRoot_ST.add_(self.aAgt_S, ">cI",
                                   (Conditions.ContainsMorpheme(
                                       (self.asIf, self.ly, self.agt, self.with_, self.justLike))).not_())
        self.aAgt_S.add_empty(self.noun_S)
        self.adjectiveRoot_ST.add_(self.justLike_S, "+msI", (Conditions.NoSurfaceAfterDerivation()).and_(
            (Conditions.ContainsMorpheme((self.justLike,))).not_()))
        self.adjectiveRoot_ST.add_(self.justLike_S, "ImsI",
                                   Conditions.not_have(p_attribute=PhoneticAttribute.LastLetterVowel).and_(
                                       Conditions.NoSurfaceAfterDerivation()).and_(
                                       Conditions.ContainsMorpheme((self.justLike,)).not_()))
        self.adjectiveRoot_ST.add_(self.become_S, "lAş", Conditions.NoSurfaceAfterDerivation())
        self.adjectiveRoot_ST.add_(self.acquire_S, "lAn", Conditions.NoSurfaceAfterDerivation())
        c1: Conditions.Condition = Conditions.PreviousMorphemeIsAny((self.futPart, self.pastPart))
        self.adjAfterVerb_S.add_empty(self.aPnon_ST, c1)
        self.adjAfterVerb_S.add_(self.aP1sg_ST, "Im", c1)
        self.adjAfterVerb_S.add_(self.aP2sg_ST, "In", c1)
        self.adjAfterVerb_S.add_(self.aP3sg_ST, "I", c1)
        self.adjAfterVerb_S.add_(self.aP1pl_ST, "ImIz", c1)
        self.adjAfterVerb_S.add_(self.aP2pl_ST, "InIz", c1)
        self.adjAfterVerb_S.add_(self.aP3pl_ST, "lArI", c1)
        self.adjectiveRoot_ST.add_(self.ness_S, "lI~k")
        self.adjectiveRoot_ST.add_(self.ness_S, "lI!ğ")
        self.adjAfterVerb_ST.add_(self.ness_S, "lI~k", Conditions.PreviousMorphemeIs(self.aorPart))
        self.adjAfterVerb_ST.add_(self.ness_S, "lI!ğ", Conditions.PreviousMorphemeIs(self.aorPart))

    def connect_numeral_states(self):
        self.numeralRoot_ST.add_(self.ness_S, "lI~k")
        self.numeralRoot_ST.add_(self.ness_S, "lI!ğ")
        self.numeralRoot_ST.add_empty(self.numZeroDeriv_S, Conditions.HAS_TAIL)
        self.numZeroDeriv_S.add_empty(self.noun_S)
        self.numZeroDeriv_S.add_empty(self.nVerb_S)
        self.numeralRoot_ST.add_(self.justLike_S, "+msI", Conditions.NoSurfaceAfterDerivation().and_(
            Conditions.ContainsMorpheme((self.justLike,)).not_()))
        self.numeralRoot_ST.add_(self.justLike_S, "ImsI",
                                 Conditions.not_have(p_attribute=PhoneticAttribute.LastLetterVowel).and_(
                                     Conditions.NoSurfaceAfterDerivation()).and_(
                                     Conditions.ContainsMorpheme((self.justLike,)).not_()))

    def connect_verb_after_noun_adj_states(self):
        self.nVerb_S.add_empty(self.nPresent_S)
        self.nVerb_S.add_(self.nPast_S, "+y>dI")
        self.nVerb_S.add_(self.nNarr_S, "+ymIş")
        self.nVerb_S.add_(self.nCond_S, "+ysA")
        self.nVerb_S.add_(self.vWhile_S, "+yken")
        degilRoot: DictionaryItem = self.lexicon.get_item_by_id("değil_Verb")
        self.nVerbDegil_S.add_empty(self.nNeg_S, Conditions.root_is(degilRoot))
        self.nNeg_S.copy_outgoing_transitions_from(self.nVerb_S)
        noFamily: Conditions.Condition = Conditions.not_have(r_attribute=RootAttribute.FamilyMember)
        verbDeriv: Conditions.ContainsMorpheme = Conditions.ContainsMorpheme(
            (self.inf1, self.inf2, self.inf3, self.pastPart, self.futPart))
        allowA1sgTrans: Conditions.Condition = noFamily.and_not(
            Conditions.ContainsMorphemeSequence((self.p1sg, self.nom))).and_not(verbDeriv)
        allowA2sgTrans: Conditions.Condition = noFamily.and_not(
            Conditions.ContainsMorphemeSequence((self.p2sg, self.nom))).and_not(verbDeriv)
        allowA3plTrans: Conditions.Condition = noFamily.and_not(
            Conditions.PreviousGroupContains((self.a3pl_S,))).and_not(
            Conditions.ContainsMorphemeSequence((self.p3pl, self.nom))).and_not(verbDeriv)
        allowA2plTrans: Conditions.Condition = noFamily.and_not(
            Conditions.ContainsMorphemeSequence((self.p2pl, self.nom))).and_not(verbDeriv)
        allowA1plTrans: Conditions.Condition = noFamily.and_not(
            Conditions.ContainsMorphemeSequence((self.p1sg, self.nom))).and_not(
            Conditions.ContainsMorphemeSequence((self.p1pl, self.nom))).and_not(verbDeriv)
        self.nPresent_S.add_(self.nA1sg_ST, "+yIm", allowA1sgTrans)
        self.nPresent_S.add_(self.nA2sg_ST, "sIn", allowA2sgTrans)
        self.nPresent_S.add_empty(self.nA3sg_S)
        self.nPresent_S.add_empty(self.nA3sg_ST, Conditions.root_is(degilRoot))
        self.nPresent_S.add_(self.nA3pl_ST, "lAr", Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg).and_not(
            Conditions.PreviousGroupContainsMorpheme((self.inf1,))).and_(allowA3plTrans))
        self.nPast_S.add_(self.nA1sg_ST, "m", allowA1sgTrans)
        self.nNarr_S.add_(self.nA1sg_ST, "Im", allowA1sgTrans)
        self.nPast_S.add_(self.nA2sg_ST, "n", allowA2sgTrans)
        self.nNarr_S.add_(self.nA2sg_ST, "sIn", allowA2sgTrans)
        self.nPast_S.add_(self.nA1pl_ST, "k", allowA1plTrans)
        self.nNarr_S.add_(self.nA1pl_ST, "Iz", allowA1plTrans)
        self.nPresent_S.add_(self.nA1pl_ST, "+yIz", allowA1plTrans)
        self.nPast_S.add_(self.nA2pl_ST, "InIz", allowA2plTrans)
        self.nNarr_S.add_(self.nA2pl_ST, "sInIz", allowA2plTrans)
        self.nPresent_S.add_(self.nA2pl_ST, "sInIz", allowA2plTrans)
        self.nPast_S.add_(self.nA3pl_ST, "lAr",
                          Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg).and_(allowA3plTrans))
        self.nNarr_S.add_(self.nA3pl_ST, "lAr",
                          Conditions.not_have(r_attribute=RootAttribute.CompoundP3sg).and_(allowA3plTrans))
        self.nPast_S.add_empty(self.nA3sg_ST)
        self.nNarr_S.add_empty(self.nA3sg_ST)
        self.nNarr_S.add_(self.nCond_S, "sA")
        self.nCond_S.add_(self.nA1sg_ST, "m", allowA1sgTrans)
        self.nCond_S.add_(self.nA2sg_ST, "n", allowA2sgTrans)
        self.nCond_S.add_(self.nA1pl_ST, "k", allowA1plTrans)
        self.nCond_S.add_(self.nA2pl_ST, "nIz", allowA2plTrans)
        self.nCond_S.add_empty(self.nA3sg_ST)
        self.nCond_S.add_(self.nA3pl_ST, "lAr")
        rejectNoCopula: Conditions.Condition = (
            Conditions.CurrentGroupContainsAny((self.nPast_S, self.nCond_S, self.nCopBeforeA3pl_S))).not_()
        self.nA1sg_ST.add_(self.nCop_ST, "dIr", rejectNoCopula)
        self.nA2sg_ST.add_(self.nCop_ST, "dIr", rejectNoCopula)
        self.nA1pl_ST.add_(self.nCop_ST, "dIr", rejectNoCopula)
        self.nA2pl_ST.add_(self.nCop_ST, "dIr", rejectNoCopula)
        self.nA3sg_S.add_(self.nCop_ST, ">dIr", rejectNoCopula)
        self.nA3pl_ST.add_(self.nCop_ST, "dIr", rejectNoCopula)
        asIfCond: Conditions.PreviousMorphemeIsAny = Conditions.PreviousMorphemeIsAny((self.narr,))
        self.nA3sg_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nA1sg_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nA2sg_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nA1pl_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nA2pl_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nA3pl_ST.add_(self.vAsIf_S, ">cAsInA", asIfCond)
        self.nPresent_S.add_(self.nCopBeforeA3pl_S, ">dIr")
        self.nCopBeforeA3pl_S.add_(self.nA3pl_ST, "lAr")

    def connect_pronoun_states(self):
        ben: DictionaryItem = self.lexicon.get_item_by_id("ben_Pron_Pers")
        sen: DictionaryItem = self.lexicon.get_item_by_id("sen_Pron_Pers")
        o: DictionaryItem = self.lexicon.get_item_by_id("o_Pron_Pers")
        biz: DictionaryItem = self.lexicon.get_item_by_id("biz_Pron_Pers")
        siz: DictionaryItem = self.lexicon.get_item_by_id("siz_Pron_Pers")
        falan: DictionaryItem = self.lexicon.get_item_by_id("falan_Pron_Pers")
        falanca: DictionaryItem = self.lexicon.get_item_by_id("falanca_Pron_Pers")
        self.pronPers_S.add_empty(self.pA1sg_S, Conditions.root_is(ben))
        self.pronPers_S.add_empty(self.pA2sg_S, Conditions.root_is(sen))
        self.pronPers_S.add_empty(self.pA3sg_S, Conditions.root_is_any((o, falan, falanca)))
        self.pronPers_S.add_(self.pA3pl_S, "nlAr", Conditions.root_is(o))
        self.pronPers_S.add_(self.pA3pl_S, "lAr", Conditions.root_is_any((falan, falanca)))
        self.pronPers_S.add_empty(self.pA1pl_S, Conditions.root_is(biz))
        self.pronPers_S.add_(self.pA1pl_S, "lAr", Conditions.root_is(biz))
        self.pronPers_S.add_empty(self.pA2pl_S, Conditions.root_is(siz))
        self.pronPers_S.add_(self.pA2pl_S, "lAr", Conditions.root_is(siz))
        self.pronPers_Mod_S.add_empty(self.pA1sgMod_S, Conditions.root_is(ben))
        self.pronPers_Mod_S.add_empty(self.pA2sgMod_S, Conditions.root_is(sen))
        self.pA1sgMod_S.add_empty(self.pPnonMod_S)
        self.pA2sgMod_S.add_empty(self.pPnonMod_S)
        self.pPnonMod_S.add_(self.pDat_ST, "A")
        self.pA1sg_S.add_empty(self.pPnon_S)
        self.pA2sg_S.add_empty(self.pPnon_S)
        self.pA3sg_S.add_empty(self.pPnon_S)
        self.pA1pl_S.add_empty(self.pPnon_S)
        self.pA2pl_S.add_empty(self.pPnon_S)
        self.pA3pl_S.add_empty(self.pPnon_S)
        self.pronAfterRel_S.add_empty(self.pA3sgRel_S)
        self.pronAfterRel_S.add_(self.pA3plRel_S, "lAr")
        self.pA3sgRel_S.add_empty(self.pPnonRel_S)
        self.pA3plRel_S.add_empty(self.pPnonRel_S)
        self.pPnonRel_S.add_empty(self.pNom_ST)
        self.pPnonRel_S.add_(self.pDat_ST, "+nA")
        self.pPnonRel_S.add_(self.pAcc_ST, "+nI")
        self.pPnonRel_S.add_(self.pAbl_ST, "+ndAn")
        self.pPnonRel_S.add_(self.pLoc_ST, "+ndA")
        self.pPnonRel_S.add_(self.pIns_ST, "+ylA")
        self.pPnonRel_S.add_(self.pGen_ST, "+nIn")
        bu: DictionaryItem = self.lexicon.get_item_by_id("bu_Pron_Demons")
        su: DictionaryItem = self.lexicon.get_item_by_id("şu_Pron_Demons")
        o_demons: DictionaryItem = self.lexicon.get_item_by_id("o_Pron_Demons")
        self.pronDemons_S.add_empty(self.pA3sg_S)
        self.pronDemons_S.add_(self.pA3pl_S, "nlAr")
        birbiri: DictionaryItem = self.lexicon.get_item_by_id("birbiri_Pron_Quant")
        biri: DictionaryItem = self.lexicon.get_item_by_id("biri_Pron_Quant")
        bazi: DictionaryItem = self.lexicon.get_item_by_id("bazı_Pron_Quant")
        bircogu: DictionaryItem = self.lexicon.get_item_by_id("birçoğu_Pron_Quant")
        birkaci: DictionaryItem = self.lexicon.get_item_by_id("birkaçı_Pron_Quant")
        beriki: DictionaryItem = self.lexicon.get_item_by_id("beriki_Pron_Quant")
        cogu: DictionaryItem = self.lexicon.get_item_by_id("çoğu_Pron_Quant")
        cumlesi: DictionaryItem = self.lexicon.get_item_by_id("cümlesi_Pron_Quant")
        hep: DictionaryItem = self.lexicon.get_item_by_id("hep_Pron_Quant")
        herbiri: DictionaryItem = self.lexicon.get_item_by_id("herbiri_Pron_Quant")
        herkes: DictionaryItem = self.lexicon.get_item_by_id("herkes_Pron_Quant")
        hicbiri: DictionaryItem = self.lexicon.get_item_by_id("hiçbiri_Pron_Quant")
        hepsi: DictionaryItem = self.lexicon.get_item_by_id("hepsi_Pron_Quant")
        kimi: DictionaryItem = self.lexicon.get_item_by_id("kimi_Pron_Quant")
        kimse: DictionaryItem = self.lexicon.get_item_by_id("kimse_Pron_Quant")
        oburku: DictionaryItem = self.lexicon.get_item_by_id("öbürkü_Pron_Quant")
        oburu: DictionaryItem = self.lexicon.get_item_by_id("öbürü_Pron_Quant")
        tumu: DictionaryItem = self.lexicon.get_item_by_id("tümü_Pron_Quant")
        topu: DictionaryItem = self.lexicon.get_item_by_id("topu_Pron_Quant")
        umum: DictionaryItem = self.lexicon.get_item_by_id("umum_Pron_Quant")
        self.pronQuant_S.add_empty(self.pQuantA3sg_S,
                                   Conditions.root_is_none((herkes, umum, hepsi, cumlesi, hep, tumu, birkaci, topu)))
        self.pronQuant_S.add_(self.pQuantA3pl_S, "lAr", Conditions.root_is_none(
            (hep, hepsi, birkaci, umum, cumlesi, cogu, bircogu, herbiri, tumu, hicbiri, topu, oburu)))
        self.pronQuant_S.add_(self.pQuantA1pl_S, "lAr", Conditions.root_is_any((bazi,)))
        self.pronQuant_S.add_(self.pQuantA2pl_S, "lAr", Conditions.root_is_any((bazi,)))
        self.pronQuant_S.add_empty(self.pQuantA3pl_S, Conditions.root_is_any(
            (herkes, umum, birkaci, hepsi, cumlesi, cogu, bircogu, tumu, topu)))
        self.pronQuant_S.add_empty(self.a3sg_S, Conditions.root_is(kimse))
        self.pronQuant_S.add_(self.a3pl_S, "lAr", Conditions.root_is_any((kimse,)))
        self.pronQuant_S.add_empty(self.pQuantA1pl_S, Conditions.root_is_any(
            (biri, bazi, birbiri, birkaci, herbiri, hep, kimi, cogu, bircogu, tumu, topu, hicbiri)))
        self.pronQuant_S.add_empty(self.pQuantA2pl_S, Conditions.root_is_any(
            (biri, bazi, birbiri, birkaci, herbiri, hep, kimi, cogu, bircogu, tumu, topu, hicbiri)))
        self.pronQuantModified_S.add_empty(self.pQuantModA3pl_S)
        self.pQuantModA3pl_S.add_(self.pP3pl_S, "lArI")
        self.pQuantA3sg_S.add_empty(self.pP3sg_S, Conditions.root_is_any(
            (biri, birbiri, kimi, herbiri, hicbiri, oburu, oburku, beriki)).and_(
            Conditions.not_have(p_attribute=PhoneticAttribute.ModifiedPronoun)))
        self.pQuantA3sg_S.add_(self.pP3sg_S, "sI",
                               Conditions.root_is_any((biri, bazi, kimi, birbiri, herbiri, hicbiri, oburku)).and_(
                                   Conditions.not_have(p_attribute=PhoneticAttribute.ModifiedPronoun)))
        self.pQuantA3pl_S.add_(self.pP3pl_S, "I", Conditions.root_is_any((biri, bazi, birbiri, kimi, oburku, beriki)))
        self.pQuantA3pl_S.add_empty(self.pP3pl_S,
                                    Conditions.root_is_any((hepsi, birkaci, cumlesi, cogu, tumu, topu, bircogu)))
        self.pQuantA3pl_S.add_empty(self.pPnon_S, Conditions.root_is_any((herkes, umum, oburku, beriki)))
        self.pQuantA1pl_S.add_(self.pP1pl_S, "ImIz")
        self.pQuantA2pl_S.add_(self.pP2pl_S, "InIz")
        ne: DictionaryItem = self.lexicon.get_item_by_id("ne_Pron_Ques")
        nere: DictionaryItem = self.lexicon.get_item_by_id("nere_Pron_Ques")
        kim: DictionaryItem = self.lexicon.get_item_by_id("kim_Pron_Ques")
        self.pronQues_S.add_empty(self.pQuesA3sg_S)
        self.pronQues_S.add_(self.pQuesA3pl_S, "lAr")
        self.pQuesA3sg_S.add_empty(self.pPnon_S).add_(self.pP3sg_S, "+sI").add_(self.pP1sg_S, "Im",
                                                                                Conditions.root_is_not(ne)).add_(
            self.pP1sg_S, "yIm", Conditions.root_is(ne)).add_(self.pP2sg_S, "In", Conditions.root_is_not(ne)).add_(
            self.pP2sg_S, "yIn", Conditions.root_is(ne)).add_(self.pP1pl_S, "ImIz", Conditions.root_is_not(ne)).add_(
            self.pP1pl_S, "yImIz", Conditions.root_is(ne))
        self.pQuesA3pl_S.add_empty(self.pPnon_S).add_(self.pP3sg_S, "I").add_(self.pP1sg_S, "Im").add_(self.pP1pl_S,
                                                                                                       "ImIz")
        kendi: DictionaryItem = self.lexicon.get_item_by_id("kendi_Pron_Reflex")
        self.pronReflex_S.add_empty(self.pReflexA1sg_S).add_empty(self.pReflexA2sg_S).add_empty(
            self.pReflexA3sg_S).add_empty(self.pReflexA1pl_S).add_empty(self.pReflexA2pl_S).add_empty(
            self.pReflexA3pl_S)
        self.pReflexA1sg_S.add_(self.pP1sg_S, "Im")
        self.pReflexA2sg_S.add_(self.pP2sg_S, "In")
        self.pReflexA3sg_S.add_(self.pP3sg_S, "+sI").add_empty(self.pP3sg_S)
        self.pReflexA1pl_S.add_(self.pP1pl_S, "ImIz")
        self.pReflexA2pl_S.add_(self.pP2pl_S, "InIz")
        self.pReflexA3pl_S.add_(self.pP3pl_S, "lArI")
        nGroup: Conditions.Condition = Conditions.root_is_none((ne, nere, falan, falanca, hep, herkes))
        yGroup: Conditions.Condition = Conditions.root_is_any((ne, nere, falan, falanca, hep, herkes))
        self.pPnon_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", Conditions.root_is_none(
            (ben, sen, ne, nere, falan, falanca, herkes))).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(
            self.pLoc_ST, "+ndA", nGroup).add_(self.pLoc_ST, ">dA", yGroup).add_(self.pAbl_ST, "+ndAn", nGroup).add_(
            self.pAbl_ST, ">dAn", yGroup).add_(self.pGen_ST, "+nIn",
                                               nGroup.and_(Conditions.root_is_none((biz, ben, sen)))).add_(
            self.pGen_ST, "im", Conditions.root_is_any((ben, biz))).add_(self.pGen_ST, "in",
                                                                         Conditions.root_is(sen)).add_(
            self.pGen_ST, "+yIn", yGroup.and_(Conditions.root_is_none((biz,)))).add_(self.pEqu_ST, ">cA", yGroup).add_(
            self.pEqu_ST, ">cA", nGroup).add_(self.pIns_ST, "+ylA", yGroup).add_(self.pIns_ST, "+nlA", nGroup).add_(
            self.pIns_ST, "+nInlA", nGroup.and_(Conditions.root_is_any((bu, su, o, sen)))).add_(
            self.pIns_ST, "inle", Conditions.root_is(siz)).add_(self.pIns_ST, "imle",
                                                                Conditions.root_is_any((biz, ben)))
        conditionpP1sg_S: Conditions.Condition = Conditions.root_is_any((kim, ben, ne, nere, kendi))
        self.pP1sg_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA",
                                                                                Conditions.root_is_any((kendi,))).add_(
            self.pAbl_ST, "+ndAn", Conditions.root_is_any((kendi,))).add_(self.pEqu_ST, "+ncA",
                                                                          Conditions.root_is_any((kendi,))).add_(
            self.pIns_ST, "+nlA", conditionpP1sg_S).add_(self.pGen_ST, "+nIn", conditionpP1sg_S)
        conditionP2sg: Conditions.Condition = Conditions.root_is_any((kim, sen, ne, nere, kendi))
        self.pP2sg_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA",
                                                                                Conditions.root_is_any((kendi,))).add_(
            self.pAbl_ST, "+ndAn", Conditions.root_is_any((kendi,))).add_(self.pEqu_ST, "+ncA",
                                                                          Conditions.root_is_any((kendi,))).add_(
            self.pIns_ST, "+nlA", conditionP2sg).add_(self.pGen_ST, "+nIn", conditionP2sg)
        p3sgCond: Conditions.Condition = Conditions.root_is_any(
            (kendi, kim, ne, nere, o, bazi, biri, birbiri, herbiri, hep, kimi, hicbiri))
        self.pP3sg_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA", p3sgCond).add_(
            self.pAbl_ST, "+ndAn", p3sgCond).add_(self.pGen_ST, "+nIn", p3sgCond).add_(self.pEqu_ST, "ncA",
                                                                                       p3sgCond).add_(
            self.pIns_ST, "+ylA", p3sgCond)
        hepCnd: Conditions.Condition = Conditions.root_is_any((kendi, kim, ne, nere, biz, siz, biri, birbiri, birkaci,
                                                               herbiri, hep, kimi, cogu, bircogu, tumu, topu, bazi,
                                                               hicbiri))
        self.pP1pl_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA", hepCnd).add_(
            self.pAbl_ST, "+ndAn", hepCnd).add_(self.pGen_ST, "+nIn", hepCnd).add_(self.pEqu_ST, "+ncA", hepCnd).add_(
            self.pIns_ST, "+nlA", hepCnd)
        self.pP2pl_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA", hepCnd).add_(
            self.pAbl_ST, "+ndAn", hepCnd).add_(self.pGen_ST, "+nIn", hepCnd).add_(self.pEqu_ST, "+ncA", hepCnd).add_(
            self.pIns_ST, "+nlA", hepCnd)
        hepsiCnd: Conditions.Condition = Conditions.root_is_any((kendi, kim, ne, nere, o, bazi, biri, herkes, umum,
                                                                 birkaci, hepsi, cumlesi, cogu, bircogu, birbiri, tumu,
                                                                 kimi, topu))
        self.pP3pl_S.add_empty(self.pNom_ST).add_(self.pDat_ST, "+nA", nGroup).add_(self.pAcc_ST, "+nI", nGroup).add_(
            self.pDat_ST, "+yA", yGroup).add_(self.pAcc_ST, "+yI", yGroup).add_(self.pLoc_ST, "+ndA", hepsiCnd).add_(
            self.pAbl_ST, "+ndAn", hepsiCnd).add_(self.pGen_ST, "+nIn",
                                                  hepsiCnd.or_(Conditions.root_is_any((sen, siz)))).add_(
            self.pEqu_ST, "+ncA", hepsiCnd).add_(self.pIns_ST, "+ylA", hepsiCnd)
        self.pNom_ST.add_(self.with_S, "+nlI", Conditions.root_is_any((bu, su, o_demons, ben, sen, o, biz, siz)))
        self.pNom_ST.add_(self.with_S, "lI", Conditions.root_is_any((nere,)))
        self.pNom_ST.add_(self.with_S, "+ylI", Conditions.root_is_any((ne,)))
        self.pNom_ST.add_(self.without_S, "+nsIz",
                          Conditions.root_is_any((nere, bu, su, o_demons, ben, sen, o, biz, siz)))
        self.pNom_ST.add_(self.without_S, "+ysIz", Conditions.root_is_any((ne,)))
        self.pGen_ST.add_(self.rel_S, "ki", Conditions.root_is_any((nere, bu, su, o_demons, ne, sen, o, biz, siz)))
        notRelRepetition: Conditions.Condition = (Conditions.HasTailSequence((self.rel, self.adj, self.zero, self.noun,
                                                                              self.a3sg, self.pnon, self.loc))).not_()
        self.pLoc_ST.add_(self.rel_S, "ki", notRelRepetition)
        self.pIns_ST.add_(self.vWhile_S, "+yken")
        self.pNom_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pDat_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pLoc_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pAbl_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pGen_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pIns_ST.add_empty(self.pronZeroDeriv_S, Conditions.HAS_TAIL)
        self.pronZeroDeriv_S.add_empty(self.pvVerbRoot_S)

    def connect_verb_after_pronoun(self):
        self.pvVerbRoot_S.add_empty(self.pvPresent_S)
        self.pvVerbRoot_S.add_(self.vWhile_S, "+yken")
        self.pvVerbRoot_S.add_(self.pvPast_S, "+ydI")
        self.pvVerbRoot_S.add_(self.pvNarr_S, "+ymIş")
        self.pvVerbRoot_S.add_(self.pvCond_S, "+ysA")
        allowA1sgTrans = (Conditions.PreviousGroupContains((self.pA1pl_S, self.pP1sg_S))).not_()
        allowA1plTrans = (
            Conditions.PreviousGroupContains((self.pA1sg_S, self.pA2sg_S, self.pP1sg_S, self.pP2sg_S))).not_()
        allowA2sgTrans = (Conditions.PreviousGroupContains((self.pA2pl_S, self.pP2sg_S))).not_()
        allowA2plTrans = (Conditions.PreviousGroupContains((self.pA2sg_S, self.pP2pl_S))).not_()
        self.pvPresent_S.add_(self.pvA1sg_ST, "+yIm", allowA1sgTrans)
        self.pvPresent_S.add_(self.pvA2sg_ST, "sIn", allowA2sgTrans)
        self.pvPresent_S.add_empty(self.nA3sg_S)
        self.pvPresent_S.add_(self.pvA1pl_ST, "+yIz", allowA1plTrans)
        self.pvPresent_S.add_(self.pvA2pl_ST, "sInIz")
        self.pvPresent_S.add_(self.pvA3pl_ST, "lAr", Conditions.PreviousGroupContains((self.pLoc_ST,)))
        self.pvPast_S.add_(self.pvA1sg_ST, "m", allowA1sgTrans)
        self.pvPast_S.add_(self.pvA2sg_ST, "n", allowA2sgTrans)
        self.pvPast_S.add_(self.pvA1pl_ST, "k", allowA1plTrans)
        self.pvPast_S.add_(self.pvA2pl_ST, "InIz")
        self.pvPast_S.add_(self.pvA3pl_ST, "lAr")
        self.pvPast_S.add_empty(self.pvA3sg_ST)
        self.pvNarr_S.add_(self.pvA1sg_ST, "Im", allowA1sgTrans)
        self.pvNarr_S.add_(self.pvA2sg_ST, "sIn", allowA2sgTrans)
        self.pvNarr_S.add_(self.pvA1pl_ST, "Iz", allowA1plTrans)
        self.pvNarr_S.add_(self.pvA2pl_ST, "sInIz")
        self.pvNarr_S.add_(self.pvA3pl_ST, "lAr")
        self.pvNarr_S.add_empty(self.pvA3sg_ST)
        self.pvNarr_S.add_(self.pvCond_S, "sA")
        self.pvCond_S.add_(self.pvA1sg_ST, "m", allowA1sgTrans)
        self.pvCond_S.add_(self.pvA2sg_ST, "n", allowA2sgTrans)
        self.pvCond_S.add_(self.pvA1pl_ST, "k", allowA1plTrans)
        self.pvCond_S.add_(self.pvA2pl_ST, "nIz", allowA2plTrans)
        self.pvCond_S.add_empty(self.pvA3sg_ST)
        self.pvCond_S.add_(self.pvA3pl_ST, "lAr")
        rejectNoCopula = (
            Conditions.CurrentGroupContainsAny((self.pvPast_S, self.pvCond_S, self.pvCopBeforeA3pl_S))).not_()
        self.pvA1sg_ST.add_(self.pvCop_ST, "dIr", rejectNoCopula)
        self.pvA2sg_ST.add_(self.pvCop_ST, "dIr", rejectNoCopula)
        self.pvA1pl_ST.add_(self.pvCop_ST, "dIr", rejectNoCopula)
        self.pvA2pl_ST.add_(self.pvCop_ST, "dIr", rejectNoCopula)
        self.pvA3sg_S.add_(self.pvCop_ST, ">dIr", rejectNoCopula)
        self.pvA3pl_ST.add_(self.pvCop_ST, "dIr", rejectNoCopula)
        self.pvPresent_S.add_(self.pvCopBeforeA3pl_S, ">dIr")
        self.pvCopBeforeA3pl_S.add_(self.pvA3pl_ST, "lAr")

    def connect_verbs(self):
        self.verbRoot_S.add_empty(self.vImp_S)
        self.vImp_S.add_empty(self.vA2sg_ST).add_(self.vA2sg_ST, "sAnA").add_(self.vA3sg_ST, "sIn").add_(self.vA2pl_ST,
                                                                                                         "+yIn").add_(
            self.vA2pl_ST, "+yInIz").add_(self.vA2pl_ST, "sAnIzA").add_(self.vA3pl_ST, "sInlAr")
        self.verbRoot_S.add_(self.vCausT_S, "t", Conditions.has(r_attribute=RootAttribute.Causative_t).or_(
            Conditions.LastDerivationIs(self.vCausTir_S)).and_not(
            Conditions.LastDerivationIsAny((self.vCausT_S, self.vPass_S, self.vAble_S))))
        self.verbRoot_S.add_(self.vCausTir_S, ">dIr",
                             Conditions.has(p_attribute=PhoneticAttribute.LastLetterConsonant).and_not(
                                 Conditions.LastDerivationIsAny((self.vCausTir_S, self.vPass_S, self.vAble_S))))
        self.vCausT_S.add_empty(self.verbRoot_S)
        self.vCausTir_S.add_empty(self.verbRoot_S)
        self.verbRoot_S.add_(self.vProgYor_S, "Iyor",
                             Conditions.not_have(p_attribute=PhoneticAttribute.LastLetterVowel))
        self.verbRoot_VowelDrop_S.add_(self.vProgYor_S, "Iyor")
        self.vProgYor_S.add_(self.vA1sg_ST, "um").add_(self.vA2sg_ST, "sun").add_empty(self.vA3sg_ST).add_(
            self.vA1pl_ST, "uz").add_(self.vA2pl_ST, "sunuz").add_(self.vA3pl_ST, "lar").add_(self.vCond_S, "sa").add_(
            self.vPastAfterTense_S, "du").add_(self.vNarrAfterTense_S, "muş").add_(self.vCopBeforeA3pl_S, "dur").add_(
            self.vWhile_S, "ken")
        self.verbRoot_S.add_(self.vProgMakta_S, "mAktA")
        self.vProgMakta_S.add_(self.vA1sg_ST, "yIm").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(
            self.vA1pl_ST, "yIz").add_(self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr").add_(self.vCond_S,
                                                                                               "ysA").add_(
            self.vPastAfterTense_S, "ydI").add_(self.vNarrAfterTense_S, "ymIş").add_(self.vCopBeforeA3pl_S, "dIr").add_(
            self.vWhile_S, "yken")
        self.verbRoot_S.add_(self.vAor_S, "Ir",
                             Conditions.has(r_attribute=RootAttribute.Aorist_I).or_(Conditions.HAS_SURFACE))
        self.verbRoot_S.add_(self.vAor_S, "Ar",
                             Conditions.has(r_attribute=RootAttribute.Aorist_A).and_(Conditions.HAS_NO_SURFACE))
        self.vAor_S.add_(self.vA1sg_ST, "Im").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                       "Iz").add_(
            self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr").add_(self.vPastAfterTense_S, "dI").add_(
            self.vNarrAfterTense_S, "mIş").add_(self.vCond_S, "sA").add_(self.vCopBeforeA3pl_S, "dIr").add_(
            self.vWhile_S, "ken")
        self.verbRoot_S.add_(self.vNeg_S, "mA", Conditions.previous_morpheme_is_not(self.able))
        self.vNeg_S.add_empty(self.vImp_S).add_(self.vPast_S, "dI").add_(self.vFut_S, "yAcA~k").add_(self.vFut_S,
                                                                                                     "yAcA!ğ").add_(
            self.vNarr_S, "mIş").add_(self.vProgMakta_S, "mAktA").add_(self.vOpt_S, "yA").add_(self.vDesr_S, "sA").add_(
            self.vNeces_S, "mAlI").add_(self.vInf1_S, "mAk").add_(self.vInf2_S, "mA").add_(self.vInf3_S, "yIş").add_(
            self.vActOf_S, "mAcA").add_(self.vPastPart_S, "dI~k").add_(self.vPastPart_S, "dI!ğ").add_(self.vFutPart_S,
                                                                                                      "yAcA~k").add_(
            self.vFutPart_S, "yAcA!ğ").add_(self.vPresPart_S, "yAn").add_(self.vNarrPart_S, "mIş").add_(
            self.vSinceDoingSo_S, "yAlI").add_(self.vByDoingSo_S, "yArAk").add_(self.vHastily_S, "yIver").add_(
            self.vEverSince_S, "yAgör").add_(self.vAfterDoing_S, "yIp").add_(self.vWhen_S, "yIncA").add_(
            self.vAsLongAs_S, "dIkçA").add_(self.vNotState_S, "mAzlI~k").add_(self.vNotState_S, "mAzlI!ğ").add_(
            self.vFeelLike_S, "yAsI")
        self.verbRoot_S.add_(self.vNegProg1_S, "m")
        self.vNegProg1_S.add_(self.vProgYor_S, "Iyor")
        self.vNeg_S.add_(self.vAorNeg_S, "z")
        self.vNeg_S.add_empty(self.vAorNegEmpty_S)
        self.vAorNeg_S.add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA2pl_ST, "sInIz").add_(
            self.vA3pl_ST, "lAr").add_(self.vPastAfterTense_S, "dI").add_(self.vNarrAfterTense_S, "mIş").add_(
            self.vCond_S, "sA").add_(self.vCopBeforeA3pl_S, "dIr").add_(self.vWhile_S, "ken")
        self.vAorNegEmpty_S.add_(self.vA1sg_ST, "m").add_(self.vA1pl_ST, "yIz")
        self.vNeg_S.add_(self.vAorPartNeg_S, "z")
        self.vAorPartNeg_S.add_empty(self.adjAfterVerb_ST)
        self.verbRoot_S.add_(self.vAble_S, "+yAbil", Conditions.last_derivation_is(self.vAble_S).not_())
        self.vAble_S.add_empty(self.verbRoot_S)
        self.vAbleNeg_S.add_empty(self.vAbleNegDerivRoot_S)
        self.vAbleNegDerivRoot_S.add_(self.vNeg_S, "mA")
        self.vAbleNegDerivRoot_S.add_(self.vNegProg1_S, "m")
        self.vNeg_S.add_(self.vAble_S, "yAbil")
        self.verbRoot_S.add_(self.vUnable_S, "+yAmA", Conditions.previous_morpheme_is_not(self.able))
        self.vUnable_S.copy_outgoing_transitions_from(self.vNeg_S)
        self.verbRoot_S.add_(self.vUnableProg1_S, "+yAm")
        self.vUnableProg1_S.add_(self.vProgYor_S, "Iyor")
        self.verbRoot_S.add_(self.vInf1_S, "mA~k")
        self.vInf1_S.add_empty(self.nounInf1Root_S)
        self.verbRoot_S.add_(self.vInf2_S, "mA")
        self.vInf2_S.add_empty(self.noun_S)
        self.verbRoot_S.add_(self.vInf3_S, "+yIş")
        self.vInf3_S.add_empty(self.noun_S)
        self.verbRoot_S.add_(self.vAgt_S, "+yIcI")
        self.vAgt_S.add_empty(self.noun_S)
        self.vAgt_S.add_empty(self.adjAfterVerb_ST)
        self.verbRoot_S.add_(self.vActOf_S, "mAcA")
        self.vActOf_S.add_empty(self.nounActOfRoot_S)
        self.verbRoot_S.add_(self.vPastPart_S, ">dI~k")
        self.verbRoot_S.add_(self.vPastPart_S, ">dI!ğ")
        self.vPastPart_S.add_empty(self.noun_S)
        self.vPastPart_S.add_empty(self.adjAfterVerb_S)
        self.verbRoot_S.add_(self.vFutPart_S, "+yAcA~k")
        self.verbRoot_S.add_(self.vFutPart_S, "+yAcA!ğ")
        self.vFutPart_S.add_empty(self.noun_S, Conditions.HAS_TAIL)
        self.vFutPart_S.add_empty(self.adjAfterVerb_S)
        self.verbRoot_S.add_(self.vNarrPart_S, "mIş")
        self.vNarrPart_S.add_empty(self.adjectiveRoot_ST)
        self.verbRoot_S.add_(self.vAorPart_S, "Ir",
                             Conditions.has(r_attribute=RootAttribute.Aorist_I).or_(Conditions.HAS_SURFACE))
        self.verbRoot_S.add_(self.vAorPart_S, "Ar",
                             Conditions.has(r_attribute=RootAttribute.Aorist_A).and_(Conditions.HAS_NO_SURFACE))
        self.vAorPart_S.add_empty(self.adjAfterVerb_ST)
        self.verbRoot_S.add_(self.vPresPart_S, "+yAn")
        self.vPresPart_S.add_empty(self.noun_S, Conditions.HAS_TAIL)
        self.vPresPart_S.add_empty(self.adjAfterVerb_ST)
        self.verbRoot_S.add_(self.vFeelLike_S, "+yAsI")
        self.vFeelLike_S.add_empty(self.noun_S, Conditions.HAS_TAIL)
        self.vFeelLike_S.add_empty(self.adjAfterVerb_ST)
        self.verbRoot_S.add_(self.vNotState_S, "mAzlI~k")
        self.verbRoot_S.add_(self.vNotState_S, "mAzlI!ğ")
        self.vNotState_S.add_empty(self.noun_S)
        self.vRecip_S.add_empty(self.verbRoot_S)
        self.vImplicitRecipRoot_S.add_empty(self.vRecip_S)
        self.vImplicitReflexRoot_S.add_empty(self.vReflex_S)
        self.vReflex_S.add_empty(self.verbRoot_S)
        self.verbRoot_S.add_(self.vPass_S, "In", Conditions.has(r_attribute=RootAttribute.Passive_In).and_not(
            Conditions.ContainsMorpheme((self.pass_,))))
        self.verbRoot_S.add_(self.vPass_S, "InIl", Conditions.has(r_attribute=RootAttribute.Passive_In).and_not(
            Conditions.ContainsMorpheme((self.pass_,))))
        self.verbRoot_S.add_(self.vPass_S, "+nIl",
                             Conditions.PreviousStateIsAny((self.vCausT_S, self.vCausTir_S)).or_(
                                 Conditions.not_have(r_attribute=RootAttribute.Passive_In).and_not(
                                     Conditions.ContainsMorpheme((self.pass_,)))))
        self.vPass_S.add_empty(self.verbRoot_S)
        self.vCond_S.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "n").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                     "k").add_(
            self.vA2pl_ST, "nIz").add_(self.vA3pl_ST, "lAr")
        self.verbRoot_S.add_(self.vPast_S, ">dI")
        self.vPast_S.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "n").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                     "k").add_(
            self.vA2pl_ST, "nIz").add_(self.vA3pl_ST, "lAr")
        self.vPast_S.add_(self.vCond_S, "ysA")
        self.verbRoot_S.add_(self.vNarr_S, "mIş")
        self.vNarr_S.add_(self.vA1sg_ST, "Im").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                        "Iz").add_(
            self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr")
        self.vNarr_S.add_(self.vCond_S, "sA")
        self.vNarr_S.add_(self.vPastAfterTense_S, "tI")
        self.vNarr_S.add_(self.vCopBeforeA3pl_S, "tIr")
        self.vNarr_S.add_(self.vWhile_S, "ken")
        self.vNarr_S.add_(self.vNarrAfterTense_S, "mIş")
        self.vPastAfterTense_S.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "n").add_empty(self.vA3sg_ST).add_(
            self.vA1pl_ST, "k").add_(self.vA2pl_ST, "nIz").add_(self.vA3pl_ST, "lAr")
        self.vNarrAfterTense_S.add_(self.vA1sg_ST, "Im").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(
            self.vA1pl_ST, "Iz").add_(self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr")
        self.vNarrAfterTense_S.add_(self.vWhile_S, "ken")
        self.vNarrAfterTense_S.add_(self.vCopBeforeA3pl_S, "tIr")
        self.verbRoot_S.add_(self.vFut_S, "+yAcA~k")
        self.verbRoot_S.add_(self.vFut_S, "+yAcA!ğ")
        self.vFut_S.add_(self.vA1sg_ST, "Im").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                       "Iz").add_(
            self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr")
        self.vFut_S.add_(self.vCond_S, "sA")
        self.vFut_S.add_(self.vPastAfterTense_S, "tI")
        self.vFut_S.add_(self.vNarrAfterTense_S, "mIş")
        self.vFut_S.add_(self.vCopBeforeA3pl_S, "tIr")
        self.vFut_S.add_(self.vWhile_S, "ken")
        diYiCondition = Conditions.RootSurfaceIsAny(("di", "yi"))
        deYeCondition = Conditions.RootSurfaceIsAny(("de", "ye"))
        cMultiVerb = Conditions.PreviousMorphemeIsAny(
            (self.everSince, self.repeat, self.almost, self.hastily, self.stay, self.start)).not_()
        self.vDeYeRoot_S.add_(self.vFut_S, "yece~k", diYiCondition).add_(self.vFut_S, "yece!ğ", diYiCondition).add_(
            self.vProgYor_S, "yor", diYiCondition).add_(self.vAble_S, "yebil", diYiCondition).add_(self.vAbleNeg_S,
                                                                                                   "ye",
                                                                                                   diYiCondition).add_(
            self.vInf3_S, "yiş", Conditions.RootSurfaceIsAny(("yi",))).add_(self.vFutPart_S, "yece~k",
                                                                            diYiCondition).add_(self.vFutPart_S,
                                                                                                "yece!ğ",
                                                                                                diYiCondition).add_(
            self.vPresPart_S, "yen", diYiCondition).add_(self.vEverSince_S, "yegel",
                                                         diYiCondition.and_(cMultiVerb)).add_(self.vRepeat_S, "yedur",
                                                                                              diYiCondition.and_(
                                                                                                  cMultiVerb)).add_(
            self.vRepeat_S, "yegör", diYiCondition.and_(cMultiVerb)).add_(self.vAlmost_S, "yeyaz",
                                                                          diYiCondition.and_(cMultiVerb)).add_(
            self.vStart_S, "yekoy", diYiCondition.and_(cMultiVerb)).add_(self.vSinceDoingSo_S, "yeli",
                                                                         diYiCondition).add_(self.vByDoingSo_S, "yerek",
                                                                                             diYiCondition).add_(
            self.vFeelLike_S, "yesi", diYiCondition).add_(self.vAfterDoing_S, "yip", diYiCondition).add_(
            self.vWithoutBeingAbleToHaveDoneSo_S, "yemeden", diYiCondition).add_(self.vOpt_S, "ye", diYiCondition)
        self.vDeYeRoot_S.add_(self.vCausTir_S, "dir", deYeCondition).add_(self.vPass_S, "n", deYeCondition).add_(
            self.vPass_S, "nil", deYeCondition).add_(self.vPast_S, "di", deYeCondition).add_(self.vNarr_S, "miş",
                                                                                             deYeCondition).add_(
            self.vAor_S, "r", deYeCondition).add_(self.vNeg_S, "me", deYeCondition).add_(self.vNegProg1_S, "m",
                                                                                         deYeCondition).add_(
            self.vProgMakta_S, "mekte", deYeCondition).add_(self.vDesr_S, "se", deYeCondition).add_(self.vInf1_S,
                                                                                                    "mek",
                                                                                                    deYeCondition).add_(
            self.vInf2_S, "me", deYeCondition).add_(self.vInf3_S, "yiş", Conditions.RootSurfaceIsAny(("de",))).add_(
            self.vPastPart_S, "di~k", deYeCondition).add_(
            self.vPastPart_S, "di!ğ", deYeCondition).add_(self.vNarrPart_S, "miş", deYeCondition).add_(
            self.vHastily_S, "yiver", diYiCondition.and_(cMultiVerb)).add_(
            self.vAsLongAs_S, "dikçe").add_(self.vWithoutHavingDoneSo_S, "meden").add_(self.vWithoutHavingDoneSo_S,
                                                                                       "meksizin").add_(
            self.vNeces_S, "meli").add_(self.vNotState_S, "mezli~k").add_(self.vNotState_S,
                                                                          "mezli!ğ").add_empty(
            self.vImp_S, Conditions.RootSurfaceIs("de")).add_empty(self.vImpYemekYe_S,
                                                                   Conditions.RootSurfaceIs("ye")).add_empty(
            self.vImpYemekYi_S, Conditions.RootSurfaceIs("yi"))
        self.vImpYemekYi_S.add_(self.vA2pl_ST, "yin").add_(self.vA2pl_ST, "yiniz")
        self.vImpYemekYe_S.add_empty(self.vA2sg_ST).add_(self.vA2sg_ST, "sene").add_(self.vA3sg_ST, "sin").add_(
            self.vA2pl_ST, "senize").add_(self.vA3pl_ST, "sinler")
        self.verbRoot_S.add_(self.vOpt_S, "+yA")
        self.vOpt_S.add_(self.vA1sg_ST, "yIm").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                        "lIm").add_(
            self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr").add_(self.vPastAfterTense_S, "ydI").add_(
            self.vNarrAfterTense_S, "ymIş")
        self.verbRoot_S.add_(self.vDesr_S, "sA")
        self.vDesr_S.add_(self.vA1sg_ST, "m").add_(self.vA2sg_ST, "n").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                     "k").add_(
            self.vA2pl_ST, "nIz").add_(self.vA3pl_ST, "lAr").add_(self.vPastAfterTense_S, "ydI").add_(
            self.vNarrAfterTense_S, "ymIş")
        self.verbRoot_S.add_(self.vNeces_S, "mAlI")
        self.vNeces_S.add_(self.vA1sg_ST, "yIm").add_(self.vA2sg_ST, "sIn").add_empty(self.vA3sg_ST).add_(self.vA1pl_ST,
                                                                                                          "yIz").add_(
            self.vA2pl_ST, "sInIz").add_(self.vA3pl_ST, "lAr").add_(self.vPastAfterTense_S, "ydI").add_(self.vCond_S,
                                                                                                        "ysA").add_(
            self.vNarrAfterTense_S, "ymIş").add_(self.vCopBeforeA3pl_S, "dIr").add_(self.vWhile_S, "yken")
        previousNotPastNarrCond = (
            Conditions.PreviousStateIsAny((self.vPastAfterTense_S, self.vNarrAfterTense_S, self.vCond_S))).not_()
        self.vA3pl_ST.add_(self.vPastAfterTense_ST, "dI", previousNotPastNarrCond)
        self.vA3pl_ST.add_(self.vNarrAfterTense_ST, "mIş", previousNotPastNarrCond)
        self.vA3pl_ST.add_(self.vCond_ST, "sA", previousNotPastNarrCond)
        a3plCopWhile = Conditions.PreviousMorphemeIsAny(
            (self.prog1, self.prog2, self.neces, self.fut, self.narr, self.aor))
        self.vA3pl_ST.add_(self.vCop_ST, "dIr", a3plCopWhile)
        self.vA3pl_ST.add_(self.vWhile_S, "ken", a3plCopWhile)
        a3sgCopWhile = Conditions.PreviousMorphemeIsAny(
            (self.prog1, self.prog2, self.neces, self.fut, self.narr, self.aor))
        self.vA1sg_ST.add_(self.vCop_ST, "dIr", a3sgCopWhile)
        self.vA2sg_ST.add_(self.vCop_ST, "dIr", a3sgCopWhile)
        self.vA3sg_ST.add_(self.vCop_ST, ">dIr", a3sgCopWhile)
        self.vA1pl_ST.add_(self.vCop_ST, "dIr", a3sgCopWhile)
        self.vA2pl_ST.add_(self.vCop_ST, "dIr", a3sgCopWhile)
        self.vCopBeforeA3pl_S.add_(self.vA3pl_ST, "lAr")
        previousPast = Conditions.PreviousMorphemeIs(self.past).and_not(
            Conditions.ContainsMorpheme((self.cond, self.desr)))
        self.vA2pl_ST.add_(self.vCondAfterPerson_ST, "sA", previousPast)
        self.vA2sg_ST.add_(self.vCondAfterPerson_ST, "sA", previousPast)
        self.vA1sg_ST.add_(self.vCondAfterPerson_ST, "sA", previousPast)
        self.vA1pl_ST.add_(self.vCondAfterPerson_ST, "sA", previousPast)
        self.verbRoot_S.add_(self.vEverSince_S, "+yAgel", cMultiVerb)
        self.verbRoot_S.add_(self.vRepeat_S, "+yAdur", cMultiVerb)
        self.verbRoot_S.add_(self.vRepeat_S, "+yAgör", cMultiVerb)
        self.verbRoot_S.add_(self.vAlmost_S, "+yAyaz", cMultiVerb)
        self.verbRoot_S.add_(self.vHastily_S, "+yIver", cMultiVerb)
        self.verbRoot_S.add_(self.vStay_S, "+yAkal", cMultiVerb)
        self.verbRoot_S.add_(self.vStart_S, "+yAkoy", cMultiVerb)
        self.vEverSince_S.add_empty(self.verbRoot_S)
        self.vRepeat_S.add_empty(self.verbRoot_S)
        self.vAlmost_S.add_empty(self.verbRoot_S)
        self.vHastily_S.add_empty(self.verbRoot_S)
        self.vStay_S.add_empty(self.verbRoot_S)
        self.vStart_S.add_empty(self.verbRoot_S)
        self.vA3sg_ST.add_(self.vAsIf_S, ">cAsInA", Conditions.PreviousMorphemeIsAny((self.aor, self.narr)))
        self.verbRoot_S.add_(self.vWhen_S, "+yIncA")
        self.verbRoot_S.add_(self.vSinceDoingSo_S, "+yAlI")
        self.verbRoot_S.add_(self.vByDoingSo_S, "+yArAk")
        self.verbRoot_S.add_(self.vAdamantly_S, "+yAsIyA")
        self.verbRoot_S.add_(self.vAfterDoing_S, "+yIp")
        self.verbRoot_S.add_(self.vWithoutBeingAbleToHaveDoneSo_S, "+yAmAdAn")
        self.verbRoot_S.add_(self.vAsLongAs_S, ">dIkçA")
        self.verbRoot_S.add_(self.vWithoutHavingDoneSo_S, "mAdAn")
        self.verbRoot_S.add_(self.vWithoutHavingDoneSo_S, "mAksIzIn")
        self.vAsIf_S.add_empty(self.advRoot_ST)
        self.vSinceDoingSo_S.add_empty(self.advRoot_ST)
        self.vByDoingSo_S.add_empty(self.advRoot_ST)
        self.vAdamantly_S.add_empty(self.advRoot_ST)
        self.vAfterDoing_S.add_empty(self.advRoot_ST)
        self.vWithoutBeingAbleToHaveDoneSo_S.add_empty(self.advRoot_ST)
        self.vAsLongAs_S.add_empty(self.advRoot_ST)
        self.vWithoutHavingDoneSo_S.add_empty(self.advRoot_ST)
        self.vWhile_S.add_empty(self.advRoot_ST)
        self.vWhen_S.add_empty(self.advNounRoot_ST)

    def connect_question(self):
        self.questionRoot_S.add_empty(self.qPresent_S)
        self.questionRoot_S.add_(self.qPast_S, "ydI")
        self.questionRoot_S.add_(self.qNarr_S, "ymIş")
        self.qPresent_S.add_(self.qA1sg_ST, "yIm")
        self.qPresent_S.add_(self.qA2sg_ST, "sIn")
        self.qPresent_S.add_empty(self.qA3sg_ST)
        self.qPast_S.add_(self.qA1sg_ST, "m")
        self.qNarr_S.add_(self.qA1sg_ST, "Im")
        self.qPast_S.add_(self.qA2sg_ST, "n")
        self.qNarr_S.add_(self.qA2sg_ST, "sIn")
        self.qPast_S.add_(self.qA1pl_ST, "k")
        self.qNarr_S.add_(self.qA1pl_ST, "Iz")
        self.qPresent_S.add_(self.qA1pl_ST, "+yIz")
        self.qPast_S.add_(self.qA2pl_ST, "InIz")
        self.qNarr_S.add_(self.qA2pl_ST, "sInIz")
        self.qPresent_S.add_(self.qA2pl_ST, "sInIz")
        self.qPast_S.add_(self.qA3pl_ST, "lAr")
        self.qNarr_S.add_(self.qA3pl_ST, "lAr")
        self.qPast_S.add_empty(self.qA3sg_ST)
        self.qNarr_S.add_empty(self.qA3sg_ST)
        reject_no_copula = Conditions.CurrentGroupContainsAny((self.qPast_S,)).not_()
        self.qA1sg_ST.add_(self.qCop_ST, "dIr", reject_no_copula)
        self.qA2sg_ST.add_(self.qCop_ST, "dIr", reject_no_copula)
        self.qA3sg_ST.add_(self.qCop_ST, ">dIr", reject_no_copula)
        self.qA1pl_ST.add_(self.qCop_ST, "dIr", reject_no_copula)
        self.qA2pl_ST.add_(self.qCop_ST, "dIr", reject_no_copula)
        self.qPresent_S.add_(self.pvCopBeforeA3pl_S, "dIr")
        self.qCopBeforeA3pl_S.add_(self.qA3pl_ST, "lAr")

    def connect_adverbs(self):
        self.advNounRoot_ST.add_empty(self.avZero_S)
        self.avZero_S.add_empty(self.avNounAfterAdvRoot_ST)
        self.avNounAfterAdvRoot_ST.add_empty(self.avA3sg_S)
        self.avA3sg_S.add_empty(self.avPnon_S)
        self.avPnon_S.add_(self.avDat_ST, "+yA")
        self.advForVerbDeriv_ST.add_empty(self.avZeroToVerb_S)
        self.avZeroToVerb_S.add_empty(self.nVerb_S)

    def connect_last_vowel_drop_words(self):
        self.nounLastVowelDropRoot_S.add_empty(self.a3sgLastVowelDrop_S)
        self.nounLastVowelDropRoot_S.add_(self.a3PlLastVowelDrop_S, "lAr")
        self.a3sgLastVowelDrop_S.add_empty(self.pNonLastVowelDrop_S)
        self.a3PlLastVowelDrop_S.add_empty(self.pNonLastVowelDrop_S)
        self.pNonLastVowelDrop_S.add_(self.loc_ST, ">dA")
        self.pNonLastVowelDrop_S.add_(self.abl_ST, ">dAn")
        self.adjLastVowelDropRoot_S.add_empty(self.zeroLastVowelDrop_S)
        self.postpLastVowelDropRoot_S.add_empty(self.zeroLastVowelDrop_S)
        self.zeroLastVowelDrop_S.add_empty(self.nounLastVowelDropRoot_S)

    def connect_postpositives(self):
        self.postpRoot_ST.add_empty(self.postpZero_S)
        self.postpZero_S.add_empty(self.nVerb_S)
        gibi_gen: DictionaryItem = self.lexicon.get_item_by_id("gibi_Postp_PCGen")
        gibi_nom: DictionaryItem = self.lexicon.get_item_by_id("gibi_Postp_PCNom")
        sonra_abl: DictionaryItem = self.lexicon.get_item_by_id("sonra_Postp_PCAbl")
        self.postpZero_S.add_empty(self.po2nRoot_S, Conditions.root_is_any((gibi_gen, gibi_nom, sonra_abl)))
        self.po2nRoot_S.add_empty(self.po2nA3sg_S)
        self.po2nRoot_S.add_(self.po2nA3pl_S, "lAr")
        self.po2nA3sg_S.add_(self.po2nP3sg_S, "+sI")
        self.po2nA3sg_S.add_(self.po2nP1sg_S, "m", Conditions.root_is_any((gibi_gen, gibi_nom)))
        self.po2nA3sg_S.add_(self.po2nP2sg_S, "n", Conditions.root_is_any((gibi_gen, gibi_nom)))
        self.po2nA3sg_S.add_(self.po2nP1pl_S, "miz", Conditions.root_is_any((gibi_gen, gibi_nom)))
        self.po2nA3sg_S.add_(self.po2nP2pl_S, "niz", Conditions.root_is_any((gibi_gen, gibi_nom)))
        self.po2nA3pl_S.add_(self.po2nP3sg_S, "+sI")
        self.po2nA3pl_S.add_empty(self.po2nPnon_S)
        self.po2nP3sg_S.add_empty(self.po2nNom_ST).add_(self.po2nDat_ST, "nA").add_(self.po2nLoc_ST, "ndA").add_(
            self.po2nAbl_ST, "ndAn").add_(self.po2nIns_ST, "ylA").add_(self.po2nGen_ST, "nIn").add_(self.po2nAcc_ST,
                                                                                                    "nI")
        self.po2nPnon_S.add_empty(self.po2nNom_ST).add_(self.po2nDat_ST, "A").add_(self.po2nLoc_ST, "dA").add_(
            self.po2nAbl_ST, "dAn").add_(self.po2nIns_ST, "lA").add_(self.po2nGen_ST, "In").add_(self.po2nEqu_ST,
                                                                                                 "cA").add_(
            self.po2nAcc_ST, "I")
        self.po2nP1sg_S.add_(self.po2nDat_ST, "e")
        self.po2nP2sg_S.add_(self.po2nDat_ST, "e")
        self.po2nP1pl_S.add_(self.po2nDat_ST, "e")
        self.po2nP2pl_S.add_(self.po2nDat_ST, "e")

    def connect_imek(self):
        self.imekRoot_S.add_(self.imekPast_S, "di")
        self.imekRoot_S.add_(self.imekNarr_S, "miş")
        self.imekRoot_S.add_(self.imekCond_S, "se")
        self.imekPast_S.add_(self.imekA1sg_ST, "m")
        self.imekPast_S.add_(self.imekA2sg_ST, "n")
        self.imekPast_S.add_empty(self.imekA3sg_ST)
        self.imekPast_S.add_(self.imekA1pl_ST, "k")
        self.imekPast_S.add_(self.imekA2pl_ST, "niz")
        self.imekPast_S.add_(self.imekA3pl_ST, "ler")
        self.imekNarr_S.add_(self.imekA1sg_ST, "im")
        self.imekNarr_S.add_(self.imekA2sg_ST, "sin")
        self.imekNarr_S.add_empty(self.imekA3sg_ST)
        self.imekNarr_S.add_(self.imekA1pl_ST, "iz")
        self.imekNarr_S.add_(self.imekA2pl_ST, "siniz")
        self.imekNarr_S.add_(self.imekA3pl_ST, "ler")
        self.imekPast_S.add_(self.imekCond_S, "yse")
        self.imekNarr_S.add_(self.imekCond_S, "se")
        self.imekCond_S.add_(self.imekA1sg_ST, "m")
        self.imekCond_S.add_(self.imekA2sg_ST, "n")
        self.imekCond_S.add_empty(self.imekA3sg_ST)
        self.imekCond_S.add_(self.imekA1pl_ST, "k")
        self.imekCond_S.add_(self.imekA2pl_ST, "niz")
        self.imekCond_S.add_(self.imekA3pl_ST, "ler")
        reject_no_copula: Conditions.Condition = Conditions.CurrentGroupContainsAny((self.imekPast_S,)).not_()
        self.imekA1sg_ST.add_(self.imekCop_ST, "dir", reject_no_copula)
        self.imekA2sg_ST.add_(self.imekCop_ST, "dir", reject_no_copula)
        self.imekA3sg_ST.add_(self.imekCop_ST, "tir", reject_no_copula)
        self.imekA1pl_ST.add_(self.imekCop_ST, "dir", reject_no_copula)
        self.imekA2pl_ST.add_(self.imekCop_ST, "dir", reject_no_copula)
        self.imekA3pl_ST.add_(self.imekCop_ST, "dir", reject_no_copula)

    def handle_post_processing_connections(self):
        self.verbLastVowelDropModRoot_S.add_(self.vPass_S, template="Il")
        self.verbLastVowelDropUnmodRoot_S.copy_outgoing_transitions_from(self.verbRoot_S)
        self.verbLastVowelDropUnmodRoot_S.remove_transitions_to(self.pass_)

    def get_root_state(self, item: DictionaryItem, phonetic_attributes: Set[PhoneticAttribute]) -> MorphemeState:
        root: MorphemeState = self.item_root_state_map.get(item.id_)
        if root is not None:
            return root
        elif PhoneticAttribute.LastLetterDropped in phonetic_attributes:
            return self.verbRoot_VowelDrop_S
        elif item.has_attribute(RootAttribute.Reciprocal):
            return self.vImplicitRecipRoot_S
        elif item.has_attribute(RootAttribute.Reflexive):
            return self.vImplicitReflexRoot_S
        else:
            if item.primary_pos == PrimaryPos.Noun:
                if item.secondary_pos == SecondaryPos.ProperNoun:
                    return self.nounProper_S
                elif item.secondary_pos == SecondaryPos.Abbreviation:
                    return self.nounAbbrv_S
                elif (item.secondary_pos == SecondaryPos.Email) or (item.secondary_pos == SecondaryPos.Url) or \
                        (item.secondary_pos == SecondaryPos.HashTag) or (item.secondary_pos == SecondaryPos.Mention):
                    return self.nounProper_S
                elif item.secondary_pos == SecondaryPos.Emoticon or item.secondary_pos == SecondaryPos.RomanNumeral:
                    return self.nounNoSuffix_S
                else:
                    if item.has_attribute(RootAttribute.CompoundP3sg):
                        return self.nounCompoundRoot_S
                    return self.noun_S

            elif item.primary_pos == PrimaryPos.Adjective:
                return self.adjectiveRoot_ST
            elif item.primary_pos == PrimaryPos.Pronoun:
                if item.secondary_pos == SecondaryPos.PersonalPron:
                    return self.pronPers_S
                elif item.secondary_pos == SecondaryPos.DemonstrativePron:
                    return self.pronDemons_S
                elif item.secondary_pos == SecondaryPos.QuantitivePron:
                    return self.pronQuant_S
                elif item.secondary_pos == SecondaryPos.QuestionPron:
                    return self.pronQues_S
                elif item.secondary_pos == SecondaryPos.ReflexivePron:
                    return self.pronReflex_S
                else:
                    return self.pronQuant_S

            elif item.primary_pos == PrimaryPos.Adverb:
                return self.advRoot_ST
            elif item.primary_pos == PrimaryPos.Conjunction:
                return self.conjRoot_ST
            elif item.primary_pos == PrimaryPos.Question:
                return self.questionRoot_S
            elif item.primary_pos == PrimaryPos.Interjection:
                return self.interjRoot_ST
            elif item.primary_pos == PrimaryPos.Verb:
                return self.verbRoot_S
            elif item.primary_pos == PrimaryPos.Punctuation:
                return self.puncRoot_ST
            elif item.primary_pos == PrimaryPos.Determiner:
                return self.detRoot_ST
            elif item.primary_pos == PrimaryPos.PostPositive:
                return self.postpRoot_ST
            elif item.primary_pos == PrimaryPos.Numeral:
                return self.numeralRoot_ST
            elif item.primary_pos == PrimaryPos.Duplicator:
                return self.dupRoot_ST
            else:
                return self.noun_S


# This class was under morphology/analysis/ but it has a circular import dependency
# with TurkishMorphotactics class and due to the restrictions of Python on circular imports
# we needed to move it here
class StemTransitionsBase:
    def __init__(self, morphotactics: TurkishMorphotactics):
        self.alphabet = TurkishAlphabet.INSTANCE
        self.morphotactics = morphotactics
        self.modifiers = {RootAttribute.Doubling, RootAttribute.LastVowelDrop, RootAttribute.ProgressiveVowelDrop,
                          RootAttribute.InverseHarmony, RootAttribute.Voicing, RootAttribute.CompoundP3sg,
                          RootAttribute.CompoundP3sgRoot}
        self.special_roots = {"içeri_Noun", "içeri_Adj", "dışarı_Adj", "şura_Noun", "bura_Noun", "ora_Noun",
                              "dışarı_Noun", "dışarı_Postp", "yukarı_Noun", "yukarı_Adj", "ileri_Noun", "ben_Pron_Pers",
                              "sen_Pron_Pers", "demek_Verb", "yemek_Verb", "imek_Verb", "birbiri_Pron_Quant",
                              "çoğu_Pron_Quant", "öbürü_Pron_Quant", "birçoğu_Pron_Quant"}

    def generate(self, item: DictionaryItem) -> Tuple[StemTransition, ...]:
        if item.id_ in self.special_roots:
            return self.handle_special_roots(item)
        elif self.has_modifier_attribute(item):
            return self.generate_modified_root_nodes(item)
        else:
            phonetic_attributes: Set[PhoneticAttribute] = self.calculate_attributes(item.pronunciation)
            transition = StemTransition(item.root, item, phonetic_attributes,
                                        self.morphotactics.get_root_state(item, phonetic_attributes))
            return (transition,)

    def has_modifier_attribute(self, item: DictionaryItem) -> bool:
        if self.modifiers & item.attributes:
            return True
        return False

    @staticmethod
    def calculate_attributes(input_: str) -> Set[PhoneticAttribute]:
        return AttributesHelper.get_morphemic_attributes(input_)

    def generate_modified_root_nodes(self, dic_item: DictionaryItem) -> Tuple[StemTransition, ...]:

        modified_seq = dic_item.pronunciation
        original_attrs = self.calculate_attributes(dic_item.pronunciation)
        modified_attrs = deepcopy(original_attrs)
        modified_root_state = None  # MorphemeState
        unmodified_root_state = None  # MorphemeState

        for attribute in dic_item.attributes:
            if attribute == RootAttribute.Voicing:
                last = self.alphabet.last_char(modified_seq)
                voiced = self.alphabet.voice(last)
                if last == voiced:
                    raise Exception("Voicing letter is not proper in: " + dic_item.id_)

                if dic_item.lemma.endswith("nk"):
                    voiced = 'g'

                modified_seq = modified_seq[: -1] + voiced
                try:
                    modified_attrs.remove(PhoneticAttribute.LastLetterVoicelessStop)
                except KeyError as ke:
                    logger.debug("Key error in modified_attrs in Voicing branch: " + str(ke))
                original_attrs.add(PhoneticAttribute.ExpectsConsonant)
                modified_attrs.add(PhoneticAttribute.ExpectsVowel)
                modified_attrs.add(PhoneticAttribute.CannotTerminate)
            elif attribute == RootAttribute.Doubling:
                modified_seq = modified_seq + self.alphabet.last_char(modified_seq)
                original_attrs.add(PhoneticAttribute.ExpectsConsonant)
                modified_attrs.add(PhoneticAttribute.ExpectsVowel)
                modified_attrs.add(PhoneticAttribute.CannotTerminate)

            elif attribute == RootAttribute.LastVowelDrop:
                last_letter = self.alphabet.get_last_letter(modified_seq)
                if last_letter.is_vowel():
                    modified_seq = modified_seq[:-1]
                    modified_attrs.add(PhoneticAttribute.ExpectsConsonant)
                    modified_attrs.add(PhoneticAttribute.CannotTerminate)
                else:
                    modified_seq = modified_seq[: -2] + modified_seq[-1:]
                    if dic_item.primary_pos != PrimaryPos.Verb:
                        original_attrs.add(PhoneticAttribute.ExpectsConsonant)
                    else:
                        unmodified_root_state = self.morphotactics.verbLastVowelDropUnmodRoot_S
                        modified_root_state = self.morphotactics.verbLastVowelDropModRoot_S

                    modified_attrs.add(PhoneticAttribute.ExpectsVowel)
                    modified_attrs.add(PhoneticAttribute.CannotTerminate)

            elif attribute == RootAttribute.InverseHarmony:
                original_attrs.add(PhoneticAttribute.LastVowelFrontal)
                modified_attrs.add(PhoneticAttribute.LastVowelFrontal)
                try:
                    original_attrs.remove(PhoneticAttribute.LastVowelBack)
                except KeyError as ke:
                    logger.debug("Non existent key original_attrs: " + str(ke))
                try:
                    modified_attrs.remove(PhoneticAttribute.LastVowelBack)
                except KeyError as ke:
                    logger.debug("Non existent key modified_attrs: " + str(ke))

            elif attribute == RootAttribute.ProgressiveVowelDrop:
                if len(modified_seq) > 1:
                    modified_seq = modified_seq[:-1]
                    if self.alphabet.contains_vowel(modified_seq):
                        modified_attrs = self.calculate_attributes(modified_seq)

                    modified_attrs.add(PhoneticAttribute.LastLetterDropped)

        if unmodified_root_state is None:
            unmodified_root_state = self.morphotactics.get_root_state(dic_item, original_attrs)

        original: StemTransition = StemTransition(dic_item.root, dic_item, original_attrs, unmodified_root_state)
        if modified_root_state is None:
            modified_root_state = self.morphotactics.get_root_state(dic_item, modified_attrs)

        modified: StemTransition = StemTransition(modified_seq, dic_item, modified_attrs, modified_root_state)
        if original == modified:
            return (original,)
        else:
            return original, modified

    def handle_special_roots(self, item: DictionaryItem) -> Tuple[StemTransition, ...]:
        id_ = item.id_
        original_attrs = self.calculate_attributes(item.pronunciation)
        unmodified_root_state = self.morphotactics.get_root_state(item, original_attrs)

        if id_ == "içeri_Noun" or id_ == "içeri_Adj" or id_ == "dışarı_Adj" or id_ == "dışarı_Noun" or \
                id_ == "dışarı_Postp" or id_ == "yukarı_Noun" or id_ == "ileri_Noun" or id_ == "yukarı_Adj" or \
                id_ == "şura_Noun" or id_ == "bura_Noun" or id_ == "ora_Noun":
            original = StemTransition(item.root, item, original_attrs, unmodified_root_state)
            if item.primary_pos == PrimaryPos.Noun:
                root_for_modified = self.morphotactics.nounLastVowelDropRoot_S
            elif item.primary_pos == PrimaryPos.Adjective:
                root_for_modified = self.morphotactics.adjLastVowelDropRoot_S
            elif item.primary_pos == PrimaryPos.PostPositive:
                root_for_modified = self.morphotactics.adjLastVowelDropRoot_S
            else:
                raise Exception("No root morpheme state found for " + item.id_)

            m = item.root[:-1]
            modified = StemTransition(m, item, self.calculate_attributes(m), root_for_modified)
            modified.phonetic_attributes.add(PhoneticAttribute.ExpectsConsonant)
            modified.phonetic_attributes.add(PhoneticAttribute.CannotTerminate)
            return original, modified
        elif id_ == "ben_Pron_Pers" or id_ == "sen_Pron_Pers":
            original = StemTransition(item.root, item, original_attrs, unmodified_root_state)
            if item.lemma == "ben":
                modified = StemTransition("ban", item, self.calculate_attributes("ban"),
                                          self.morphotactics.pronPers_Mod_S)
            else:
                modified = StemTransition("san", item, self.calculate_attributes("san"),
                                          self.morphotactics.pronPers_Mod_S)
            original.phonetic_attributes.add(PhoneticAttribute.UnModifiedPronoun)
            modified.phonetic_attributes.add(PhoneticAttribute.ModifiedPronoun)
            return original, modified
        elif id_ == "demek_Verb" or id_ == "yemek_Verb":
            original = StemTransition(item.root, item, original_attrs, self.morphotactics.vDeYeRoot_S)

            if item.lemma == "demek":
                modified = StemTransition("di", item, self.calculate_attributes("di"),
                                          self.morphotactics.vDeYeRoot_S)
            else:
                modified = StemTransition("yi", item, self.calculate_attributes("yi"),
                                          self.morphotactics.vDeYeRoot_S)
            return original, modified
        elif id_ == "imek_Verb":
            original = StemTransition(item.root, item, original_attrs, self.morphotactics.imekRoot_S)
            return (original,)
        elif id_ == "birbiri_Pron_Quant" or id_ == "çoğu_Pron_Quant" or id_ == "öbürü_Pron_Quant" or \
                id_ == "birçoğu_Pron_Quant":
            original = StemTransition(item.root, item, original_attrs, self.morphotactics.pronQuant_S)

            if item.lemma == "birbiri":
                modified = StemTransition("birbir", item, self.calculate_attributes("birbir"),
                                          self.morphotactics.pronQuantModified_S)
            elif item.lemma == "çoğu":
                modified = StemTransition("çok", item, self.calculate_attributes("çok"),
                                          self.morphotactics.pronQuantModified_S)
            elif item.lemma == "öbürü":
                modified = StemTransition("öbür", item, self.calculate_attributes("öbür"),
                                          self.morphotactics.pronQuantModified_S)
            else:
                modified = StemTransition("birçok", item, self.calculate_attributes("birçok"),
                                          self.morphotactics.pronQuantModified_S)
            original.phonetic_attributes.add(PhoneticAttribute.UnModifiedPronoun)
            modified.phonetic_attributes.add(PhoneticAttribute.ModifiedPronoun)
            return original, modified
        else:
            raise Exception("Lexicon Item with special stem change cannot be handled:" + item.id_)


# This class was under morphology/analysis/ but it has a circular import dependency
# with TurkishMorphotactics class and due to the restrictions of Python on circular imports
# we needed to move it here
class StemTransitionsMapBased(StemTransitionsBase):

    def __init__(self, lexicon: RootLexicon, morphotactics: TurkishMorphotactics):
        super().__init__(morphotactics)
        self.lexicon = lexicon
        self.morphotactics = morphotactics
        self.multi_stems: Dict[str, List[StemTransition]] = dict()
        self.single_stems: Dict[str, StemTransition] = dict()
        self.different_stem_items: Dict[DictionaryItem, List[StemTransition]] = dict()

        self.ascii_keys = None  # MultiMap <String, String>

        self.lock = ReadWriteLock()

        for item in lexicon:
            self.add_dictionary_item(item)

    def add_dictionary_item(self, item: DictionaryItem):
        self.lock.acquire_write()

        try:
            transitions: Tuple[StemTransition] = self.generate(item)
            for transition in transitions:
                self.add_stem_transition(transition)

            if len(transitions) > 1 or (len(transitions) == 1 and transitions[0].surface != item.root):
                if item in self.different_stem_items.keys():
                    self.different_stem_items[item].extend(transitions)
                else:
                    self.different_stem_items[item] = list(transitions)
        except ValueError:
            logger.debug('Cannot generate stem transition for %s: '.format(item.id_))
        finally:
            self.lock.release_write()

    def remove_dictionary_item(self, item):
        self.lock.acquire_write()

        try:
            transitions: Tuple[StemTransition] = self.generate(item)
            for transition in transitions:
                self.remove_stem_node(transition)

            if item in self.different_stem_items.keys():
                self.different_stem_items.pop(item)
        except ValueError as e:
            logger.warning("Cannot remove" + str(e))
        finally:
            self.lock.release_write()

    def remove_stem_node(self, stem_transition: StemTransition):
        surface_form = stem_transition.surface
        if surface_form in self.multi_stems.keys():
            self.multi_stems[surface_form].remove(stem_transition)
        elif surface_form in self.single_stems.keys() and self.single_stems.get(
                surface_form).item == stem_transition.item:
            self.single_stems.pop(surface_form)

        # BURADA HATA OLABILIR DIKKAT ET
        # THERE WAS A NEGATION THAT NEGATES WHOLE IF STATEMENT BELOW, CHECK RESULTS
        if not (stem_transition.item in self.different_stem_items.keys() and stem_transition in
                self.different_stem_items[stem_transition.item]):
            try:
                self.different_stem_items[stem_transition.item].remove(stem_transition)
            except KeyError:
                logger.debug(f"Hata: {str(stem_transition.item)}")

    def add_stem_transition(self, stem_transition: StemTransition):
        surface_form = stem_transition.surface
        if surface_form in self.multi_stems.keys():
            self.multi_stems[surface_form].append(stem_transition)
        elif surface_form in self.single_stems.keys():
            self.multi_stems[surface_form] = [self.single_stems[surface_form], stem_transition]
            self.single_stems.pop(surface_form)
        else:
            self.single_stems[surface_form] = stem_transition

    def get_transitions(self, stem: str = None) -> Union[Set[StemTransition], Tuple[StemTransition, ...]]:
        if not stem:
            result = set(self.single_stems.values())
            for value in self.multi_stems.values():
                result |= set(value)
            return result
        else:
            self.lock.acquire_read()
            try:
                if stem in self.single_stems.keys():
                    return (self.single_stems[stem],)

                if stem in self.multi_stems.keys():
                    return tuple(self.multi_stems[stem])

            finally:
                self.lock.release_read()

            return ()

    def get_transitions_for_item(self, item: DictionaryItem) -> Tuple[StemTransition]:
        self.lock.acquire_read()
        try:
            if item in self.different_stem_items.keys():
                return tuple(self.different_stem_items[item])
            else:
                transitions: Tuple[StemTransition] = self.get_transitions(item.root)
                return tuple(s for s in transitions if s.item == item)
        finally:
            self.lock.release_read()

    def get_transitions_ascii_tolerant(self, stem: str) -> Set[StemTransition]:
        self.lock.acquire_read()
        try:
            result: Set[StemTransition] = set()
            if stem in self.single_stems.keys():
                result.add(self.single_stems[stem])
            elif stem in self.multi_stems.keys():
                result |= set(self.multi_stems[stem])

            ascii_stems: Set[str] = set(self.ascii_keys.get(TurkishAlphabet.INSTANCE.to_ascii(stem), []))
            for st in ascii_stems:
                if st in self.single_stems.keys():
                    result.add(self.single_stems[st])
                elif st in self.multi_stems.keys():
                    result |= set(self.multi_stems[st])
            return result
        finally:
            self.lock.release_read()

    def get_prefix_matches(self, inp: str, ascii_tolerant: bool) -> Tuple[StemTransition]:
        if self.ascii_keys is None and ascii_tolerant:
            self.generate_ascii_tolerant_map()

        self.lock.acquire_read()

        try:
            matches: List[StemTransition] = []

            for i in range(1, len(inp) + 1):
                stem = inp[0:i]
                if ascii_tolerant:
                    matches.extend(self.get_transitions_ascii_tolerant(stem))
                else:
                    matches.extend(self.get_transitions(stem=stem))

            return tuple(matches)
        finally:
            self.lock.release_read()

    def generate_ascii_tolerant_map(self):
        self.lock.acquire_write()
        self.ascii_keys: Dict[str, List[str]] = {}

        try:
            for s in self.single_stems.keys():
                ascii_ = TurkishAlphabet.INSTANCE.to_ascii(s)
                if TurkishAlphabet.INSTANCE.contains_ascii_related(s):
                    if ascii_ not in self.ascii_keys.keys():
                        self.ascii_keys[ascii_] = [s]
                    else:
                        self.ascii_keys[ascii_].append(s)

            for sts in self.multi_stems.values():
                for st in sts:
                    s = st.surface
                    ascii_ = TurkishAlphabet.INSTANCE.to_ascii(s)
                    if TurkishAlphabet.INSTANCE.contains_ascii_related(s):
                        if ascii_ in self.ascii_keys.keys():
                            self.ascii_keys[ascii_].append(s)
                        else:
                            self.ascii_keys[ascii_] = [s]
        finally:
            self.lock.release_write()
