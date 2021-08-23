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
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO, TutorClassRepartitionDTO
from infrastructure.encodage_de_notes.shared_kernel.service.attribution_enseignant import \
    AttributionEnseignantTranslator


class SearchAttributionsEnseignantTest(SimpleTestCase):

    def setUp(self) -> None:
        self.code_unite_enseignement = "LDROI1001"
        self.annee = 2020
        self.translator = AttributionEnseignantTranslator()
        self.matricule_fgs_enseignant = '12345678'
        self.attribution_unite_enseignement_dto = TutorAttributionToLearningUnitDTO(
            learning_unit_code=self.code_unite_enseignement,
            learning_unit_year=self.annee,
            attribution_uuid='uuid-attribution',
            last_name='Smith',
            first_name='Pierre',
            personal_id_number=self.matricule_fgs_enseignant,
            function='FUNCTION',
            lecturing_volume_attributed=10.0,
            practical_volume_attributed=15.0,
        )
        self.code_complet_classe = self.code_unite_enseignement + 'A'
        self.repartition_classe_dto = TutorClassRepartitionDTO(
            attribution_uuid='uuid-attribution',
            last_name='Smith',
            first_name='Pierre',
            function='FUNCTION',
            distributed_volume_to_class='10.0',
            personal_id_number=self.matricule_fgs_enseignant,
            complete_class_code=self.code_complet_classe,
            annee=self.annee,
        )

    @mock.patch("infrastructure.messages_bus.search_tutors_distributed_to_class")
    @mock.patch("infrastructure.messages_bus.search_attributions_to_learning_unit")
    def test_should_trouver_attribution_unite_enseignement_sans_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = [self.repartition_classe_dto]
        result = self.translator.search_attributions_enseignant(self.code_unite_enseignement, self.annee)
        dto = list(result)[0]
        detail_assertion = "Seule l'attribution à l'unite enseignement doit être renvoyée, pas l'attrib. à la classe"
        self.assertNotEqual(self.code_complet_classe, dto.code_unite_enseignement, detail_assertion)
        self.assertEqual(self.code_unite_enseignement, dto.code_unite_enseignement, detail_assertion)

    @mock.patch("infrastructure.messages_bus.search_tutors_distributed_to_class")
    @mock.patch("infrastructure.messages_bus.search_attributions_to_learning_unit")
    def test_should_trouver_repartition_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = []
        mock_classes.return_value = [self.repartition_classe_dto]
        result = self.translator.search_attributions_enseignant(self.code_complet_classe, self.annee)
        detail_assertion = "Seule l'attribution à la classe doit être renvoyée, pas l'attribution à l'UE"
        self.assertEqual(list(result)[0].code_unite_enseignement, self.code_complet_classe, detail_assertion)
        self.assertNotEqual(list(result)[0].code_unite_enseignement, self.code_unite_enseignement, detail_assertion)

    @mock.patch("infrastructure.messages_bus.search_tutors_distributed_to_class")
    @mock.patch("infrastructure.messages_bus.search_attributions_to_learning_unit")
    def test_should_trouver_attribution_unite_enseignement(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = []
        result = self.translator.search_attributions_enseignant(self.code_complet_classe, self.annee)
        self.assertNotEqual(self.code_complet_classe, list(result)[0].code_unite_enseignement)
        self.assertEqual(self.code_unite_enseignement, list(result)[0].code_unite_enseignement)

    @mock.patch("infrastructure.messages_bus.search_tutors_distributed_to_class")
    @mock.patch("infrastructure.messages_bus.search_attributions_to_learning_unit")
    def test_should_convertir_attribution_unite_enseignement(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = []
        result = self.translator.search_attributions_enseignant(self.code_unite_enseignement, self.annee)
        dto = list(result)[0]
        self.assertEqual(self.matricule_fgs_enseignant, dto.matricule_fgs_enseignant)
        self.assertEqual(self.code_unite_enseignement, dto.code_unite_enseignement)
        self.assertEqual(self.annee, dto.annee)
        self.assertEqual('Smith', dto.nom)
        self.assertEqual('Pierre', dto.prenom)

    @mock.patch("infrastructure.messages_bus.search_tutors_distributed_to_class")
    @mock.patch("infrastructure.messages_bus.search_attributions_to_learning_unit")
    def test_should_convertir_repartition_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = []
        mock_classes.return_value = [self.repartition_classe_dto]
        result = self.translator.search_attributions_enseignant(self.code_unite_enseignement, self.annee)
        dto = list(result)[0]
        self.assertEqual(self.matricule_fgs_enseignant, dto.matricule_fgs_enseignant)
        self.assertEqual(self.code_complet_classe, dto.code_unite_enseignement)
        self.assertEqual(self.annee, dto.annee)
        self.assertEqual('Smith', dto.nom)
        self.assertEqual('Pierre', dto.prenom)


class AttributionEnseignantTest(SimpleTestCase):

    def setUp(self) -> None:
        self.code_unite_enseignement = "LDROI1001"
        self.annee = 2020
        self.translator = AttributionEnseignantTranslator()
        self.matricule_fgs_enseignant = '12345678'
        self.attribution_unite_enseignement_dto = TutorAttributionToLearningUnitDTO(
            learning_unit_code=self.code_unite_enseignement,
            learning_unit_year=self.annee,
            attribution_uuid='uuid-attribution',
            last_name='Smith',
            first_name='Pierre',
            personal_id_number=self.matricule_fgs_enseignant,
            function='FUNCTION',
            lecturing_volume_attributed=10.0,
            practical_volume_attributed=15.0,
        )
        self.code_complet_classe = self.code_unite_enseignement + 'A'
        self.repartition_classe_dto = TutorClassRepartitionDTO(
            attribution_uuid='uuid-attribution',
            last_name='Smith',
            first_name='Pierre',
            function='FUNCTION',
            distributed_volume_to_class='10.0',
            personal_id_number=self.matricule_fgs_enseignant,
            complete_class_code=self.code_complet_classe,
            annee=self.annee,
        )

    @mock.patch("infrastructure.messages_bus.search_classes_enseignant")
    @mock.patch("infrastructure.messages_bus.search_attributions_enseignant")
    def test_should_trouver_attribution_unite_enseignement(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = []
        result = self.translator.search_attributions_enseignant_par_matricule(self.annee, self.matricule_fgs_enseignant)
        self.assertEqual(self.code_unite_enseignement, list(result)[0].code_unite_enseignement)

    @mock.patch("infrastructure.messages_bus.search_classes_enseignant")
    @mock.patch("infrastructure.messages_bus.search_attributions_enseignant")
    def test_should_trouver_attribution_ue_et_repartition_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = [self.repartition_classe_dto]

        result = self.translator.search_attributions_enseignant_par_matricule(self.annee, self.matricule_fgs_enseignant)

        detail_assertion = "L'attribution à l'unite enseignement ET la répartition sur la classe doivent être renvoyées"
        self.assertEqual(2, len(result))
        codes = [dto.code_unite_enseignement for dto in result]
        self.assertIn(self.code_complet_classe, codes, detail_assertion)
        self.assertIn(self.code_unite_enseignement, codes, detail_assertion)

    @mock.patch("infrastructure.messages_bus.search_classes_enseignant")
    @mock.patch("infrastructure.messages_bus.search_attributions_enseignant")
    def test_should_trouver_repartition_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = []
        mock_classes.return_value = [self.repartition_classe_dto]
        result = self.translator.search_attributions_enseignant_par_matricule(self.annee, self.matricule_fgs_enseignant)
        self.assertEqual(self.code_complet_classe, list(result)[0].code_unite_enseignement)

    @mock.patch("infrastructure.messages_bus.search_classes_enseignant")
    @mock.patch("infrastructure.messages_bus.search_attributions_enseignant")
    def test_should_convertir_attribution_unite_enseignement(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = [self.attribution_unite_enseignement_dto]
        mock_classes.return_value = []
        result = self.translator.search_attributions_enseignant_par_matricule(self.annee, self.matricule_fgs_enseignant)
        dto = list(result)[0]
        self.assertEqual(self.matricule_fgs_enseignant, dto.matricule_fgs_enseignant)
        self.assertEqual(self.code_unite_enseignement, dto.code_unite_enseignement)
        self.assertEqual(self.annee, dto.annee)
        self.assertEqual('Smith', dto.nom)
        self.assertEqual('Pierre', dto.prenom)

    @mock.patch("infrastructure.messages_bus.search_classes_enseignant")
    @mock.patch("infrastructure.messages_bus.search_attributions_enseignant")
    def test_should_convertir_repartition_classe(self, mock_unites_enseignement, mock_classes):
        mock_unites_enseignement.return_value = []
        mock_classes.return_value = [self.repartition_classe_dto]
        result = self.translator.search_attributions_enseignant_par_matricule(self.annee, self.matricule_fgs_enseignant)
        dto = list(result)[0]
        self.assertEqual(self.matricule_fgs_enseignant, dto.matricule_fgs_enseignant)
        self.assertEqual(self.code_complet_classe, dto.code_unite_enseignement)
        self.assertEqual(self.annee, dto.annee)
        self.assertEqual('Smith', dto.nom)
        self.assertEqual('Pierre', dto.prenom)
