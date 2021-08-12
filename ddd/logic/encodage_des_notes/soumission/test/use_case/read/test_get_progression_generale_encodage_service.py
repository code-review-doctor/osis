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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import GetProgressionGeneraleCommand
from ddd.logic.encodage_des_notes.soumission.dtos import SignaletiqueEtudiantDTO, AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.tests.factory._note_etudiant import NoteManquanteEtudiantFactory
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecUneSeuleNoteManquante, \
    FeuilleDeNotesAvecNotesEncodeesEtNotesManquantes, FeuilleDeNotesAvecNotesSoumises, \
    FeuilleDeNotesDateLimiteRemiseHierEtAujourdhui
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.unite_enseignement import \
    UniteEnseignementTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class GetProgressionGeneraleEncodageTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.noma = '11111111'
        self.nom_cohorte = 'DROI1BA'

        self.feuille_de_notes = FeuilleDeNotesAvecUneSeuleNoteManquante(
            notes={
                NoteManquanteEtudiantFactory(entity_id__noma=self.noma)
            }
        )
        self.repository = FeuilleDeNotesInMemoryRepository()
        self.repository.save(self.feuille_de_notes)

        self.cmd = GetProgressionGeneraleCommand(matricule_fgs_enseignant=self.matricule_enseignant)

        self.periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.signaletique_translator = SignaletiqueEtudiantTranslatorInMemory()
        self.unite_enseignement_trans = UniteEnseignementTranslatorInMemory()
        self.__mock_service_bus()
        self.addCleanup(lambda *args, **kwarg: self.repository.entities.clear())

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            FeuilleDeNotesRepository=lambda: self.repository,
            PeriodeEncodageNotesTranslator=lambda: self.periode_soumission_translator,
            SignaletiqueEtudiantTranslator=lambda: self.signaletique_translator,
            AttributionEnseignantTranslator=lambda: self.attribution_translator,
            UniteEnseignementTranslator=lambda: self.unite_enseignement_trans,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_calculer_annee_academique_et_numero_session(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.annee_academique, self.annee)
        self.assertEqual(result.numero_session, self.numero_session)

    def test_should_renvoyer_detail_unite_enseignement(self):
        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertEqual(progression_premiere_unite_enseign.code_unite_enseignement, self.code_unite_enseignement)
        self.assertEqual(
            progression_premiere_unite_enseign.intitule_complet_unite_enseignement,
            "Intitule complet unite enseignement"
        )

    def test_should_calculer_si_possede_au_moins_1_etudiant_peps(self):
        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertTrue(progression_premiere_unite_enseign.a_etudiants_peps)

    @mock.patch("infrastructure.messages_bus.SignaletiqueEtudiantTranslator")
    def test_should_calculer_si_possede_aucun_etudiant_peps(self, mock_translator):
        etudiant_sans_peps = SignaletiqueEtudiantDTO(
            noma=self.noma,
            nom="Dupont",
            prenom="Marie",
            peps=None,
        )
        signaletique_translator = SignaletiqueEtudiantTranslatorInMemory()
        signaletique_translator.search = lambda *args, **kwargs: {etudiant_sans_peps}
        mock_translator.return_value = signaletique_translator

        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertFalse(progression_premiere_unite_enseign.a_etudiants_peps)

    def test_should_grouper_et_ordonner_par_date_echeance(self):
        nombre_de_dates_echeances = 2
        aujourdhui = datetime.date.today()
        hier = aujourdhui - datetime.timedelta(days=1)

        feuille_de_notes = FeuilleDeNotesDateLimiteRemiseHierEtAujourdhui()
        self.repository.save(feuille_de_notes)

        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertEqual(len(progression_premiere_unite_enseign.dates_echeance), nombre_de_dates_echeances)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].jour, hier.day)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].mois, hier.month)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].annee, hier.year)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[1].jour, aujourdhui.day)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[1].mois, aujourdhui.month)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[1].annee, aujourdhui.year)

    def test_should_calculer_aucune_note_soumise(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesEncodeesEtNotesManquantes()
        self.repository.save(feuille_de_notes)
        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].quantite_notes_soumises, 0)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].quantite_total_notes, 4)

    def test_should_calculer_1_note_soumise(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesSoumises()
        self.repository.save(feuille_de_notes)
        result = self.message_bus.invoke(self.cmd)
        progression_premiere_unite_enseign = result.progression_generale[0]
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].quantite_notes_soumises, 2)
        self.assertEqual(progression_premiere_unite_enseign.dates_echeance[0].quantite_total_notes, 4)

    @mock.patch("infrastructure.messages_bus.AttributionEnseignantTranslator")
    def test_should_ordonner_plusieurs_unites_enseignement(self, mock_attrib_translator):
        self.repository.save(FeuilleDeNotesAvecUneSeuleNoteManquante(entity_id__code_unite_enseignement="LDROI1003"))
        self.repository.save(FeuilleDeNotesAvecUneSeuleNoteManquante(entity_id__code_unite_enseignement="LDROI1001"))
        self.repository.save(FeuilleDeNotesAvecUneSeuleNoteManquante(entity_id__code_unite_enseignement="LDROI1002"))
        attribution_translator = AttributionEnseignantTranslatorInMemory()
        attribution_translator.search_attributions_enseignant_par_matricule = lambda *args, **kwargs: {
            AttributionEnseignantDTO(
                matricule_fgs_enseignant=self.matricule_enseignant,
                code_unite_enseignement="LDROI1002",
                annee=self.annee,
                nom="Smith",
                prenom="Charles",
            ),
            AttributionEnseignantDTO(
                matricule_fgs_enseignant=self.matricule_enseignant,
                code_unite_enseignement="LDROI1001",
                annee=self.annee,
                nom="Jolypas",
                prenom="Michelle",
            ),
            AttributionEnseignantDTO(
                matricule_fgs_enseignant=self.matricule_enseignant,
                code_unite_enseignement="LDROI1003",
                annee=self.annee,
                nom="Carcarson",
                prenom="Alphonse",
            ),
        }
        mock_attrib_translator.return_value = attribution_translator

        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(len(result.progression_generale), 3)
        self.assertEqual(result.progression_generale[0].code_unite_enseignement, "LDROI1001")
        self.assertEqual(result.progression_generale[1].code_unite_enseignement, "LDROI1002")
        self.assertEqual(result.progression_generale[2].code_unite_enseignement, "LDROI1003")
