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
from datetime import date
from decimal import Decimal

import attr
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.commands import EncoderFeuilleDeNotesCommand, NoteEtudiantCommand
from ddd.logic.encodage_des_notes.soumission.domain.model._note import Justification, NoteChiffree
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException, \
    EnseignantNonAttribueUniteEnseignementException, DateRemiseNoteAtteinteException, NomaNeCorrespondPasEmailException, \
    AucunEtudiantTrouveException, NoteIncorrecteException, NoteDecimaleNonAutoriseeException, NoteDejaSoumiseException
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, DateDTO, AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.use_case.write.encoder_feuille_de_notes_service import \
    encoder_feuille_de_notes
from ddd.logic.encodage_des_notes.tests.factory._note_etudiant import NoteManquanteEtudiantFactory
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import EmptyFeuilleDeNotesFactory, \
    FeuilleDeNotesAvecNotesManquantes, FeuilleDeNotesDecimalesAutorisees
from infrastructure.encodage_de_notes.soumission.domain.service.attribution_enseignant import \
    AttributionEnseignantTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.periode_soumission_notes import \
    PeriodeSoumissionNotesTranslator
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository


class EncoderFeuilleDeNoesTest(SimpleTestCase):

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

        self.periode_soumission_ouverte = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=DateDTO(jour=1, mois=1, annee=date.today().year),
            fin_periode_soumission=DateDTO(jour=31, mois=12, annee=date.today().year),
        )
        self.periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        self.periode_soumission_translator.get = lambda *args: self.periode_soumission_ouverte

        self.attribution_dto = AttributionEnseignantDTO(
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee=self.feuille_de_notes.annee,
        )
        self.attribution_translator = AttributionEnseignantTranslator()
        self.attribution_translator.search_attributions_enseignant = lambda **kwargs: {self.attribution_dto}

    def test_should_empecher_si_periode_fermee(self):
        date_dans_le_passe = DateDTO(jour=1, mois=1, annee=1950)
        periode_fermee = attr.evolve(
            self.periode_soumission_ouverte,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        periode_soumission_translator.get = lambda *args: periode_fermee

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )

    def test_should_empecher_si_aucune_periode_trouvee(self):
        aucune_periode_trouvee = None
        periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        periode_soumission_translator.get = lambda *args: aucune_periode_trouvee

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )

    def test_should_empecher_si_utilisateur_non_attribue_unite_enseignement(self):
        attribution_autre_unite_enseignement = attr.evolve(self.attribution_dto, code_unite_enseignement='LAUTRE1234')
        attribution_translator = AttributionEnseignantTranslator()
        attribution_translator.search_attributions_enseignant = lambda **kwargs: {attribution_autre_unite_enseignement}

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=attribution_translator,
            )

    def test_should_empecher_si_utilisateur_aucune_attribution(self):
        aucune_attribution = set()
        attribution_translator = AttributionEnseignantTranslator()
        attribution_translator.search_attributions_enseignant = lambda **kwargs: aucune_attribution

        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(EnseignantNonAttribueUniteEnseignementException):
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=attribution_translator,
            )

    def test_should_empecher_si_date_de_remise_est_hier(self):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        note_date_limite_depassee = NoteManquanteEtudiantFactory(date_limite_de_remise=hier)
        feuille_de_notes = EmptyFeuilleDeNotesFactory(
            notes={note_date_limite_depassee}
        )
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=note_date_limite_depassee.noma,
                    email=note_date_limite_depassee.email,
                    note='12'
                )
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DateRemiseNoteAtteinteException
        )

    def test_should_empecher_si_date_de_remise_est_aujourdhui(self):
        aujourdhui = datetime.date.today()
        note_date_limite_depassee = NoteManquanteEtudiantFactory(date_limite_de_remise=aujourdhui)
        feuille_de_notes = EmptyFeuilleDeNotesFactory(
            notes={note_date_limite_depassee}
        )
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=note_date_limite_depassee.noma,
                    email=note_date_limite_depassee.email,
                    note='12'
                )
            ],
        )
        self.assertTrue(
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            ),
            """Si la date de remise est aujourd'hui, l'encodage de la note est autorisée jusqu'à aujourd'hui 23h59"""
        )

    def test_should_empecher_si_email_correspond_pas_noma(self):
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email="email@ne_corespond_pas.be", note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NomaNeCorrespondPasEmailException
        )

    def test_should_empecher_si_etudiant_pas_sur_feuille_de_notes(self):
        noma_pas_sur_feuille_de_notes = "9999999999"
        note_etudiant = NoteEtudiantCommand(noma=noma_pas_sur_feuille_de_notes, email=self.note_manquante.email, note='12')
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AucunEtudiantTrouveException
        )

    def test_should_empecher_si_note_inferieure_0(self):
        note_inferieure_0 = "-1"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=note_inferieure_0)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_superieure_20(self):
        note_superieure_20 = "21"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=note_superieure_20)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_pas_lettre_autorisee(self):
        lettre_inexistante = "S"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=lettre_inexistante)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_mal_formatee(self):
        lettre_inexistante = "T 12"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=lettre_inexistante)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            NoteIncorrecteException
        )

    def test_should_empecher_si_note_decimale_non_autorisee(self):
        note_decimale = "12.5"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=note_decimale)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
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
        entity_id = encoder_feuille_de_notes(
            cmd=cmd,
            feuille_de_note_repo=self.repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            attribution_translator=self.attribution_translator,
        )
        self.assertEqual(list(self.repository.get(entity_id).notes)[0].note.value, Decimal(12.5))

    def test_should_empecher_si_note_deja_soumise(self):
        note_est_soumise = NoteManquanteEtudiantFactory(est_soumise=True)
        feuille_de_notes = EmptyFeuilleDeNotesFactory(
            notes={note_est_soumise}
        )
        self.repository.save(feuille_de_notes)
        cmd = EncoderFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            notes_etudiants=[
                NoteEtudiantCommand(
                    noma=note_est_soumise.noma,
                    email=note_est_soumise.email,
                    note='12'
                )
            ],
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            encoder_feuille_de_notes(
                cmd=cmd,
                feuille_de_note_repo=self.repository,
                periode_soumission_note_translator=self.periode_soumission_translator,
                attribution_translator=self.attribution_translator,
            )
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
        entity_id = encoder_feuille_de_notes(
            cmd=cmd,
            feuille_de_note_repo=self.repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            attribution_translator=self.attribution_translator,
        )
        expected_result = NoteChiffree(value=Decimal(12.0))
        for note in self.repository.get(entity_id).notes:
            self.assertEqual(note.note, expected_result)

    def test_should_encoder_absence_injustifiee(self):
        absence_injustifiee = "A"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=absence_injustifiee)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        entity_id = encoder_feuille_de_notes(
            cmd=cmd,
            feuille_de_note_repo=self.repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            attribution_translator=self.attribution_translator,
        )
        expected_result = Justification(value='A')
        self.assertEqual(list(self.repository.get(entity_id).notes)[0].note, expected_result)

    def test_should_encoder_tricherie(self):
        absence_injustifiee = "T"
        note_etudiant = NoteEtudiantCommand(noma=self.note_manquante.noma, email=self.note_manquante.email, note=absence_injustifiee)
        cmd = attr.evolve(self.cmd, notes_etudiants=[note_etudiant])
        entity_id = encoder_feuille_de_notes(
            cmd=cmd,
            feuille_de_note_repo=self.repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            attribution_translator=self.attribution_translator,
        )
        expected_result = Justification(value='T')
        self.assertEqual(list(self.repository.get(entity_id).notes)[0].note, expected_result)

    def test_should_aggreger_erreurs_plusieurs_notes(self):
        raise NotImplementedError
