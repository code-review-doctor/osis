from ddd.logic.preparation_programme_annuel_etudiant.domain.model.programme_inscription_cours import \
    ProgrammeInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement import UniteEnseignementIdentity
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_programme_inscription_cours import \
    IProgrammeInscriptionCoursRepository
from osis_common.ddd import interface


class DeplacerUEAjoutee(interface.DomainService):
    @classmethod
    def deplacer_vers_le_bas(
        cls,
        programme_inscription_cours: ProgrammeInscriptionCours,
        contenu_groupement: ContenuGroupementDTO,
        unite_enseignement_identity: UniteEnseignementIdentity,
        repository: IProgrammeInscriptionCoursRepository
    ) -> None:

        # TODO: traiter l'actualisation des autres UE ajoutées du groupement quand on ajoute une UE
        #  et déterminer le code de l'UE ou du groupement qui précède l'UE déplacée
        #  (modifier a_la_suite_de pour toutes les UE et déterminer a_la_suite_de pour l'UE déplacée)

        programme_inscription_cours.deplacer_unite_enseignement_ajoutee(
            unite_enseignement_identity=unite_enseignement_identity,
            # a_la_suite_de=a_la_suite_de
        )
        repository.save(programme_inscription_cours)

    @classmethod
    def deplacer_vers_le_haut(
        cls,
        programme_inscription_cours: ProgrammeInscriptionCours,
        contenu_groupement: ContenuGroupementDTO,
        unite_enseignement_identity: UniteEnseignementIdentity,
        repository: IProgrammeInscriptionCoursRepository
    ) -> None:

        # TODO: traiter l'actualisation des autres UE ajoutées du groupement quand on ajoute une UE
        #  et déterminer le code de l'UE ou du groupement qui précède l'UE déplacée
        #  (modifier a_la_suite_de pour toutes les UE et déterminer a_la_suite_de pour l'UE déplacée)

        programme_inscription_cours.deplacer_unite_enseignement_ajoutee(
            unite_enseignement_identity=unite_enseignement_identity,
            # a_la_suite_de=a_la_suite_de
        )
        repository.save(programme_inscription_cours)