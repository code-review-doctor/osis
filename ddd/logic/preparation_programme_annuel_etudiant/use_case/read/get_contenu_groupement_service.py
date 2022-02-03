from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand, \
    GetContenuGroupementAjusteCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.get_contenu_groupement import GetContenuGroupement
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository


def get_contenu_groupement_service(
        cmd: 'GetContenuGroupementAjusteCommand',
        repo: 'IGroupementAjusteInscriptionCoursRepository',
        catalogue_formations_translator: 'ICatalogueFormationsTranslator',
        catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
) -> 'ContenuGroupementDTO':
    return GetContenuGroupement.get_contenu_groupement(
        cmd,
        repo,
        catalogue_formations_translator,
        catalogue_unites_enseignement_translator
    )
