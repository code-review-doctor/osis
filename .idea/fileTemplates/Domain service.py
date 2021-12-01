#set( $Service = ${StringUtils.removeAndHump($NAME)} )
from osis_common.ddd import interface


class $Service(interface.DomainService):
    @classmethod
    def methode(cls) -> None:
        pass
