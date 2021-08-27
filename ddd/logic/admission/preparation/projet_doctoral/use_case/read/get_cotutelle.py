from ddd.logic.admission.preparation.projet_doctoral.commands import GetCotutelleCommand
from ddd.logic.admission.preparation.projet_doctoral.dtos import CotutelleDTO
from ddd.logic.admission.preparation.projet_doctoral.repository.i_groupe_de_supervision import \
    IGroupeDeSupervisionRepository


def get_cotutelle(
        cmd: 'GetCotutelleCommand',
        repository: 'IGroupeDeSupervisionRepository',
) -> 'CotutelleDTO':
    # GIVEN
    return repository.get_cotutelle_dto(cmd.uuid_proposition)
