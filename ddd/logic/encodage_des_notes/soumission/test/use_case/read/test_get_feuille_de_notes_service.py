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

from django.test import SimpleTestCase

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO, InscriptionExamenDTO, EnseignantDTO, \
    AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_feuille_de_notes_service import get_feuille_de_notes
from ddd.logic.encodage_des_notes.tests.factory._note_etudiant import NoteManquanteEtudiantFactory
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecUneSeuleNoteManquante
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.periode_soumission_notes import \
    PeriodeSoumissionNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.unite_enseignement import \
    UniteEnseignementTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository


class GetFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.noma = '11111111'
        self.sigle_formation = 'DROI1BA'

        self.feuille_de_notes = FeuilleDeNotesAvecUneSeuleNoteManquante(
            notes={
                NoteManquanteEtudiantFactory(entity_id__noma=self.noma)
            }
        )
        self.repository = FeuilleDeNotesInMemoryRepository()
        self.repository.save(self.feuille_de_notes)

        self.resp_notes_repository = ResponsableDeNotesInMemoryRepository()

        self.cmd = GetFeuilleDeNotesCommand(
            code_unite_enseignement=self.code_unite_enseignement,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )

        self.periode_soumission_translator = PeriodeSoumissionNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.inscr_examen_translator = InscriptionExamenTranslatorInMemory()
        self.signaletique_translator = SignaletiqueEtudiantTranslatorInMemory()
        self.unite_enseignement_trans = UniteEnseignementTranslatorInMemory()

    def test_should_renvoyer_responsable_de_notes(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        self.assertEqual(result.responsable_note.nom, 'Chileng')
        self.assertEqual(result.responsable_note.prenom, 'Jean-Michel')

    def test_should_ignorer_responsable_notes_dans_autre_enseigants(self):
        attribution_translator = AttributionEnseignantTranslatorInMemory()
        responsable_notes = AttributionEnseignantDTO(
            code_unite_enseignement=self.code_unite_enseignement,
            annee=self.annee,
            nom="Chileng",  # Responsable de notes
            prenom="Jean-Michel"  # Responsable de notes
        )
        attribution_translator.search_attributions_enseignant = lambda *args, **kwargs: {responsable_notes}
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        self.assertEqual(result.autres_enseignants, list())

    def test_should_renvoyer_unite_enseignement(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        self.assertEqual(result.code_unite_enseignement, self.code_unite_enseignement)
        self.assertEqual(result.intitule_complet_unite_enseignement, "Intitule complet unite enseignement")

    def test_should_renvoyer_autres_enseignants_ordonnes(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        resultat_ordonne = [
            EnseignantDTO(nom="Jolypas", prenom="Michelle"),
            EnseignantDTO(nom="Smith", prenom="Charles"),
        ]
        self.assertListEqual(resultat_ordonne, result.autres_enseignants)

    def test_should_renvoyer_signaletique_etudiant(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        note_etudiant = result.notes_etudiants[0]
        self.assertEqual(note_etudiant.noma, self.noma)
        self.assertEqual(note_etudiant.nom, "Dupont")
        self.assertEqual(note_etudiant.prenom, "Marie")
        self.assertEqual(note_etudiant.peps.type_peps, PepsTypes.ARRANGEMENT_JURY.name)
        self.assertEqual(note_etudiant.peps.tiers_temps, True)
        self.assertEqual(note_etudiant.peps.copie_adaptee, True)
        self.assertEqual(note_etudiant.peps.local_specifique, True)
        self.assertEqual(note_etudiant.peps.autre_amenagement, True)
        self.assertEqual(note_etudiant.peps.details_autre_amenagement, "Details autre aménagement")
        self.assertEqual(note_etudiant.peps.accompagnateur, "Accompagnateur")

    def test_should_renvoyer_numero_de_session_et_annee(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        self.assertEqual(result.annee_academique, self.annee)
        self.assertEqual(result.numero_session, self.numero_session)

    def test_should_renvoyer_inscrit_tardivement(self):
        periode_ouverte = self.periode_soumission_translator.get()
        date_apres_ouverture = periode_ouverte.debut_periode_soumission.to_date() + datetime.timedelta(days=1)
        inscr_exam_translator = InscriptionExamenTranslatorInMemory()
        inscrit_tardivement = InscriptionExamenDTO(
            annee=self.annee,
            noma=self.noma,
            code_unite_enseignement=self.code_unite_enseignement,
            sigle_formation=self.sigle_formation,
            date_inscription=DateDTO(
                jour=date_apres_ouverture.day,
                mois=date_apres_ouverture.month,
                annee=date_apres_ouverture.year,
            ),
        )
        inscr_exam_translator.search_inscrits = lambda *args, **kwargs: {inscrit_tardivement}
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=inscr_exam_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        note_etudiant = result.notes_etudiants[0]
        self.assertTrue(note_etudiant.inscrit_tardivement)

    def test_should_renvoyer_desinscrit_tardivement(self):
        periode_ouverte = self.periode_soumission_translator.get()
        date_apres_ouverture = periode_ouverte.debut_periode_soumission.to_date() + datetime.timedelta(days=1)
        inscr_exam_translator = InscriptionExamenTranslatorInMemory()
        desinscrit_tardivement = InscriptionExamenDTO(
            annee=self.annee,
            noma=self.noma,
            code_unite_enseignement=self.code_unite_enseignement,
            sigle_formation=self.sigle_formation,
            date_inscription=DateDTO(
                jour=date_apres_ouverture.day,
                mois=date_apres_ouverture.month,
                annee=date_apres_ouverture.year,
            ),
        )
        inscr_exam_translator.search_inscrits = lambda *args, **kwargs: set()
        inscr_exam_translator.search_desinscrits = lambda *args, **kwargs: {desinscrit_tardivement}
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=inscr_exam_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        note_etudiant = result.notes_etudiants[0]
        self.assertTrue(note_etudiant.desinscrit_tardivement)

    def test_should_renvoyer_note_est_soumise(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        note_etudiant = result.notes_etudiants[0]
        self.assertFalse(note_etudiant.est_soumise)

    def test_should_renvoyer_valeur_note(self):
        result = get_feuille_de_notes(
            self.cmd,
            feuille_de_note_repo=self.repository,
            responsable_notes_repo=self.resp_notes_repository,
            periode_soumission_note_translator=self.periode_soumission_translator,
            inscription_examen_translator=self.inscr_examen_translator,
            signaletique_etudiant_translator=self.signaletique_translator,
            attribution_translator=self.attribution_translator,
            unite_enseignement_translator=self.unite_enseignement_trans,
        )
        note_etudiant = result.notes_etudiants[0]
        expected_result = ""
        self.assertEqual(expected_result, note_etudiant.note)
