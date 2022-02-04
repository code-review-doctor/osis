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
from typing import List, Union
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO, \
    GroupementCatalogueDTO, UniteEnseignementCatalogueDTO, ContenuGroupementCatalogueDTO, UniteEnseignementDTO, \
    GroupementDTO
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslatorInMemory, ANNEE


class GetFormulaireInscriptionCoursTest(SimpleTestCase):

    def setUp(self) -> None:
        self.catalogue_formations_translator = CatalogueFormationsTranslatorInMemory()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            CatalogueFormationsTranslator=lambda: self.catalogue_formations_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_afficher_programme_inscription_cas_nominal_version_standard(self):
        obj_FormationDTO_de_depart = CatalogueFormationsTranslatorInMemory.dtos[0]
        cmd = GetFormulaireInscriptionCoursCommand(
            annee=ANNEE,
            code_programme='LECGE100B',
        )

        self._assert_equal_tous_les_attributs_ok_apres_conversion(cmd, obj_FormationDTO_de_depart)

    def test_should_afficher_programme_inscription_cas_formation_version_particuliere(self):
        obj_FormationDTO_de_depart = CatalogueFormationsTranslatorInMemory.dtos[1]
        cmd = GetFormulaireInscriptionCoursCommand(
            annee=ANNEE,
            code_programme='LCORP203S',
        )

        self._assert_equal_tous_les_attributs_ok_apres_conversion(cmd, obj_FormationDTO_de_depart)

    def _assert_equal_tous_les_attributs_ok_apres_conversion(self, cmd, obj_FormationDTO_de_depart):
        resultat_conversion_en_FormulaireInscriptionCoursDTO = self.message_bus.invoke(cmd)
        self.assertEqual(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.annee_formation,
            obj_FormationDTO_de_depart.annee
        )
        self.assertEqual(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.sigle_formation,
            obj_FormationDTO_de_depart.sigle
        )
        self.assertEqual(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.version_formation,
            obj_FormationDTO_de_depart.version
        )
        self.assertEqual(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.intitule_formation,
            obj_FormationDTO_de_depart.intitule_formation
        )
        self.__assert_equal_groupement(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.racine.groupement_contenant,
            obj_FormationDTO_de_depart.racine.groupement_contenant
        )
        self.__assert_equal_contenus(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.racine.contenu,
            obj_FormationDTO_de_depart.racine.contenu_ordonne_catalogue,
        )

    def __assert_equal_contenus(
            self,
            contenu_groupement: List[Union['UniteEnseignementDTO', 'ContenuGroupementDTO']],
            contenu_groupement_catalogue: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']],
    ):
        for idx, element in enumerate(contenu_groupement):
            element_catalogue = contenu_groupement_catalogue[idx]

            if isinstance(element, ContenuGroupementDTO):
                self.__assert_equal_groupement(element.groupement_contenant, element_catalogue.groupement_contenant)
                self.__assert_equal_contenus(element.contenu, element_catalogue.contenu_ordonne_catalogue)
            elif isinstance(element, UniteEnseignementDTO):
                self.__assert_equal_unite_conversion(element, element_catalogue)

    def __assert_equal_groupement(
            self,
            groupement: 'GroupementDTO',
            groupement_catalogue_dto: 'GroupementCatalogueDTO'
    ):

        self.assertEqual(groupement.intitule, groupement_catalogue_dto.intitule)
        self.assertEqual(groupement.intitule_complet, groupement_catalogue_dto.intitule_complet)
        self.assertEqual(groupement.obligatoire, groupement_catalogue_dto.obligatoire)

    def __assert_equal_unite_conversion(
            self,
            unite_enseignement: UniteEnseignementDTO,
            unite_enseignement_catalogue_dto: UniteEnseignementCatalogueDTO
    ):
        self.assertEqual(unite_enseignement.bloc, unite_enseignement_catalogue_dto.bloc)
        self.assertEqual(unite_enseignement.code, unite_enseignement_catalogue_dto.code)
        self.assertEqual(unite_enseignement.intitule_complet, unite_enseignement_catalogue_dto.intitule_complet)
        self.assertEqual(unite_enseignement.quadrimestre, unite_enseignement_catalogue_dto.quadrimestre)
        self.assertEqual(unite_enseignement.quadrimestre_texte, unite_enseignement_catalogue_dto.quadrimestre_texte)
        self.assertEqual(unite_enseignement.credits_absolus, unite_enseignement_catalogue_dto.credits_absolus)
        self.assertEqual(unite_enseignement.volume_annuel_pm, unite_enseignement_catalogue_dto.volume_annuel_pm)
        self.assertEqual(unite_enseignement.volume_annuel_pp, unite_enseignement_catalogue_dto.volume_annuel_pp)
        self.assertEqual(unite_enseignement.obligatoire, unite_enseignement_catalogue_dto.obligatoire)
        self.assertEqual(unite_enseignement.session_derogation, unite_enseignement_catalogue_dto.session_derogation)
        self.assertEqual(unite_enseignement.credits_relatifs, unite_enseignement_catalogue_dto.credits_relatifs)
