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
from decimal import Decimal

import mock
from django.test import SimpleTestCase

from ddd.logic.preparation_programme_annuel_etudiant.commands import GetContenuGroupementCommand
from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementContenantDTO, UniteEnseignementContenueDTO
from ddd.logic.preparation_programme_annuel_etudiant.tests.factory.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCoursFactory
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslatorInMemory
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_unites_enseignement \
    import \
    CatalogueUnitesEnseignementTranslatorInMemory
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours \
    import \
    GroupementAjusteInscriptionCoursInMemoryRepository


class GetContenuGroupementServiceTest(SimpleTestCase):

    def setUp(self) -> None:
        self.catalogue_formations_translator = CatalogueFormationsTranslatorInMemory()
        self.catalogue_unites_enseignements_translator = CatalogueUnitesEnseignementTranslatorInMemory()
        self.repo = GroupementAjusteInscriptionCoursInMemoryRepository()

        self.__mock_service_bus()

        self.cmd = GetContenuGroupementCommand(
            annee=2021,
            code_groupement="MAT2ECGE",
            code_programme="LECGE100B"
        )

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            CatalogueFormationsTranslator=lambda: self.catalogue_formations_translator,
            CatalogueUnitesEnseignementTranslator=lambda: self.catalogue_unites_enseignements_translator,
            GroupementAjusteInscriptionCoursInMemoryRepository=lambda: self.repo
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_retourner_contenu_vide_si_groupement_est_vide(self):
        cmd = GetContenuGroupementCommand(
            annee=2021,
            code_groupement="MAT2ECGE",
            code_programme="LECGE100B"
        )

        result = self.message_bus.invoke(cmd)

        expected_result = GroupementContenantDTO(
            intitule="Economie et gestion",
            intitule_complet="Economie et gestion",
            elements_contenus=[]
        )

        self.assertEqual(result, expected_result)

    def test_should_retourner_contenu_sans_ajustement(self):
        cmd = GetContenuGroupementCommand(
            annee=2021,
            code_groupement="LECGE100R",
            code_programme="LECGE100B"
        )

        result = self.message_bus.invoke(cmd)

        expected_result = GroupementContenantDTO(
            intitule="Formation pluridisciplinaire en sciences humaines",
            intitule_complet="Formation pluridisciplinaire en sciences humaines",
            elements_contenus=[
                UniteEnseignementContenueDTO(
                    bloc=3,
                    code='LESPO1321',
                    intitule_complet='Economic, Political and Social Ethics',
                    quadrimestre_texte='Q2',
                    credits_absolus=Decimal(3),
                    credits_relatifs=None,
                    volume_annuel_pm=30,
                    volume_annuel_pp=0,
                    obligatoire=True,
                    session_derogation='',
                )
            ]
        )

        self._assert_equals_groupement_contenant_DTO(expected_result, result)

    def test_should_retourner_contenu_du_groupement_ajuste_si_groupement_a_une_ue_ajoutee(self):
        self.repo.entities.append(
            GroupementAjusteInscriptionCoursFactory(groupement_id__code='LECGE100R', ajoutees=True)
        )

        cmd = GetContenuGroupementCommand(
            annee=2021,
            code_groupement="LECGE100R",
            code_programme="LECGE100B"
        )

        result = self.message_bus.invoke(cmd)

        expected_result = GroupementContenantDTO(
            intitule="Formation pluridisciplinaire en sciences humaines",
            intitule_complet="Formation pluridisciplinaire en sciences humaines",
            elements_contenus=[
                UniteEnseignementContenueDTO(
                    bloc=3,
                    code='LESPO1321',
                    intitule_complet='Economic, Political and Social Ethics',
                    quadrimestre_texte='Q2',
                    credits_absolus=Decimal(3),
                    credits_relatifs=None,
                    volume_annuel_pm=30,
                    volume_annuel_pp=0,
                    obligatoire=True,
                    session_derogation='',
                ),
                UniteEnseignementContenueDTO(
                    bloc=1,
                    code='LSINF1311',
                    intitule_complet='Human-computer interaction',
                    quadrimestre_texte='Q1',
                    credits_absolus=Decimal(5),
                    credits_relatifs=None,
                    volume_annuel_pm=30,
                    volume_annuel_pp=15,
                    obligatoire=True,
                    session_derogation='',
                    ajoute=True
                )
            ]
        )

        self._assert_equals_groupement_contenant_DTO(expected_result, result)

    def _assert_equals_groupement_contenant_DTO(self, expected_result, result):
        self.assertEqual(result.intitule, expected_result.intitule)
        self.assertEqual(result.intitule_complet, expected_result.intitule_complet)
        for cpt, ue_resultat in enumerate(result.elements_contenus):
            ue_expected = expected_result.elements_contenus[cpt]
            self.assertEqual(ue_resultat.bloc, ue_expected.bloc)
            self.assertEqual(ue_resultat.code, ue_expected.code)
            self.assertEqual(ue_resultat.intitule_complet, ue_expected.intitule_complet)
            self.assertEqual(ue_resultat.quadrimestre_texte, ue_expected.quadrimestre_texte)
            self.assertEqual(ue_resultat.credits_absolus, ue_expected.credits_absolus)
            self.assertEqual(ue_resultat.credits_relatifs, ue_expected.credits_relatifs)
            self.assertEqual(ue_resultat.volume_annuel_pm, ue_expected.volume_annuel_pm)
            self.assertEqual(ue_resultat.volume_annuel_pp, ue_expected.volume_annuel_pp)
            self.assertEqual(ue_resultat.obligatoire, ue_expected.obligatoire)
            self.assertEqual(ue_resultat.session_derogation, ue_expected.session_derogation)
