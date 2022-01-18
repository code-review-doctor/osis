from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjouteeIdentity
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_programme_inscription_cours import \
    IProgrammeInscriptionCoursRepository
from osis_common.ddd import interface


class DeplacerUEAjoutee(interface.DomainService):
    @classmethod
    def deplacer_vers_le_bas(
        cls,
        groupement_ajuste_inscr_cours: GroupementAjusteInscriptionCours,
        contenu_groupement: ContenuGroupementDTO,
        unite_enseignement_identity: UniteEnseignementAjouteeIdentity,
        repository: IProgrammeInscriptionCoursRepository
    ) -> None:

        # TODO: traiter l'actualisation des autres UE ajoutées du groupement quand on ajoute une UE
        #  et déterminer le code de l'UE ou du groupement qui précède l'UE déplacée
        #  (modifier a_la_suite_de pour toutes les UE et déterminer a_la_suite_de pour l'UE déplacée)

        groupement_ajuste_inscr_cours.deplacer_unite_enseignement_ajoutee(
            unite_enseignement_identity=unite_enseignement_identity,
            # a_la_suite_de=a_la_suite_de
        )
        repository.save(groupement_ajuste_inscr_cours)  # TODO :: pq pas .save() dans le use case et pq DomainService ?

    @classmethod
    def deplacer_vers_le_haut(
        cls,
        groupement_ajuste_inscr_cours: 'GroupementAjusteInscriptionCours',
        contenu_groupement: ContenuGroupementDTO,
        unite_enseignement_identity: UniteEnseignementAjouteeIdentity,
        repository: IProgrammeInscriptionCoursRepository
    ) -> None:

        # TODO: traiter l'actualisation des autres UE ajoutées du groupement quand on ajoute une UE
        #  et déterminer le code de l'UE ou du groupement qui précède l'UE déplacée
        #  (modifier a_la_suite_de pour toutes les UE et déterminer a_la_suite_de pour l'UE déplacée)

        groupement_ajuste_inscr_cours.deplacer_unite_enseignement_ajoutee(
            unite_enseignement_identity=unite_enseignement_identity,
            # a_la_suite_de=a_la_suite_de
        )
        repository.save(groupement_ajuste_inscr_cours)  # TODO :: pq pas .save() dans le use case et pq DomainService ?
