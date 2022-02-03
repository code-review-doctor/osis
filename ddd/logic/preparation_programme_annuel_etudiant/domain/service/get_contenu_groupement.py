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
from typing import List, Union, Optional

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand, \
    GetContenuGroupementAjusteCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_unites_enseignement import \
    ICatalogueUnitesEnseignementTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO, GroupementDTO, \
    UniteEnseignementDTO, UniteEnseignementCatalogueDTO, ContenuGroupementCatalogueDTO
from ddd.logic.preparation_programme_annuel_etudiant.repository.i_groupement_ajuste_inscription_cours import \
    IGroupementAjusteInscriptionCoursRepository
from education_group.ddd.domain.group import GroupIdentity
from osis_common.ddd import interface


class GetContenuGroupement(interface.DomainService):
    @classmethod
    def get_contenu_groupement(
            cls,
            cmd: 'GetContenuGroupementAjusteCommand',
            repo: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator',
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ) -> 'ContenuGroupementDTO':

        contenu_catalogue = catalogue_formations_translator.get_contenu_groupement(
            annee=cmd.annee,
            code_groupement=cmd.code_groupement,
            code_programme=cmd.code_programme
        )

        groupement_id = GroupIdentity(code=cmd.code_groupement, year=cmd.annee)

        try:
            groupement_ajuste = repo.search(code_programme=cmd.code_programme, groupement_id=groupement_id)[0]
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

        return ContenuGroupementDTO(
            groupement_contenant=GroupementDTO(
                intitule=contenu_catalogue.groupement_contenant.intitule,
                intitule_complet=contenu_catalogue.groupement_contenant.intitule_complet,
                obligatoire=contenu_catalogue.groupement_contenant.obligatoire,
                chemin_acces=""
            ),
            contenu=cls.__ajuster_contenu_groupement_dto(
                contenu_catalogue.contenu_ordonne_catalogue,
                groupement_ajuste,
                unite_enseignements_ajoutes_dto
            )
        )

    @classmethod
    def __ajuster_contenu_groupement_dto(
            cls,
            contenu_groupement: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']],
            groupement_ajuste: Optional['GroupementAjusteInscriptionCours'],
            unite_enseignement_ajoutes_dto: List['UniteEnseignementCatalogueDTO']
    ) -> List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']]:
        contenu_ajuste = cls.__convert_contenu(contenu_groupement)

        if not groupement_ajuste:
            return contenu_ajuste

        return contenu_ajuste + [
            cls.__build_unite_enseignement_ajoute_dto(unites_enseignement_ajoutee, unite_enseignement_ajoutes_dto)
            for unites_enseignement_ajoutee in groupement_ajuste.unites_enseignement_ajoutees
        ]

    @classmethod
    def __convert_contenu(
            cls,
            contenu: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']]
            ) -> List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']]:
        result = []
        for element in contenu:
            if isinstance(element, ContenuGroupementCatalogueDTO):
                result.append(
                    ContenuGroupementDTO(
                        groupement_contenant=GroupementDTO(
                            intitule=element.groupement_contenant.intitule,
                            intitule_complet=element.groupement_contenant.intitule_complet,
                            obligatoire=element.groupement_contenant.obligatoire,
                            chemin_acces=""
                        ),
                        contenu=cls.__convert_contenu(element.contenu_ordonne_catalogue)
                    )
                )
            else:
                result.append(
                    UniteEnseignementDTO(
                        bloc=element.bloc,
                        code=element.code,
                        intitule_complet=element.intitule_complet,
                        quadrimestre=element.quadrimestre,
                        quadrimestre_texte=element.quadrimestre_texte,
                        credits_absolus=element.credits_absolus,
                        volume_annuel_pm=element.volume_annuel_pm,
                        volume_annuel_pp=element.volume_annuel_pp,
                        obligatoire=element.obligatoire,
                        session_derogation=element.session_derogation,
                        credits_relatifs=element.credits_relatifs,
                        chemin_acces="",
                    )
                )
        return result

    @classmethod
    def __build_unite_enseignement_ajoute_dto(
            cls,
            unite_enseignement_ajoute: 'UniteEnseignementAjoutee',
            unite_enseignement_dtos: List['UniteEnseignementCatalogueDTO']
    ) -> 'UniteEnseignementDTO':
        unite_enseignement_dto_correspondant = next(
            dto for dto in unite_enseignement_dtos if dto.code == unite_enseignement_ajoute.code
        )
        return UniteEnseignementDTO(
            code=unite_enseignement_ajoute.code,
            obligatoire=unite_enseignement_dto_correspondant.obligatoire,
            bloc=1,
            session_derogation=unite_enseignement_dto_correspondant.session_derogation,
            credits_relatifs=unite_enseignement_dto_correspondant.credits_relatifs,
            chemin_acces="",
            intitule_complet=unite_enseignement_dto_correspondant.intitule_complet,
            quadrimestre=unite_enseignement_dto_correspondant.quadrimestre,
            quadrimestre_texte=unite_enseignement_dto_correspondant.quadrimestre_texte,
            credits_absolus=unite_enseignement_dto_correspondant.credits_absolus,
            volume_annuel_pm=unite_enseignement_dto_correspondant.volume_annuel_pm,
            volume_annuel_pp=unite_enseignement_dto_correspondant.volume_annuel_pp,
            ajoutee=True
        )

