from typing import List

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.validator.exceptions import \
    AucunContenuAReinitialiserException
from osis_common.ddd import interface


class CanReinitialiserProgramme(interface.DomainService):
    @classmethod
    def verifier(
            cls,
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
    ) -> None:
        if not groupements_ajustes:
            raise AucunContenuAReinitialiserException()
