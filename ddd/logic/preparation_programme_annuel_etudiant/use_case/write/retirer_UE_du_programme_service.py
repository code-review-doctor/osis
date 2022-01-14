from ddd.logic.preparation_programme_annuel_etudiant.commands import RetirerUEDuProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.builder.programme_inscription_cours_identity_builder import \
    ProgrammeInscriptionCoursIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.programme_inscription_cours import \
    ProgrammeInscriptionCoursIdentity
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_programme_inscription_cours import \
    IProgrammeInscriptionCoursRepository


def retirer_UE_du_programme(
        cmd: 'RetirerUEDuProgrammeCommand',
        repository: 'IProgrammeInscriptionCoursRepository',
) -> 'ProgrammeInscriptionCoursIdentity':
    # GIVEN
    programme_inscription_cours_identity = ProgrammeInscriptionCoursIdentityBuilder.build_from_command(cmd)
    programme_inscription_cours = repository.get(
        entity_id=programme_inscription_cours_identity
    )

    # WHEN
    for cmd_ue in cmd.unites_enseignements:
        programme_inscription_cours.retirer_unite_enseignement(
            unite_enseignement=cmd_ue.code,
            a_retirer_de=cmd.a_retirer_de
        )

    # THEN
    repository.save(programme_inscription_cours)
    return programme_inscription_cours.entity_id
