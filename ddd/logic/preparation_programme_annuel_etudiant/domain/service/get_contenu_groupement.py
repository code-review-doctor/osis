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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List, Optional

import attr

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO, \
    GroupementContenantDTO, \
    ElementContenuDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface


class GetContenuGroupement(interface.DomainService):
    @classmethod
    def get_contenu_groupement(
            cls,
            cmd: 'GetContenuGroupementCommand',
            repo: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator',
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ) -> 'GroupementContenantDTO':

        contenu_catalogue = catalogue_formations_translator.get_contenu_groupement(cmd=cmd)

        groupement_id = GroupIdentity(code=cmd.code, year=cmd.annee)

        try:
            groupement_ajuste = repo.search(code_programme=cmd.code_formation, groupement_id=groupement_id)[0]
            entity_id_unites_enseignement = [
                unite_enseignement.unite_enseignement_identity
                for unite_enseignement in groupement_ajuste.unites_enseignement_ajoutees
            ]
            unite_enseignements_ajoutes_dto = catalogue_unites_enseignement_translator.search(
                entity_ids=entity_id_unites_enseignement
            )
        except IndexError:
            groupement_ajuste = None
            unite_enseignements_ajoutes_dto = []

        return cls.__ajuster_contenu_groupement_dto(
            contenu_catalogue,
            groupement_ajuste,
            unite_enseignements_ajoutes_dto
        )

    @classmethod
    def __ajuster_contenu_groupement_dto(
            cls,
            contenu_groupement: 'GroupementContenantDTO',
            groupement_ajuste: Optional['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> GroupementContenantDTO:
        if not groupement_ajuste:
            return contenu_groupement

        return attr.evolve(
            contenu_groupement,
            elements_contenus=contenu_groupement.elements_contenus + [
                cls.__build_unite_enseignement_ajoute_dto(unites_enseignement_ajoutee, unite_enseignement_ajoutes_dto)
                for unites_enseignement_ajoutee in groupement_ajuste.unites_enseignement_ajoutees
            ]
        )

    @classmethod
    def __build_unite_enseignement_ajoute_dto(
            cls,
            unite_enseignement_ajoute: 'UniteEnseignementAjoutee',
            unite_enseignement_dtos: List['UniteEnseignementCatalogueDTO']
    ) -> 'ElementContenuDTO':
        unite_enseignement_dto_correspondant = next(
            dto for dto in unite_enseignement_dtos if dto.code == unite_enseignement_ajoute.code
        )
        return ElementContenuDTO(
            code=unite_enseignement_ajoute.code,
            obligatoire=unite_enseignement_dto_correspondant.obligatoire,
            bloc="1",
            session_derogation=unite_enseignement_dto_correspondant.session_derogation,
            credits=str(unite_enseignement_dto_correspondant.credits_relatifs),
            intitule_complet=unite_enseignement_dto_correspondant.intitule_complet,
            quadrimestre_texte=unite_enseignement_dto_correspondant.quadrimestre_texte,
            volumes=""
        )
