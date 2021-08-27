from abc import abstractmethod

from osis_common.ddd import interface


class ISecteurUclTranslator(interface.DomainService):
    @classmethod
    @abstractmethod
    def get(cls, sigle_entite: str) -> 'EntiteUclDTO':  # TODO :: réutiliser EntiteUclDTO from shared kernel
        pass
