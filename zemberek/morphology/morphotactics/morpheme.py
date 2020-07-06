from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zemberek.core.turkish import PrimaryPos


class Morpheme:

    UNKNOWN: 'Morpheme'

    def __init__(self, builder: 'Morpheme.Builder'):
        self.name = builder.name
        self.id_ = builder.id_
        self.informal = builder.informal
        self.derivational_ = builder.derivational
        self.pos = builder.pos
        self.mapped_morpheme = builder.mapped_morpheme

    def __str__(self):
        return self.name + ':' + self.id_

    def __hash__(self):
        return hash(self.id_)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Morpheme):
            return self.id_ == other.id_
        else:
            return False

    @staticmethod
    def instance(name: str, id_: str, pos: PrimaryPos = None) -> 'Morpheme':
        return Morpheme.Builder(name, id_, pos=pos).build()

    @staticmethod
    def builder(name: str, id_: str) -> 'Morpheme.Builder':
        return Morpheme.Builder(name, id_)

    @staticmethod
    def derivational(name: str, id_: str) -> 'Morpheme':
        return Morpheme.Builder(name, id_, derivational=True).build()

    class Builder:

        def __init__(self, name: str, id_: str, derivational: bool = False, informal: bool = False,
                     pos: PrimaryPos = None, mapped_morpheme: 'Morpheme' = None):
            self.name = name
            self.id_ = id_
            self.derivational = derivational
            self.informal = informal
            self.pos = pos
            self.mapped_morpheme = mapped_morpheme

        def informal_(self) -> 'Morpheme.Builder':
            self.informal = True
            return self

        def mapped_morpheme_(self, morpheme: 'Morpheme') -> 'Morpheme.Builder':
            self.mapped_morpheme = morpheme
            return self

        def build(self) -> 'Morpheme':
            return Morpheme(self)


Morpheme.UNKNOWN = Morpheme.Builder(name="Unknown", id_="Unknown").build()
