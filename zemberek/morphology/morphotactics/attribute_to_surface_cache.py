from threading import Lock
from typing import Dict, Set, Union

from zemberek.core.turkish.phonetic_attribute import PhoneticAttribute


class AttributeToSurfaceCache:

    def __init__(self):
        self.attribute_map: Dict[int, str] = {}
        self.lock = Lock()

    def add_surface(self, attributes: Set[PhoneticAttribute], surface: str):
        """
        Method changed. Instead of original, this method uses hash value of concatenated short form of phonetic
        attributes as key
        :param attributes:
        :param surface:
        :return:
        """
        key_string = ""
        for attribute in attributes:
            key_string += attribute.get_string_form()
        with self.lock:
            self.attribute_map[hash(key_string)] = surface

    def get_surface(self, attributes: Set[PhoneticAttribute]) -> Union[str, None]:
        """
        Method changed. Instead of original, this method uses hash value of concatenated short form of phonetic
        attributes as key
        :param attributes:
        :return:
        """
        key_string = ""
        for attribute in attributes:
            key_string += attribute.get_string_form()
        return self.attribute_map.get(hash(key_string))
