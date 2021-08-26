#set( $Aggregate = ${StringUtils.removeAndHump($NAME)} )

class I${Aggregate}Translator(interface.DomainService):
    @classmethod
    @abstractmethod
    def get(cls, sigle: str, annee: int) -> $Aggregate:
        pass
