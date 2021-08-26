#set( $Service = ${StringUtils.removeAndHump($NAME)} )
from typing import Optional, List

class $Service(interface.DomainService):
    @classmethod
    def methode(cls) -> None:
        pass