from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_formations import \
    CatalogueFormationsTranslator


def get_contenu_groupement_service(
        cmd: 'GetContenuGroupementCommand',
        translator: 'CatalogueFormationsTranslator',
) -> 'ContenuGroupementDTO':
    return translator.get_contenu_groupement(
        sigle_formation=cmd.sigle_formation,
        version_formation=cmd.version_formation,
        annee=cmd.annee,
        code_groupement=cmd.code,
    )
