from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_doctorat import IDoctoratTranslator
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_secteur_ucl import ISecteurUclTranslator
from ddd.logic.admission.preparation.projet_doctoral.dtos import PropositionDTO
from ddd.logic.admission.preparation.projet_doctoral.repository.i_proposition import IPropositionRepository
from osis_common.ddd import interface


class PropositionDto(interface.DomainService):
    @classmethod
    def get(
            cls,
            uuid_proposition: str,
            repository: 'IPropositionRepository',
            doctorat_translator: 'IDoctoratTranslator',
            secteur_ucl_translator: 'ISecteurUclTranslator',
    ) -> 'PropositionDTO':
        raise NotImplementedError
