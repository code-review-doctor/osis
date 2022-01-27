##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeInscriptionCoursDTO, \
    GroupementInscriptionCoursDTO, UniteEnseignementProgrammeDTO, ContenuGroupementCatalogueDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from osis_common.ddd import interface
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentityBuilder


class GetProgrammeInscriptionCours(interface.DomainService):
    @classmethod
    def get_programme_inscription_cours(
            cls,
            cmd: 'GetProgrammeInscriptionCoursCommand',
            groupement_ajuste_repository: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator'
    ):
        formation = catalogue_formations_translator.get_formation(
            sigle=cmd.sigle_formation,
            annee=cmd.annee_formation,
            version=cmd.version_formation,
            transition_name=cmd.transition_formation
        )
        program_tree_version_identity = ProgramTreeVersionIdentityBuilder().build(
            year=cmd.annee_formation,
            offer_acronym=cmd.sigle_formation,
            version_name=cmd.version_formation,
            transition_name=cmd.transition_formation
        )
        groupements_ajustes = groupement_ajuste_repository.get_dtos(program_tree_version_identity)
        groupements = cls.__build_groupement_inscription_cours_dtos([formation.racine])
        return ProgrammeInscriptionCoursDTO(
            uuid='uuid-1234',
            code=program_tree_version_identity.offer_acronym,
            annee=program_tree_version_identity.year,
            version=program_tree_version_identity.version_name,
            transition=program_tree_version_identity.transition_name,
            intitule_complet_formation=formation.intitule_complet,
            sous_programme=groupements,
        )

    @classmethod
    def __build_groupement_inscription_cours_dtos(
            cls,
            groupements_contenus: List[ContenuGroupementCatalogueDTO]
    ) -> List[GroupementInscriptionCoursDTO]:
        return [
            GroupementInscriptionCoursDTO(
                intitule_complet=groupement.groupement_contenant.intitule_complet,
                obligatoire=groupement.groupement_contenant.obligatoire,
                code=groupement.groupement_contenant.code,
                unites_enseignements=[
                    UniteEnseignementProgrammeDTO(
                        code=unite_enseignement.code,
                        intitule=unite_enseignement.intitule_complet,
                        obligatoire=unite_enseignement.obligatoire,
                        bloc=unite_enseignement.bloc,
                    ) for unite_enseignement in groupement.unites_enseignement_contenues
                ],
                sous_programme=cls.__build_groupement_inscription_cours_dtos(groupement.groupements_contenus),
            ) for groupement in groupements_contenus
        ]
