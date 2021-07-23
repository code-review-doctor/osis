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
from datetime import date

import attr
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import SoumettreFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PeriodeSoumissionNotesFermeeException, \
    PasResponsableDeNotesException
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, DateDTO
from ddd.logic.encodage_des_notes.soumission.use_case.write.soumettre_feuille_de_notes_service import \
    soumettre_feuille_de_notes
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecNotesEncodees, \
    FeuilleDeNotesAvecNotesManquantes
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import \
    ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.soumission.domain.service.periode_soumission_notes import \
    PeriodeSoumissionNotesTranslator
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository


class SoumettreFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.responsable_notes = ResponsableDeNotesLDROI1001Annee2020Factory()
        self.responsables_notes_repo = ResponsableDeNotesInMemoryRepository()
        self.responsables_notes_repo.save(self.responsable_notes)
        self.matricule_enseignant = self.responsable_notes.matricule_fgs_enseignant

        self.feuille_de_notes = FeuilleDeNotesAvecNotesEncodees(
            entity_id__code_unite_enseignement='LDROI1001',
        )
        self.feuille_notes_repo = FeuilleDeNotesInMemoryRepository()
        self.feuille_notes_repo.save(self.feuille_de_notes)

        self.cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=self.feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=self.feuille_de_notes.annee,
            numero_session=self.feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )

        self.periode_soumission_ouverte = PeriodeSoumissionNotesDTO(
            annee_concernee=self.feuille_de_notes.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=DateDTO(jour=1, mois=1, annee=date.today().year),
            fin_periode_soumission=DateDTO(jour=31, mois=12, annee=date.today().year),
        )
        self.periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        self.periode_soumission_translator.get = lambda *args: self.periode_soumission_ouverte

    def test_should_pas_soumettre_si_note_manquante(self):
        feuille_notes_repo = FeuilleDeNotesInMemoryRepository()
        feuille_de_notes = FeuilleDeNotesAvecNotesManquantes(
            entity_id__code_unite_enseignement='LDROI1001',
        )
        feuille_notes_repo.save(feuille_de_notes)
        cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes.annee,
            numero_session=feuille_de_notes.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )
        soumettre_feuille_de_notes(
            cmd,
            feuille_notes_repo,
            self.responsables_notes_repo,
            self.periode_soumission_translator,
        )
        feuille_de_notes_apres_soumettre = feuille_notes_repo.get(feuille_de_notes.entity_id)
        for note in feuille_de_notes_apres_soumettre.notes:
            self.assertFalse(note.est_soumise)

    def test_should_empecher_si_periode_soumission_fermee(self):
        date_dans_le_passe = DateDTO(jour=1, mois=1, annee=1950)
        periode_fermee = attr.evolve(
            self.periode_soumission_ouverte,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        periode_soumission_translator.get = lambda *args: periode_fermee
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            soumettre_feuille_de_notes(
                self.cmd,
                self.feuille_notes_repo,
                self.responsables_notes_repo,
                periode_soumission_translator,
            )

    def test_should_empecher_si_acune_periode_soumission_trouvee(self):
        aucune_periode_trouvee = None
        periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        periode_soumission_translator.get = lambda *args: aucune_periode_trouvee
        with self.assertRaises(PeriodeSoumissionNotesFermeeException):
            soumettre_feuille_de_notes(
                self.cmd,
                self.feuille_notes_repo,
                self.responsables_notes_repo,
                periode_soumission_translator,
            )

    def test_should_empecher_si_responsable_de_notes_aucune_unite_enseignement(self):
        matricule_non_responsable = "99999999"
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant=matricule_non_responsable)
        with self.assertRaises(PasResponsableDeNotesException):
            soumettre_feuille_de_notes(
                cmd,
                self.feuille_notes_repo,
                self.responsables_notes_repo,
                self.periode_soumission_translator,
            )

    def test_should_empecher_si_pas_responsable_de_notes_unite_enseignement(self):
        feuille_de_notes_sans_responsable = FeuilleDeNotesAvecNotesEncodees()
        cmd = SoumettreFeuilleDeNotesCommand(
            code_unite_enseignement=feuille_de_notes_sans_responsable.code_unite_enseignement,
            annee_unite_enseignement=feuille_de_notes_sans_responsable.annee,
            numero_session=feuille_de_notes_sans_responsable.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )
        with self.assertRaises(PasResponsableDeNotesException):
            soumettre_feuille_de_notes(
                cmd,
                self.feuille_notes_repo,
                self.responsables_notes_repo,
                self.periode_soumission_translator,
            )

    def test_should_soumettre_plusieurs_notes(self):
        soumettre_feuille_de_notes(
            self.cmd,
            self.feuille_notes_repo,
            self.responsables_notes_repo,
            self.periode_soumission_translator,
        )
        feuille_de_notes_apres_soumettre = self.feuille_notes_repo.get(self.feuille_de_notes.entity_id)
        for note in feuille_de_notes_apres_soumettre.notes:
            self.assertTrue(note.est_soumise)
