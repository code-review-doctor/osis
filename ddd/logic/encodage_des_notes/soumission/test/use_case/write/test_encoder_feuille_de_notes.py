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

import attr
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.exam_enrollment_justification_type import TutorJustificationTypes
from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand, NoteEtudiantCommand
from ddd.logic.encodage_des_notes.soumission.domain.model._note import Justification, NoteChiffree
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException, \
    EnseignantNonAttribueUniteEnseignementException, AucunEtudiantTrouveException, NoteIncorrecteException, \
    NoteDejaSoumiseException
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import NomaNeCorrespondPasEmailException, \
    DateEcheanceNoteAtteinteException, NoteDecimaleNonAutoriseeException
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecNotesManquantes, \
    FeuilleDeNotesDecimalesAutorisees, FeuilleDeNotesAvecToutesNotesSoumises, \
    FeuilleDeNotesDateLimiteRemiseAujourdhui, FeuilleDeNotesDateLimiteRemiseHier
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class EncoderFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.matricule_enseignant = '00321234'

        self.feuille_de_notes = FeuilleDeNotesAvecNotesManquantes()
        self.note_manquante = list(self.feuille_de_notes.notes)[0]
        self.repository = FeuilleDeNotesInMemoryRepository()
        self.repository.save(self.feuille_de_notes)

        self.cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=self.feuille_de_notes.annee,
            numero_session=self.feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[],
        )

        self.periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            FeuilleDeNotesRepository=lambda: self.repository,
            PeriodeEncodageNotesTranslator=lambda: PeriodeEncodageNotesTranslatorInMemory(),
            AttributionEnseignantTranslator=lambda: AttributionEnseignantTranslatorInMemory(),
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_periode_fermee_depuis_hier(self, mock_periode_translator):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_fermee
        mock_periode_translator.return_value = periode_soumission_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            self.message_bus.invoke(cmd)

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_autoriser_si_periode_ferme_aujourdhui(self, mock_periode_translator):
        aujourdhui = datetime.date.today()
        date_aujourdhui = DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year)
        date_dans_le_passe = DateDTO(jour=1, mois=1, annee=1950)
        periode_ouverte = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_aujourdhui,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_ouverte
        mock_periode_translator.return_value = periode_soumission_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        self.assertTrue(
            self.message_bus.invoke(cmd),
            "Si la date de fermeture est aujourdhui, alors l'encodage est autorisé jusqu'à aujourdhui 23h59"
        )

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_autoriser_si_periode_ouvre_aujourdhui(self, mock_periode_translator):
        aujourdhui = datetime.date.today()
        date_aujourdhui = DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year)
        date_dans_le_futur = DateDTO(jour=1, mois=1, annee=9999)
        periode_ouverte = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=date_aujourdhui,
            fin_periode_soumission=date_dans_le_futur,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_ouverte
        mock_periode_translator.return_value = periode_soumission_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        self.assertTrue(
            self.message_bus.invoke(cmd),
            "Si la période d'encodage ouvre aujourdhui, alors l'encodage est autorisé à partir de aujourd'hui 00h01"
        )

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_aucune_periode_trouvee(self, mock_periode_translator):
        aucune_periode_trouvee = None
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: aucune_periode_trouvee
        mock_periode_translator.return_value = periode_soumission_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            self.message_bus.invoke(cmd)

    @mock.patch("infrastructure.messages_bus.AttributionEnseignantTranslator")
    def test_should_empecher_si_utilisateur_non_attribue_unite_enseignement(self, mock_attribution_translator):
        attribution_autre_unite_enseignement = AttributionEnseignantDTO(
            matricule_fgs_enseignant=self.matricule_enseignant,
            code_unite_enseignement="LAUTRE1234",
            annee=self.feuille_de_notes.annee,
            nom="Smith",
            prenom="Charles",
        )
        attribution_translator = AttributionEnseignantTranslatorInMemory()
        attribution_translator.search_attributions_enseignant = lambda **kwargs: {attribution_autre_unite_enseignement}
        mock_attribution_translator.return_value = attribution_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            self.message_bus.invoke(cmd)

    @mock.patch("infrastructure.messages_bus.AttributionEnseignantTranslator")
    def test_should_empecher_si_utilisateur_aucune_attribution(self, mock_attribution_translator):
        aucune_attribution = set()
        attribution_translator = AttributionEnseignantTranslatorInMemory()
        attribution_translator.search_attributions_enseignant = lambda **kwargs: aucune_attribution
        mock_attribution_translator.return_value = attribution_translator

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            self.message_bus.invoke(cmd)

    def test_should_empecher_si_date_de_remise_est_hier(self):
        feuille_de_notes = FeuilleDeNotesDateLimiteRemiseHier()
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=list(feuille_de_notes.notes)[0].noma,
                    email=list(feuille_de_notes.notes)[0].email,
                    note='12'
                )
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DateEcheanceNoteAtteinteException
        )

    def test_should_autoriser_si_date_de_remise_est_aujourdhui(self):
        feuille_de_notes = FeuilleDeNotesDateLimiteRemiseAujourdhui()
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=list(feuille_de_notes.notes)[0].noma,
                    email=list(feuille_de_notes.notes)[0].email,
                    note='12'
                )
            ],
        )
        self.assertTrue(
            self.message_bus.invoke(cmd),
            """Si la date de remise est aujourd'hui, l'encodage de la note est autorisée jusqu'à aujourd'hui 23h59"""
        )

    def test_should_empecher_si_email_correspond_pas_noma(self):
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email="email@ne_corespond_pas.be", note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NomaNeCorrespondPasEmailException
        )

    def test_should_empecher_si_etudiant_pas_sur_feuille_de_notes(self):
        noma_pas_sur_feuille_de_notes = "9999999999"
        note_etudiant = NoteEtudiantCommand(
            noma=noma_pas_sur_feuille_de_notes,
            email=self.note_manquante.email,
            note='12',
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AucunEtudiantTrouveException
        )

    def test_should_empecher_si_note_inferieure_0(self):
        note_inferieure_0 = "-1"
        note_etudiant = NoteEtudiantCommand(
            noma=self.note_manquante.noma,
            email=self.note_manquante.email,
            note=note_inferieure_0,
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_superieure_20(self):
        note_superieure_20 = "21"
        note_etudiant = NoteEtudiantCommand(
            noma=self.note_manquante.noma,
            email=self.note_manquante.email,
            note=note_superieure_20,
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_pas_lettre_autorisee(self):
        lettre_inexistante = "S"
        note_etudiant = NoteEtudiantCommand(
            noma=self.note_manquante.noma,
            email=self.note_manquante.email,
            note=lettre_inexistante,
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_mal_formatee(self):
        lettre_inexistante = "T 12"
        note_etudiant = NoteEtudiantCommand(
            noma=self.note_manquante.noma,
            email=self.note_manquante.email,
            note=lettre_inexistante,
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_decimale_non_autorisee(self):
        note_decimale = "12.5"
        note_etudiant = NoteEtudiantCommand(
            noma=self.note_manquante.noma,
            email=self.note_manquante.email,
            note=note_decimale,
        )
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteDecimaleNonAutoriseeException
        )

    def test_should_encoder_si_note_decimale_autorisee(self):
        feuille_de_notes = FeuilleDeNotesDecimalesAutorisees()
        note_avec_decimale_autorisee = list(feuille_de_notes.notes)[0]
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=note_avec_decimale_autorisee.noma,
                    email=note_avec_decimale_autorisee.email,
                    note='12.5'
                )
            ],
        )
        entity_id = self.message_bus.invoke(cmd)
        self.assertEqual(list(self.repository.get(entity_id).notes)[0].note.value, Decimal(12.5))

    def test_should_empecher_si_note_deja_soumise(self):
        feuille_de_notes = FeuilleDeNotesAvecToutesNotesSoumises()
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=list(feuille_de_notes.notes)[0].noma,
                    email=list(feuille_de_notes.notes)[0].email,
                    note='12'
                )
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteDejaSoumiseException
        )

    def test_should_encoder_liste_de_notes(self):
        feuille_de_notes = FeuilleDeNotesAvecNotesManquantes()
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=note.noma,
                    email=note.email,
                    note='12'
                ) for note in feuille_de_notes.notes
            ],
        )
        entity_id = self.message_bus.invoke(cmd)
        expected_result = NoteChiffree(value=Decimal(12.0))
        for note in self.repository.get(entity_id).notes:
            self.assertEqual(note.note, expected_result)

    def test_should_encoder_absence_injustifiee(self):
        for absence_injustifiee in ['A', TutorJustificationTypes.ABSENCE_UNJUSTIFIED.name]:
            with self.subTest(absence=absence_injustifiee):
                note_etudiant = NoteEtudiantCommand(
                    noma=self.note_manquante.noma,
                    email=self.note_manquante.email,
                    note=absence_injustifiee,
                )
                cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
                entity_id = self.message_bus.invoke(cmd)
                expected_result = Justification(value=TutorJustificationTypes.ABSENCE_UNJUSTIFIED)
                self.assertEqual(list(self.repository.get(entity_id).notes)[0].note, expected_result)

    def test_should_encoder_tricherie(self):
        for tricherie in ['T', TutorJustificationTypes.CHEATING.name]:
            with self.subTest(tricherie=tricherie):
                note_etudiant = NoteEtudiantCommand(
                    noma=self.note_manquante.noma,
                    email=self.note_manquante.email,
                    note=tricherie,
                )
                cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
                entity_id = self.message_bus.invoke(cmd)
                expected_result = Justification(value=TutorJustificationTypes.CHEATING)
                self.assertEqual(list(self.repository.get(entity_id).notes)[0].note, expected_result)

    def test_should_aggreger_erreurs_plusieurs_notes(self):
        feuille_de_notes = FeuilleDeNotesAvecToutesNotesSoumises()
        self.repository.save(feuille_de_notes)
        notes = list(feuille_de_notes.notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=notes[0].noma,
                    email=notes[0].email,
                    note='12'
                ),
                NoteEtudiantCommand(
                    noma=notes[1].noma,
                    email=notes[1].email,
                    note='12'
                ),
                NoteEtudiantCommand(
                    noma=notes[2].noma,
                    email=notes[2].email,
                    note='12'
                ),
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exceptions = class_exceptions.exception.exceptions
        self.assertEqual(len(exceptions), 3)
        for exception in exceptions:
            self.assertIsInstance(exception, NoteDejaSoumiseException)
