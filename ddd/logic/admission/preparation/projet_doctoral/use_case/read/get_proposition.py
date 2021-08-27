from ddd.logic.admission.preparation.projet_doctoral.commands import GetPropositionCommand
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_doctorat import IDoctoratTranslator
from ddd.logic.admission.preparation.projet_doctoral.domain.service.i_secteur_ucl import ISecteurUclTranslator
from ddd.logic.admission.preparation.projet_doctoral.domain.service.proposition_dto import PropositionDto
from ddd.logic.admission.preparation.projet_doctoral.dtos import PropositionDTO
from ddd.logic.admission.preparation.projet_doctoral.repository.i_proposition import IPropositionRepository


def get_proposition(
        cmd: 'GetPropositionCommand',
        proposition_repository: 'IPropositionRepository',
        doctorat_translator: 'IDoctoratTranslator',
        secteur_ucl_translator: 'ISecteurUclTranslator',
) -> 'PropositionDTO':
    return PropositionDto().get(
        uuid_proposition=cmd.uuid_proposition,
        repository=proposition_repository,
        doctorat_translator=doctorat_translator,
        secteur_ucl_translator=secteur_ucl_translator,

    )
