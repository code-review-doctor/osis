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
from typing import List, Optional, Union

import attr

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_supprimee import \
    UniteEnseignementSupprimee
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
from preparation_inscription.utils.chiffres_significatifs_de_decimal import get_chiffres_significatifs


class GetContenuGroupement(interface.DomainService):
    @classmethod
    def get_contenu_groupement(
            cls,
            cmd: 'GetContenuGroupementCommand',
            repo: 'IGroupementAjusteInscriptionCoursRepository',
            catalogue_formations_translator: 'ICatalogueFormationsTranslator',
            catalogue_unites_enseignement_translator: 'ICatalogueUnitesEnseignementTranslator'
    ) -> 'GroupementContenantDTO':

        contenu_groupement = catalogue_formations_translator.get_contenu_groupement(cmd=cmd)

        try:
            groupement_ajuste = repo.search(
                programme_id=GroupIdentity(code=cmd.code_formation, year=cmd.annee),
                groupement_id=GroupIdentity(code=cmd.code, year=cmd.annee)
            )[0]
            unites_enseignements_ajustees_dto = catalogue_unites_enseignement_translator.search(
                entity_ids=groupement_ajuste.get_identites_unites_enseignement_ajustees()
            )
            unites_enseignement_ajoutees_dto = [
                ue for ue in unites_enseignements_ajustees_dto if ue.code in [
                    ue.code for ue in groupement_ajuste.get_identites_unites_enseignement_ajoutees()
                ]
            ]
            unites_enseignement_supprimees_dto = [
                ue for ue in unites_enseignements_ajustees_dto if ue.code in [
                    ue.code for ue in groupement_ajuste.get_identites_unites_enseignement_supprimees()
                ]
            ]
        except IndexError:
            groupement_ajuste = None
            unites_enseignement_ajoutees_dto = []
            unites_enseignement_supprimees_dto = []

        return cls.__ajuster_contenu_groupement(
            contenu_groupement,
            groupement_ajuste,
            unites_enseignement_ajoutees_dto,
            unites_enseignement_supprimees_dto
        )

    @classmethod
    def __ajuster_contenu_groupement(
            cls,
            contenu_groupement: 'GroupementContenantDTO',
            groupement_ajuste: Optional['GroupementAjusteInscriptionCours'],
            unites_enseignement_ajoutees_dto: List['UniteEnseignementCatalogueDTO'],
            unites_enseignement_supprimees_dto: List['UniteEnseignementCatalogueDTO']
    ) -> GroupementContenantDTO:
        if not groupement_ajuste:
            return contenu_groupement

        elements_ajoutes = [
            cls.__convert_unite_enseignement_ajuste_to_element_contenu_dto(
                unite_enseignement_ajoutee,
                unites_enseignement_ajoutees_dto,
                ajoute=True
            ) for unite_enseignement_ajoutee in groupement_ajuste.unites_enseignement_ajoutees
        ]

        elements_supprimes = [
            cls.__convert_unite_enseignement_ajuste_to_element_contenu_dto(
                unite_enseignement_supprimee,
                unites_enseignement_supprimees_dto,
                supprime=True
            ) for unite_enseignement_supprimee in groupement_ajuste.unites_enseignement_supprimees
        ]

        elements_non_ajustes = [
            el for el in contenu_groupement.elements_contenus if el.code not in [el.code for el in elements_supprimes]
        ]

        return attr.evolve(
            contenu_groupement,
            elements_contenus=elements_ajoutes + elements_supprimes + elements_non_ajustes
        )

    @classmethod
    def __convert_unite_enseignement_ajuste_to_element_contenu_dto(
            cls,
            unite_enseignement_ajustee: Union['UniteEnseignementAjoutee', 'UniteEnseignementSupprimee'],
            unite_enseignement_dtos: List['UniteEnseignementCatalogueDTO'],
            ajoute=False,
            supprime=False
    ) -> 'ElementContenuDTO':
        unite_enseignement_dto_correspondant = next(
            dto for dto in unite_enseignement_dtos if dto.code == unite_enseignement_ajustee.code
        )
        return ElementContenuDTO(
            code=unite_enseignement_ajustee.code,
            obligatoire=unite_enseignement_dto_correspondant.obligatoire,
            bloc=str(unite_enseignement_dto_correspondant.bloc),
            session_derogation=unite_enseignement_dto_correspondant.session_derogation,
            intitule_complet=unite_enseignement_dto_correspondant.intitule_complet,
            quadrimestre_texte=unite_enseignement_dto_correspondant.quadrimestre_texte,
            credits_absolus=unite_enseignement_dto_correspondant.credits_absolus,
            credits_relatifs=unite_enseignement_dto_correspondant.credits_relatifs,
            volume_annuel_pm=unite_enseignement_dto_correspondant.volume_annuel_pm,
            volume_annuel_pp=unite_enseignement_dto_correspondant.volume_annuel_pp,
            ajoute=ajoute,
            supprime=supprime
        )


def _get_credits(credits_relatifs, credits_absolus: Decimal) -> str:
    if credits_relatifs:
        if credits_relatifs != credits_absolus:
            return "{}({})".format(credits_relatifs, get_chiffres_significatifs(credits_absolus))
        return "{}".format(get_chiffres_significatifs(credits_relatifs))
    return get_chiffres_significatifs(credits_absolus)
