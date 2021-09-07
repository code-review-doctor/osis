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
from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNotesCommand, EncoderNoteCommand
from ddd.logic.encodage_des_notes.encodage.domain.model._note import Justification, NoteChiffree
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.validator.exceptions import NoteIncorrecteException
from ddd.logic.encodage_des_notes.encodage.dtos import CohorteGestionnaireDTO
from ddd.logic.encodage_des_notes.encodage.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteDecimalesAuthorisees
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import DateEcheanceNoteAtteinteException, \
    NomaNeCorrespondPasEmailException, NoteDecimaleNonAutoriseeException, PeriodeEncodageNotesFermeeException
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasGestionnaireParcoursException, \
    PasGestionnaireParcoursCohorteException
from infrastructure.encodage_de_notes.encodage.domain.service.in_memory.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireInMemory
from infrastructure.encodage_de_notes.encodage.domain.service.in_memory.notifier_encodage_notes import NotifierEncodageNotesInMemory
from infrastructure.encodage_de_notes.encodage.repository.in_memory.note_etudiant import NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.messages_bus import message_bus_instance


class EncoderNoteTest(SimpleTestCase):

    def setUp(self) -> None:
        self.matricule_gestionnaire = '22220000'

        self.note = NoteManquanteEtudiantFactory()
        self.repository = NoteEtudiantInMemoryRepository()
        self.repository.save(self.note)

        self.cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.matricule_gestionnaire,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=self.note.noma,
                    email=self.note.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="19",
                )
            ],
        )

        self.periode_encodage_notes_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.cohortes_gestionnaire_trans = CohortesDuGestionnaireInMemory()
        self.notifier_notes_domain_service = NotifierEncodageNotesInMemory()
        self.notifier_notes_domain_service.notifications.clear()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            NoteEtudiantGestionnaireRepository=lambda: self.repository,
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_notes_translator,
            CohortesDuGestionnaireTranslator=lambda: self.cohortes_gestionnaire_trans,
            NotifierNotes=lambda: self.notifier_notes_domain_service,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_empecher_si_periode_fermee_depuis_hier(self):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeEncodageNotesDTO(
            annee_concernee=self.note.annee_academique,
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
            annee_concernee=self.note.annee_academique,
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
            annee_concernee=self.note.annee_academique,
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

    def test_should_empecher_si_utilisateur_non_gestionnaire(self):
        self.cohortes_gestionnaire_trans.search = lambda *args, **kwargs: set()

        with self.assertRaises(PasGestionnaireParcoursException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_utilisateur_pas_gestionnaire_cohorte_etudiant(self):
        cohorte_gestionnaire = CohorteGestionnaireDTO(
            matricule_gestionnaire=self.matricule_gestionnaire,
            nom_cohorte="AUTRECOHORTE",
        )
        self.cohortes_gestionnaire_trans.search = lambda *args, **kwargs: {cohorte_gestionnaire}

        with self.assertRaises(PasGestionnaireParcoursCohorteException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_date_de_remise_est_hier(self):
        note_etudiant_a_remettre_au_plus_tard_hier = NoteManquanteEtudiantFactory(date_remise_hier=True)
        self.repository.save(note_etudiant_a_remettre_au_plus_tard_hier)

        cmd = self._generate_command_from_note_etudiant(note_etudiant_a_remettre_au_plus_tard_hier)

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DateEcheanceNoteAtteinteException
        )

    def test_should_autoriser_si_date_de_remise_est_aujourdhui(self):
        note_etudiant_a_remettre_au_plus_tard_aujourdhui = NoteManquanteEtudiantFactory(date_remise_aujourdhui=True)
        self.repository.save(note_etudiant_a_remettre_au_plus_tard_aujourdhui)

        cmd = self._generate_command_from_note_etudiant(note_etudiant_a_remettre_au_plus_tard_aujourdhui)

        self.assertTrue(
            self.message_bus.invoke(cmd),
            """Si la date de remise est aujourd'hui, l'encodage de la note est autorisée jusqu'à aujourd'hui 23h59"""
        )

    def test_should_empecher_si_email_correspond_pas_noma(self):
        cmd = self._evolve_command(email="email@ne_correspond_pas.be")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NomaNeCorrespondPasEmailException
        )

    def test_should_ignorer_noma_non_inscrit_examen(self):
        noma_non_insct_examen = '99999999'
        cmd = self._evolve_command(noma=noma_non_insct_examen)

        self.assertEqual(
            list(),
            self.message_bus.invoke(cmd),
            "Si aucun etudiant n'est trouvé, aucune exception n'est lancée",
        )

    def test_should_empecher_si_note_inferieure_0(self):
        cmd = self._evolve_command(note="-1")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_encoder_note_de_presence(self):
        note_de_presence = "0"
        cmd = self._evolve_command(note=note_de_presence)

        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(0.0))

    def test_should_empecher_si_note_superieure_20(self):
        cmd = self._evolve_command(note="21")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_encoder_20(self):
        note_de_presence = "20"
        cmd = self._evolve_command(note=note_de_presence)

        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(20.0))

    def test_should_empecher_si_note_pas_lettre_autorisee(self):
        cmd = self._evolve_command(note="S")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_mal_formatee(self):
        cmd = self._evolve_command(note="T 12")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_decimale_non_autorisee(self):
        cmd = self._evolve_command(note="12.5")

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteDecimaleNonAutoriseeException
        )

    def test_should_encoder_si_note_decimale_autorisee(self):
        note_etudiant = NoteDecimalesAuthorisees(entity_id=self.note.entity_id)
        self.repository.save(note_etudiant)

        cmd = self._evolve_command(note="12.5", email=note_etudiant.email)

        entity_id = self.message_bus.invoke(cmd)[0]
        self.assertEqual(self.repository.get(entity_id).note.value, Decimal(12.5))

    def test_should_encoder_absence_injustifiee(self):
        for absence_injustifiee in ['A', JustificationTypes.ABSENCE_UNJUSTIFIED.name]:
            with self.subTest(absence=absence_injustifiee):
                cmd = self._evolve_command(note=absence_injustifiee)

                entity_id = self.message_bus.invoke(cmd)[0]

                expected_result = Justification(value=JustificationTypes.ABSENCE_UNJUSTIFIED)
                self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_encoder_absence_justifiee(self):
        for absence_justifiee in ['M', JustificationTypes.ABSENCE_JUSTIFIED.name]:
            with self.subTest(absence=absence_justifiee):
                cmd = self._evolve_command(note=absence_justifiee)

                entity_id = self.message_bus.invoke(cmd)[0]

                expected_result = Justification(value=JustificationTypes.ABSENCE_JUSTIFIED)
                self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_encoder_tricherie(self):
        for tricherie in ['T', JustificationTypes.CHEATING.name]:
            with self.subTest(tricherie=tricherie):
                cmd = self._evolve_command(note=tricherie)

                entity_id = self.message_bus.invoke(cmd)[0]

                expected_result = Justification(value=JustificationTypes.CHEATING)
                self.assertEqual(self.repository.get(entity_id).note, expected_result)

    def test_should_notifier(self):
        result = self.message_bus.invoke(self.cmd)

        notification_kwargs = self.notifier_notes_domain_service.notifications[0]
        self.assertEqual(notification_kwargs['notes_encodees'], result)

    def test_should_afficher_rapport_plusieurs_notes_erreurs(self):
        note1 = NoteManquanteEtudiantFactory()
        self.repository.save(note1)
        note2 = NoteManquanteEtudiantFactory()
        self.repository.save(note2)
        note3 = NoteManquanteEtudiantFactory()
        self.repository.save(note3)
        cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.matricule_gestionnaire,
            notes_encodees=[
                EncoderNoteCommand(  # Note incorrecte
                    noma=note1.noma,
                    email=note1.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="valeur note incorrecte",
                ),
                EncoderNoteCommand(  # email ne correspond pas au noma
                    noma=note2.noma,
                    email="email@ne_correspond_pas.be",
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="20",
                ),
                EncoderNoteCommand(  # note valide
                    noma=self.note.noma,
                    email=self.note.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="7",
                ),
                EncoderNoteCommand(  # note incorrecte
                    noma=note3.noma,
                    email=note3.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="valeur note incorrecte",
                ),
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)
        exceptions = class_exceptions.exception.exceptions
        self.assertIsInstance(exceptions, list, "Doit être une liste afin de préserver l'ordre des erreurs")
        self.assertEqual(len(exceptions), 3)  # 3 notes sur 4 en erreur

        # Doit renvoyer une liste ordonnée des erreurs rencontrées pour chaque note
        self.assertIsInstance(class_exceptions.exception.exceptions.pop(), NoteIncorrecteException)
        self.assertIsInstance(class_exceptions.exception.exceptions.pop(), NomaNeCorrespondPasEmailException)
        self.assertIsInstance(class_exceptions.exception.exceptions.pop(), NoteIncorrecteException)

    @mock.patch("infrastructure.messages_bus.NoteEtudiantGestionnaireRepository")
    def test_should_sauvegarder_note_meme_si_autre_note_en_erreur(self, mock_note_repo):
        appels_save = []
        fake_repo = NoteEtudiantInMemoryRepository()
        fake_repo.save = lambda *args, **kwargs: appels_save.append(1)
        mock_note_repo.return_value = fake_repo
        note = NoteManquanteEtudiantFactory()
        self.repository.save(note)
        cmd = EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.matricule_gestionnaire,
            notes_encodees=[
                EncoderNoteCommand(  # Note incorrecte
                    noma=note.noma,
                    email=note.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="valeur note incorrecte",
                ),
                EncoderNoteCommand(  # note valide
                    noma=self.note.noma,
                    email=self.note.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note="7",
                ),
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            self.message_bus.invoke(cmd)

        self.assertIsInstance(class_exceptions.exception.exceptions.pop(), NoteIncorrecteException)

        self.assertEqual(
            len(appels_save),
            1,
            "Meme en cas d'erreur sur certaines notes, les notes valides doivent être persistées. "
            "Dans notre cas de test ici, 1 note valide == 1 appel à repository.save()",
        )

    def _generate_command_from_note_etudiant(self, note_etudiant: 'NoteEtudiant'):
        return EncoderNotesCommand(
            matricule_fgs_gestionnaire=self.matricule_gestionnaire,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=note_etudiant.noma,
                    email=note_etudiant.email,
                    code_unite_enseignement=note_etudiant.code_unite_enseignement,
                    note="19",
                )
            ],
        )

    def _evolve_command(self, noma=None, email=None, note=None):
        return attr.evolve(
            self.cmd,
            notes_encodees=[
                EncoderNoteCommand(
                    noma=noma or self.note.noma,
                    email=email or self.note.email,
                    code_unite_enseignement=self.note.code_unite_enseignement,
                    note=note or "19",
                )
            ],
        )
