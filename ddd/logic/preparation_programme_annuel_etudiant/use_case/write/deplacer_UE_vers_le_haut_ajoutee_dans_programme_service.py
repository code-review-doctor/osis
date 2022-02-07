##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from ddd.logic.preparation_programme_annuel_etudiant.commands import DeplacerVersLeHautUEAjouteeDansProgrammeCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.builder.groupement_ajuste_inscription_cours_identity_builder import \
    GroupementAjusteInscriptionCoursIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.domain.builder.unite_enseignement_identity_builder import \
    UniteEnseignementIdentityBuilder
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.deplacer_UE_ajoutee import DeplacerUEAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_formations import \
    CatalogueFormationsTranslator


def deplacer_vers_le_haut_UE_ajoutee_dans_programme(
        cmd: 'DeplacerVersLeHautUEAjouteeDansProgrammeCommand',
        repository: 'IGroupementAjusteInscriptionCoursRepository',
        translator: 'CatalogueFormationsTranslator',
) -> 'IdentiteGroupementAjusteInscriptionCours':
    # GIVEN
    unite_enseignement_identity = UniteEnseignementIdentityBuilder.build_from_command(cmd.unite_enseignement)

    identite_groupement_ajuste = GroupementAjusteInscriptionCoursIdentityBuilder.build_from_command(cmd)
    groupement_ajuste = repository.get(
        entity_id=identite_groupement_ajuste
    )

    contenu_groupement = translator.get_contenu_groupement(
        sigle_formation=cmd.sigle_formation,
        version_formation=cmd.version_formation,
        annee=cmd.annee_formation,
        code_groupement=cmd.ajoutee_dans,
    )

    # WHEN
    DeplacerUEAjoutee.deplacer_vers_le_haut(
        groupement_ajuste_inscr_cours=groupement_ajuste,
        contenu_groupement=contenu_groupement,
        unite_enseignement_identity=unite_enseignement_identity,
        repository=repository
    )

    # THEN
    return groupement_ajuste.entity_id
