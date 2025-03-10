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
from decimal import Decimal
from typing import List, Union
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.dtos import UniteEnseignementCatalogueDTO, \
    ContenuGroupementCatalogueDTO
from infrastructure.preparation_programme_annuel_etudiant.domain.service.catalogue_formations import \
    CatalogueFormationsTranslator
from program_management.ddd.domain.program_tree_version import STANDARD
from program_management.ddd.dtos import ProgrammeDeFormationDTO, ContenuNoeudDTO, UniteEnseignementDTO

ANNEE = 2021


class CatalogueFormationsTranslatorTest(SimpleTestCase):

    def setUp(self) -> None:
        self.translator = CatalogueFormationsTranslator()
        self.patch_message_bus = mock.patch(
            "infrastructure.utils.MessageBus.invoke",
            return_value=_build_ProgrammeDeFormationDTO()

        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def test_should_convertir_version_standard(self,):
        program_to_translate = self.message_bus_mocked.return_value

        formation_dto = self.translator.get_formation(
            code_programme=program_to_translate.code,
            annee=program_to_translate.annee,
        )

        self.assertEqual(program_to_translate.annee, formation_dto.annee)
        self.assertEqual(program_to_translate.sigle, formation_dto.sigle)
        self.assertEqual(program_to_translate.version, formation_dto.version)
        self.assertEqual(program_to_translate.intitule_formation, formation_dto.intitule_formation)

        self._assert_equal_contenu_conversion(formation_dto.racine, program_to_translate.racine)

        self._assert_equal_groupements_contenus(
            formation_dto.racine.contenu_ordonne_catalogue,
            program_to_translate.racine.contenu_ordonne,
        )

    def _assert_equal_groupements_contenus(
            self,
            formation_groupements_contenus: List[Union['UniteEnseignementCatalogueDTO', 'ContenuGroupementCatalogueDTO']],
            prgm_racine_groupements_contenus: List[Union['UniteEnseignementDTO', 'ContenuNoeudDTO']],
    ):
        for idx, pgm_contenu in enumerate(formation_groupements_contenus):
            if isinstance(pgm_contenu, UniteEnseignementCatalogueDTO):
                self._assert_equal_unite_conversion(
                    pgm_contenu,
                    prgm_racine_groupements_contenus[idx]
                )
            elif isinstance(pgm_contenu, ContenuGroupementCatalogueDTO):
                self._assert_equal_contenu_conversion(
                    pgm_contenu,
                    prgm_racine_groupements_contenus[idx]
                )

                self._assert_equal_groupements_contenus(
                    pgm_contenu.contenu_ordonne_catalogue,
                    prgm_racine_groupements_contenus[idx].contenu_ordonne
                )

    def _assert_equal_contenu_conversion(
            self,
            formation_contenu: ContenuGroupementCatalogueDTO,
            pgm_contenu: ContenuNoeudDTO
    ):
        self.assertEqual(pgm_contenu.code, formation_contenu.groupement_contenant.code)
        self.assertEqual(pgm_contenu.intitule, formation_contenu.groupement_contenant.intitule)
        self.assertEqual(pgm_contenu.intitule_complet, formation_contenu.groupement_contenant.intitule_complet)
        self.assertEqual(pgm_contenu.obligatoire, formation_contenu.groupement_contenant.obligatoire)
        self.assertEqual(pgm_contenu.remarque, formation_contenu.groupement_contenant.remarque)
        self.assertEqual(pgm_contenu.credits, formation_contenu.groupement_contenant.credits)

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


def _build_ProgrammeDeFormationDTO():
    return ProgrammeDeFormationDTO(
        annee=ANNEE,
        sigle='ECGE1BA',
        code='LECGE100B',
        version=STANDARD,
        transition_name='',
        intitule_formation='Bachelier en sciences économiques et de gestion',
        racine=ContenuNoeudDTO(
            intitule='ECGE1BA',
            code='LECGE100B',
            obligatoire=True,
            remarque='Remarque',
            credits=Decimal(10),
            intitule_complet='Bachelier en sciences économiques et de gestion ',
            contenu_ordonne=[
                ContenuNoeudDTO(
                    intitule='Contenu :',
                    obligatoire=True,
                    remarque='Remarque',
                    credits=Decimal(10),
                    intitule_complet='Contenu :',
                    code='LECGE100T',
                    contenu_ordonne=[
                        UniteEnseignementDTO(
                            bloc=1,
                            code='LESPO1113pp',
                            intitule_complet='Sociologie et anthropologie des mondes contemporains',
                            quadrimestre='Q1or2',
                            quadrimestre_texte='Q1 ou Q2',
                            credits_absolus=Decimal(5),
                            volume_annuel_pm=40,
                            volume_annuel_pp=0,
                            obligatoire=False,
                            credits_relatifs=5,
                            session_derogation='',
                        )
                    ]
                )
            ]
        )
    )
