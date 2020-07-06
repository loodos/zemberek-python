from abc import ABC


class MorphemeTransition(ABC):

    def __init__(self):
        self.from_ = None
        self.to = None
        self.condition = None
        self.condition_count = None

    def has_surface_form(self):
        raise NotImplementedError

    def get_copy(self):
        raise NotImplementedError()


