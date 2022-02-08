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
import itertools
from typing import List, Union

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetProgrammeInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeInscriptionCoursDTO, \
    GroupementInscriptionCoursDTO, UniteEnseignementProgrammeDTO, ContenuGroupementCatalogueDTO, \
    UniteEnseignementAjouteeDTO, UniteEnseignementCatalogueDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface


class GetProgrammeInscriptionCours(interface.DomainService):
    @classmethod
    def get_programme_inscription_cours(
            cls,
            cmd: 'GetProgrammeInscriptionCoursCommand',
            groupement_ajuste_repository: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator',
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ):
        formation = catalogue_formations_translator.get_formation(
            code_programme=cmd.code_programme,
            annee=cmd.annee,
        )

        groupements_ajustes = groupement_ajuste_repository.search(
            programme_id=GroupIdentity(code=cmd.code_programme, year=cmd.annee)
        )
        unite_enseignements_ajoutes_dto = cls.rechercher_unites_enseignement_ajoutees_catalogue_dto(
            groupements_ajustes,
            catalogue_unites_enseignement_translator
        )
        return ProgrammeInscriptionCoursDTO(
            uuid='uuid-1234',
            code=formation.racine.groupement_contenant.code,
            annee=cmd.annee,
            sigle=formation.sigle,
            version=formation.version,
            transition_name=formation.transition_name,
            intitule_complet_formation=formation.intitule_formation,
            racine=cls.__build_contenu(
                [formation.racine],
                groupements_ajustes,
                unite_enseignements_ajoutes_dto
            )[0],
        )

    @classmethod
    def rechercher_unites_enseignement_ajoutees_catalogue_dto(
            cls,
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ) -> List['UniteEnseignementCatalogueDTO']:
        unites_enseignement_ajoutees = itertools.chain.from_iterable(
            [
                groupement.unites_enseignement_ajoutees
                for groupement in groupements_ajustes
            ]
        )
        entity_id_unites_enseignement = [
            unite_enseignement.unite_enseignement_identity
            for unite_enseignement in unites_enseignement_ajoutees
        ]

        return catalogue_unites_enseignement_translator.search(
            entity_ids=entity_id_unites_enseignement
        )

    @classmethod
    def __build_contenu(
            cls,
            contenu_ordonne_catalogue: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']],
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> List[Union['UniteEnseignementProgrammeDTO', 'GroupementInscriptionCoursDTO']]:
        contenu = []
        for element in contenu_ordonne_catalogue:
            if isinstance(element, UniteEnseignementCatalogueDTO):
                contenu.append(
                    UniteEnseignementProgrammeDTO(
                        code=element.code,
                        intitule=element.intitule_complet,
                        obligatoire=element.obligatoire,
                        bloc=element.bloc,
                    )
                )
            elif isinstance(element, ContenuGroupementCatalogueDTO):
                contenu.append(
                    GroupementInscriptionCoursDTO(
                        intitule_complet=element.groupement_contenant.intitule_complet,
                        obligatoire=element.groupement_contenant.obligatoire,
                        code=element.groupement_contenant.code,
                        unites_enseignement_ajoutees=cls.__build_unite_enseignement_ajoute_dtos(
                            element,
                            groupements_ajustes,
                            unite_enseignement_ajoutes_dto
                        ),
                        contenu=cls.__build_contenu(
                            element.contenu_ordonne_catalogue,
                            groupements_ajustes,
                            unite_enseignement_ajoutes_dto
                        )
                    )
                )
        return contenu

    @classmethod
    def __build_unite_enseignement_ajoute_dtos(
            cls,
            groupement: 'ContenuGroupementCatalogueDTO',
            groupements_ajustes: List['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> List['UniteEnseignementAjouteeDTO']:
        groupement_ajuste_correspondant = next(
            (
                groupement_ajuste
                for groupement_ajuste in groupements_ajustes
                if groupement_ajuste.groupement_id.code == groupement.groupement_contenant.code
            ),
            None
        )
        unites_enseignemnts_ajoutes = groupement_ajuste_correspondant.unites_enseignement_ajoutees if \
            groupement_ajuste_correspondant else []

        return [
            cls.__build_unite_enseignement_ajoute_dto(unite_enseignement, unite_enseignement_ajoutes_dto)
            for unite_enseignement in unites_enseignemnts_ajoutes
        ]

    @classmethod
    def __build_unite_enseignement_ajoute_dto(
            cls,
            unite_enseignement_ajoute: 'UniteEnseignementAjoutee',
            unite_enseignement_dtos: List['UniteEnseignementCatalogueDTO']
    ) -> 'UniteEnseignementAjouteeDTO':
        unite_enseignement_dto_correspondant = next(
            dto for dto in unite_enseignement_dtos if dto.code == unite_enseignement_ajoute.code
        )
        return UniteEnseignementAjouteeDTO(
            code=unite_enseignement_ajoute.code,
            intitule=unite_enseignement_dto_correspondant.intitule_complet,
            obligatoire=unite_enseignement_dto_correspondant.obligatoire,
            bloc=1,
            a_la_suite_de="",
        )
