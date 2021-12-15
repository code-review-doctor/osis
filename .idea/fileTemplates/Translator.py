#set( $Aggregate = ${StringUtils.removeAndHump($NAME)} )
from osis_common.ddd import interface


class I${Aggregate}Translator(interface.DomainService):
    @classmethod
    @abstractmethod
    def get(cls, param: int) -> $Aggregate:
        pass
