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
import datetime
from decimal import Decimal
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.effective_class_repartition.commands import SearchClassesParNomEnseignantCommand
from infrastructure.effective_class_repartition.domain.service.in_memory.tutor_attribution import \
    TutorAttributionToLearningUnitTranslatorInMemory
from infrastructure.effective_class_repartition.repository.in_memory.tutor import TutorRepository as \
    TutorRepositoryInMemory
from infrastructure.messages_bus import message_bus_instance


class SearchClassesEnseignantTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = datetime.date.today().year
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.attribution_uuid = 'attribution_uuid1'

        self.attributions_translator = TutorAttributionToLearningUnitTranslatorInMemory()
        self.tutor_repository = TutorRepositoryInMemory()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            TutorAttributionToLearningUnitTranslator=lambda: self.attributions_translator,
            TutorRepository=lambda: self.tutor_repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_trouver_aucun_resultat(self):
        recherche = 'Personne Inexistante'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertListEqual([], result)

    def test_should_renvoyer_annee_recherchee(self):
        recherche = 'Charles Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual(self.annee, result[0].annee)

    def test_should_renvoyer_uuid_attribution(self):
        recherche = 'Charles Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual(self.attribution_uuid, result[0].attribution_uuid)

    def test_should_renvoyer_matricule_enseignant(self):
        recherche = 'Charles Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual(self.matricule_enseignant, result[0].personal_id_number)

    def test_should_renvoyer_code_classe(self):
        recherche = 'Charles Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('LDROI1001-X', result[0].complete_class_code)

    def test_should_renvoyer_volume_distribue_sur_classe(self):
        recherche = 'Charles Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual(Decimal(5.0), result[0].distributed_volume_to_class)

    def test_should_trouver_enseignant_sur_cours_par_nom(self):
        recherche = 'Smith'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('Smith', result[0].last_name)

    def test_should_trouver_enseignant_sur_cours_par_nom_partiel(self):
        recherche = 'it'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('Smith', result[0].last_name)

    def test_should_trouver_enseignant_sur_cours_par_prenom(self):
        recherche = 'Charles'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('Charles', result[0].first_name)

    def test_should_trouver_enseignant_sur_cours_par_prenom_partiel(self):
        recherche = 'arl'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('Charles', result[0].first_name)

    def test_should_trouver_enseignant_sur_cours_par_nom_partiel_et_prenom_partiel(self):
        recherche = 'arl it'
        cmd = SearchClassesParNomEnseignantCommand(annee=self.annee, nom_prenom=recherche)
        result = self.message_bus.invoke(cmd)
        self.assertEqual('Charles', result[0].first_name)
        self.assertEqual('Smith', result[0].last_name)
