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
import contextlib
import datetime
from decimal import Decimal
from unittest import mock

import attr
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.shared_kernel.domain.model.encoder_notes_rapport import IdentiteEncoderNotesRapport
from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import DateEcheanceNoteAtteinteException, \
    NomaNeCorrespondPasEmailException, NoteDecimaleNonAutoriseeException, PeriodeEncodageNotesFermeeException
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand, EncoderNotesEtudiantCommand
from ddd.logic.encodage_des_notes.soumission.domain.model._note import Justification
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EnseignantNonAttribueUniteEnseignementException, NoteIncorrecteException, NoteDejaSoumiseException, \
    EncoderNotesEtudiantEnLotLigneBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO, AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteDecimalesAuthorisees, NoteDejaSoumise
from infrastructure.encodage_de_notes.shared_kernel.repository.in_memory.encoder_notes_rapport import \
    EncoderNotesRapportInMemoryRepository
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.historiser_notes import \
    HistoriserNotesServiceInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.note_etudiant import \
    NoteEtudiantInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class EncoderNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.matricule_enseignant = '00321234'

        self.note = NoteManquanteEtudiantFactory()
        self.repository = NoteEtudiantInMemoryRepository()
        self.repository.save(self.note)

        self.cmd = EncoderNotesEtudiantCommand(
            code_unite_enseignement=self.note.code_unite_enseignement,
            annee_unite_enseignement=self.note.annee,
            numero_session=self.note.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="12"
                )
            ]
        )

        self.periode_encodage_notes_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.inscription_examen_translator = InscriptionExamenTranslatorInMemory()
        self.historiser_notes_service = HistoriserNotesServiceInMemory()
        self.historiser_notes_service.appels.clear()
        self.rapport_repository = EncoderNotesRapportInMemoryRepository()
        self.rapport_repository.reset()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            NoteEtudiantRepository=lambda: self.repository,
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_notes_translator,
            AttributionEnseignantTranslator=lambda: self.attribution_translator,
            HistoriserNotesService=lambda: self.historiser_notes_service,
            InscriptionExamenTranslator=lambda: self.inscription_examen_translator,
            EncoderNotesRapportRepository=lambda: self.rapport_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_empecher_si_periode_fermee_depuis_hier(self):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeEncodageNotesDTO(
            annee_concernee=self.note.annee,
            session_concernee=self.note.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        self.periode_encodage_notes_translator.get = lambda *args: periode_fermee

        with self.assertRaises(PeriodeEncodageNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_autoriser_si_periode_ferme_aujourdhui(self):
        aujourdhui = datetime.date.today()
        date_aujourdhui = DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year)
        date_dans_le_passe = DateDTO(jour=1, mois=1, annee=1950)
        periode_ouverte = PeriodeEncodageNotesDTO(
            annee_concernee=self.note.annee,
            session_concernee=self.note.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_aujourdhui,
        )
        self.periode_encodage_notes_translator.get = lambda *args: periode_ouverte

        self.assertTrue(
            self.message_bus.invoke(self.cmd),
            "Si la date de fermeture est aujourdhui, alors l'encodage est autorisé jusqu'à aujourdhui 23h59"
        )

    def test_should_autoriser_si_periode_ouvre_aujourdhui(self):
        aujourdhui = datetime.date.today()
        date_aujourdhui = DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year)
        date_dans_le_futur = DateDTO(jour=1, mois=1, annee=9999)
        periode_ouverte = PeriodeEncodageNotesDTO(
            annee_concernee=self.note.annee,
            session_concernee=self.note.numero_session,
            debut_periode_soumission=date_aujourdhui,
            fin_periode_soumission=date_dans_le_futur,
        )
        self.periode_encodage_notes_translator.get = lambda *args: periode_ouverte

        self.assertTrue(
            self.message_bus.invoke(self.cmd),
            "Si la période d'encodage ouvre aujourdhui, alors l'encodage est autorisé à partir de aujourd'hui 00h01"
        )

    def test_should_empecher_si_aucune_periode_trouvee(self):
        aucune_periode_trouvee = None
        self.periode_encodage_notes_translator.get = lambda *args: aucune_periode_trouvee

        with self.assertRaises(PeriodeEncodageNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_utilisateur_non_attribue_unite_enseignement(self):
        attribution_autre_unite_enseignement = AttributionEnseignantDTO(
            matricule_fgs_enseignant=self.matricule_enseignant,
            code_unite_enseignement="LAUTRE1234",
            annee=self.note.annee,
            nom="Smith",
            prenom="Charles",
        )
        self.attribution_translator.\
            search_attributions_enseignant = lambda **kwargs: {attribution_autre_unite_enseignement}

        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_utilisateur_aucune_attribution(self):
        aucune_attribution = set()
        self.attribution_translator.search_attributions_enseignant = lambda **kwargs: aucune_attribution

        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_date_de_remise_est_hier(self):
        note_etudiant_a_remettre_au_plus_tard_hier = NoteManquanteEtudiantFactory(date_remise_hier=True)
        self.repository.save(note_etudiant_a_remettre_au_plus_tard_hier)

        cmd = self._generate_command_from_note_etudiant(note_etudiant_a_remettre_au_plus_tard_hier)

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, DateEcheanceNoteAtteinteException().message)

    def test_should_autoriser_si_date_de_remise_est_aujourdhui(self):
        note_etudiant_a_remettre_au_plus_tard_aujourdhui = NoteManquanteEtudiantFactory(date_remise_aujourdhui=True)
        self.repository.save(note_etudiant_a_remettre_au_plus_tard_aujourdhui)

        cmd = self._generate_command_from_note_etudiant(note_etudiant_a_remettre_au_plus_tard_aujourdhui)

        self.assertTrue(
            self.message_bus.invoke(cmd),
            """Si la date de remise est aujourd'hui, l'encodage de la note est autorisée jusqu'à aujourd'hui 23h59"""
        )

    def test_should_empecher_si_email_correspond_pas_noma(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant="email@ne_corespond_pas.be",
                    note="12"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NomaNeCorrespondPasEmailException().message)

    def test_should_ignore_when_noma_ne_dispose_pas_de_note_etudiant(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant="9999999999",
                    email_etudiant=self.note.email,
                    note="12"
                )
            ]
        )

        result = self.message_bus.invoke(cmd)
        self.assertEqual(result, [])

    def test_should_empecher_si_note_inferieure_0(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="-1"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteIncorrecteException(note_incorrecte='-1').message)

    def test_should_encoder_note_de_presence(self):
        note_de_presence = "0"
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note=note_de_presence
                )
            ]
        )
        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(0.0))

    def test_should_empecher_si_note_superieure_20(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="21"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteIncorrecteException(note_incorrecte='21').message)

    def test_should_encoder_20(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="20"
                )
            ]
        )
        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(20.0))

    def test_should_empecher_si_note_pas_lettre_autorisee(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="S"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteIncorrecteException(note_incorrecte='S').message)

    def test_should_empecher_si_note_mal_formatee(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="T 12"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteIncorrecteException(note_incorrecte='T 12').message)

    def test_should_empecher_si_note_decimale_non_autorisee(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note="12.5"
                )
            ]
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteDecimaleNonAutoriseeException().message)

    def test_should_encoder_si_note_decimale_autorisee(self):
        note_etudiant = NoteDecimalesAuthorisees()
        self.repository.save(note_etudiant)

        cmd = attr.evolve(self._generate_command_from_note_etudiant(note_etudiant, note="12.5"))

        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(12.5))

    def test_should_empecher_si_note_deja_soumise(self):
        note_etudiant = NoteDejaSoumise()
        self.repository.save(note_etudiant)

        cmd = self._generate_command_from_note_etudiant(note_etudiant)

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        exception = class_exceptions.exception.exceptions.pop()
        self.assertIsInstance(exception, EncoderNotesEtudiantEnLotLigneBusinessExceptions)
        self.assertEqual(exception.message, NoteDejaSoumiseException().message)

    def test_should_encoder_absence_injustifiee_as_A(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note='A'
                )
            ]
        )

        entity_id = self.message_bus.invoke(cmd)[0]

        expected_result = Justification(value=JustificationTypes.ABSENCE_UNJUSTIFIED)
        self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_encoder_absence_injustifiee_as_ABSENCE_UNJUSTIFIED(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note=JustificationTypes.ABSENCE_UNJUSTIFIED.name
                )
            ]
        )

        entity_id = self.message_bus.invoke(cmd)[0]

        expected_result = Justification(value=JustificationTypes.ABSENCE_UNJUSTIFIED)
        self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_encoder_tricherie_as_T(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note='T'
                )
            ]
        )

        entity_id = self.message_bus.invoke(cmd)[0]

        expected_result = Justification(value=JustificationTypes.CHEATING)
        self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_encoder_tricherie_as_CHEATING(self):
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note=JustificationTypes.CHEATING.name
                )
            ]
        )
        entity_id = self.message_bus.invoke(cmd)[0]

        expected_result = Justification(value=JustificationTypes.CHEATING)
        self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_pas_persister_car_pas_de_modification(self):
        self.assertEqual(self.repository.get(self.note.entity_id).note.value, "")
        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=self.note.noma,
                    email_etudiant=self.note.email,
                    note=""
                )
            ]
        )

        results = self.message_bus.invoke(cmd)
        self.assertEqual(len(results), 0)
        self.assertEqual(self.repository.get(self.note.entity_id).note.value, "")

    def test_should_historiser_encodage(self):
        self.message_bus.invoke(self.cmd)
        self.assertEqual(len(self.historiser_notes_service.appels), 1)

    def test_should_ajouter_notes_enregistree_dans_rapport(self):
        self.message_bus.invoke(self.cmd)

        rapport = self.rapport_repository.get(IdentiteEncoderNotesRapport(transaction_id=self.cmd.transaction_id))

        notes_enregistrees = rapport.get_notes_enregistrees()
        self.assertEqual(len(notes_enregistrees), 1)
        self.assertEqual(notes_enregistrees[0].noma, self.note.noma)
        self.assertEqual(notes_enregistrees[0].code_unite_enseignement, self.note.code_unite_enseignement)
        self.assertEqual(notes_enregistrees[0].numero_session, self.note.entity_id.numero_session)
        self.assertEqual(notes_enregistrees[0].annee_academique, self.note.entity_id.annee_academique)

    def test_should_ajouter_notes_non_enregistree_dans_rapport(self):
        note1 = NoteManquanteEtudiantFactory()
        self.repository.save(note1)

        note2 = NoteManquanteEtudiantFactory()
        self.repository.save(note2)

        cmd = attr.evolve(
            self.cmd,
            notes=[
                EncoderNoteCommand(  # Email ne correspond pas au noma
                    noma_etudiant=note1.noma,
                    email_etudiant="email@ne_correspond_pas.be",
                    note="19",
                ),
                EncoderNoteCommand(  # Note inchangee
                    noma_etudiant=note2.noma,
                    email_etudiant=note2.email,
                    note="",
                ),
            ]
        )

        with contextlib.suppress(MultipleBusinessExceptions):
            self.message_bus.invoke(cmd)

        rapport = self.rapport_repository.get(IdentiteEncoderNotesRapport(transaction_id=cmd.transaction_id))

        self.assertEqual(len(rapport.get_notes_enregistrees()), 0)

        notes_non_enregistrees = rapport.get_notes_non_enregistrees()
        self.assertEqual(len(notes_non_enregistrees), 1)
        self.assertEqual(notes_non_enregistrees[0].noma, note1.noma)
        self.assertEqual(notes_non_enregistrees[0].code_unite_enseignement, note1.code_unite_enseignement)
        self.assertEqual(notes_non_enregistrees[0].numero_session, note1.entity_id.numero_session)
        self.assertEqual(notes_non_enregistrees[0].annee_academique, note1.entity_id.annee_academique)
        self.assertEqual(notes_non_enregistrees[0].cause, str(NomaNeCorrespondPasEmailException().message))

    def _generate_command_from_note_etudiant(self, note_etudiant: 'NoteEtudiant', note=None):
        return EncoderNotesEtudiantCommand(
            code_unite_enseignement=note_etudiant.code_unite_enseignement,
            annee_unite_enseignement=note_etudiant.annee,
            numero_session=note_etudiant.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes=[
                EncoderNoteCommand(
                    noma_etudiant=note_etudiant.noma,
                    email_etudiant=note_etudiant.email,
                    note=note or "12"
                )
            ]
        )
