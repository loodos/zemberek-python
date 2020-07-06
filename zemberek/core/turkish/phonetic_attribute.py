from enum import Enum


class PhoneticAttribute(Enum):

    LastLetterVowel = "LLV"
    LastLetterConsonant = "LLC"
    LastVowelFrontal = "LVF"
    LastVowelBack = "LVB"
    LastVowelRounded = "LVR"
    LastVowelUnrounded = "LVuR"
    LastLetterVoiceless = "LLVless"
    LastLetterVoiced = "LLVo"
    LastLetterVoicelessStop = "LLVlessStop"
    FirstLetterVowel = "FLV"
    FirstLetterConsonant = "FLC"
    HasNoVowel = "NoVow"
    ExpectsVowel = "EV"
    ExpectsConsonant = "EC"
    ModifiedPronoun = "MP"
    UnModifiedPronoun = "UMP"
    LastLetterDropped = "LWD"
    CannotTerminate = "CNT"

    def __init__(self, short_form: str):
        self.short_form = short_form

    def get_string_form(self) -> str:
        """
        returns the value of related member
        :return: short form
        """
        return self.short_form
