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
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetFormulaireInscriptionCoursCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ContenuGroupementDTO, \
    GroupementCatalogueDTO, UniteEnseignementCatalogueDTO, ContenuGroupementCatalogueDTO
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslatorInMemory
from program_management.ddd.dtos import UniteEnseignementDTO, ContenuNoeudDTO
from program_management.ddd.domain.program_tree_version import STANDARD, NOT_A_TRANSITION


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

    def test_should_afficher_programme_inscription_cas_nominal_version_stabdard(self):
        obj_FormationDTO_de_depart = CatalogueFormationsTranslatorInMemory.dtos[0]
        cmd = GetFormulaireInscriptionCoursCommand(
            annee_formation=2021,
            sigle_formation='ECGE1BA',
            version_formation=STANDARD,
            transition_formation=NOT_A_TRANSITION
        )

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
            resultat_conversion_en_FormulaireInscriptionCoursDTO.intitule_complet_formation,
            obj_FormationDTO_de_depart.intitule_complet
        )

        self._assert_equal_contenu_conversion(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.racine.groupement_contenant,
            obj_FormationDTO_de_depart.racine.groupement_contenant
        )

        self._assert_equal_groupements_contenus(
            resultat_conversion_en_FormulaireInscriptionCoursDTO.racine.groupements_contenus,
            obj_FormationDTO_de_depart.racine.groupements_contenus,
        )

    def _assert_equal_groupements_contenus(
            self,
            formation_groupements_contenus: List['ContenuGroupementCatalogueDTO'],
            prgm_racine_groupements_contenus: List['ContenuNoeudDTO'],
    ):
        for idx, pgm_contenu in enumerate(formation_groupements_contenus):
            self._assert_equal_contenu_conversion(
                pgm_contenu.groupement_contenant,
                prgm_racine_groupements_contenus[idx].groupement_contenant
            )
            self._assert_equal_groupements_contenus(
                pgm_contenu.groupements_contenus,
                prgm_racine_groupements_contenus[idx].groupements_contenus
            )
            for idx_unite, unite_contenue in enumerate(pgm_contenu.unites_enseignement_contenues):
                self._assert_equal_unite_conversion(
                    unite_contenue,
                    prgm_racine_groupements_contenus[idx].unites_enseignement_contenues[idx_unite]
                )

    def _assert_equal_contenu_conversion(
            self,
            formation_contenu: 'ContenuGroupementDTO',
            pgm_contenu: 'GroupementCatalogueDTO'
    ):

        self.assertEqual(pgm_contenu.intitule, formation_contenu.intitule)
        self.assertEqual(pgm_contenu.intitule_complet, formation_contenu.intitule_complet)
        self.assertEqual(pgm_contenu.obligatoire, formation_contenu.obligatoire)
        self.assertEqual(pgm_contenu.remarque, formation_contenu.remarque)
        self.assertEqual(pgm_contenu.credits, formation_contenu.credits)

    def _assert_equal_unite_conversion(
            self,
            unite_contenue: UniteEnseignementCatalogueDTO,
            unite_contenu_dans_programme: UniteEnseignementDTO
    ):
        self.assertEqual(unite_contenue.bloc, unite_contenu_dans_programme.bloc)
        self.assertEqual(unite_contenue.code, unite_contenu_dans_programme.code)
        self.assertEqual(unite_contenue.intitule_complet, unite_contenu_dans_programme.intitule_complet)
        self.assertEqual(unite_contenue.quadrimestre, unite_contenu_dans_programme.quadrimestre)
        self.assertEqual(unite_contenue.credits_absolus, unite_contenu_dans_programme.credits_absolus)
        self.assertEqual(unite_contenue.volume_annuel_pm, unite_contenu_dans_programme.volume_annuel_pm)
        self.assertEqual(unite_contenue.volume_annuel_pp, unite_contenu_dans_programme.volume_annuel_pp)
        self.assertEqual(unite_contenue.obligatoire, unite_contenu_dans_programme.obligatoire)
        self.assertEqual(unite_contenue.credits_relatifs, unite_contenu_dans_programme.credits_relatifs)
        self.assertEqual(unite_contenue.session_derogation, unite_contenu_dans_programme.session_derogation)
