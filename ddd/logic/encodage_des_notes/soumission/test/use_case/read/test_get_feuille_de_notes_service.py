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
from unittest import mock

from django.test import SimpleTestCase

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, EnseignantDTO, PeriodeEncodageNotesDTO, AdresseDTO
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import PeriodeEncodageNotesFermeeException
from ddd.logic.encodage_des_notes.soumission.dtos import InscriptionExamenDTO, AttributionEnseignantDTO
from ddd.logic.encodage_des_notes.soumission.test.factory import NoteManquanteEtudiantFactory
from ddd.logic.encodage_des_notes.soumission.test.factory.responsable_de_notes import ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.unite_enseignement import \
    UniteEnseignementTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.note_etudiant import \
    NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class GetFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.noma = '11111111'
        self.nom_cohorte = 'DROI1BA'

        self.note_etudiant = NoteManquanteEtudiantFactory(entity_id__noma=self.noma)

        self.repository = NoteEtudiantInMemoryRepository()
        self.repository.entities.clear()
        self.repository.save(self.note_etudiant)

        self.resp_notes_repository = ResponsableDeNotesInMemoryRepository()
        self.responsable_notes = ResponsableDeNotesLDROI1001Annee2020Factory(
            entity_id__matricule_fgs_enseignant=self.matricule_enseignant
        )
        self.resp_notes_repository.save(self.responsable_notes)

        self.cmd = GetFeuilleDeNotesCommand(
            code_unite_enseignement=self.code_unite_enseignement,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )

        self.periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.inscr_examen_translator = InscriptionExamenTranslatorInMemory()
        self.signaletique_etudiant_translator = SignaletiqueEtudiantTranslatorInMemory()
        self.signaletique_personne_translator = SignaletiquePersonneTranslatorInMemory()
        self.unite_enseignement_trans = UniteEnseignementTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            NoteEtudiantRepository=lambda: self.repository,
            ResponsableDeNotesRepository=lambda: self.resp_notes_repository,
            SignaletiquePersonneTranslator=lambda: self.signaletique_personne_translator,
            PeriodeEncodageNotesTranslator=lambda: self.periode_soumission_translator,
            InscriptionExamenTranslator=lambda: self.inscr_examen_translator,
            SignaletiqueEtudiantTranslator=lambda: self.signaletique_etudiant_translator,
            AttributionEnseignantTranslator=lambda: self.attribution_translator,
            UniteEnseignementTranslator=lambda: self.unite_enseignement_trans,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    @mock.patch("infrastructure.messages_bus.PeriodeEncodageNotesTranslator")
    def test_should_empecher_si_periode_fermee_depuis_hier(self, mock_periode_translator):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeEncodageNotesDTO(
            annee_concernee=self.annee,
            session_concernee=self.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        periode_soumission_translator = PeriodeEncodageNotesTranslatorInMemory()
        periode_soumission_translator.get = lambda *args: periode_fermee
        mock_periode_translator.return_value = periode_soumission_translator

        with self.assertRaises(PeriodeEncodageNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_renvoyer_responsable_de_notes(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.responsable_note.nom, 'Chileng')
        self.assertEqual(result.responsable_note.prenom, 'Jean-Michel')

    @mock.patch("infrastructure.messages_bus.AttributionEnseignantTranslator")
    def test_should_ignorer_responsable_notes_dans_autres_enseignants(self, mock_attrib_translator):
        attribution_translator = AttributionEnseignantTranslatorInMemory()
        responsable_notes = AttributionEnseignantDTO(
            matricule_fgs_enseignant=self.matricule_enseignant,
            code_unite_enseignement=self.code_unite_enseignement,
            annee=self.annee,
            nom="Chileng",  # Responsable de notes
            prenom="Jean-Michel"  # Responsable de notes
        )
        attribution_translator.search_attributions_enseignant = lambda *args, **kwargs: {responsable_notes}
        mock_attrib_translator.return_value = attribution_translator
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.autres_enseignants, list())

    def test_should_renvoyer_unite_enseignement(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.code_unite_enseignement, self.code_unite_enseignement)
        self.assertEqual(result.intitule_complet_unite_enseignement, "Intitule complet unite enseignement")

    def test_should_renvoyer_autres_enseignants_ordonnes(self):
        result = self.message_bus.invoke(self.cmd)
        resultat_ordonne = [
            EnseignantDTO(nom="Jolypas", prenom="Michelle"),
            EnseignantDTO(nom="Smith", prenom="Charles"),
        ]
        self.assertListEqual(resultat_ordonne, result.autres_enseignants)

    def test_should_renvoyer_signaletique_etudiant(self):
        result = self.message_bus.invoke(self.cmd)
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
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.annee_academique, self.annee)
        self.assertEqual(result.numero_session, self.numero_session)

    @mock.patch("infrastructure.messages_bus.InscriptionExamenTranslator")
    def test_should_renvoyer_inscrit_tardivement(self, mock_inscr_exam):
        periode_ouverte = self.periode_soumission_translator.get()
        date_apres_ouverture = periode_ouverte.debut_periode_soumission.to_date() + datetime.timedelta(days=1)
        inscr_exam_translator = InscriptionExamenTranslatorInMemory()
        inscrit_tardivement = InscriptionExamenDTO(
            annee=self.annee,
            noma=self.noma,
            code_unite_enseignement=self.code_unite_enseignement,
            nom_cohorte=self.nom_cohorte,
            date_inscription=DateDTO(
                jour=date_apres_ouverture.day,
                mois=date_apres_ouverture.month,
                annee=date_apres_ouverture.year,
            ),
        )
        inscr_exam_translator.search_inscrits = lambda *args, **kwargs: {inscrit_tardivement}
        mock_inscr_exam.return_value = inscr_exam_translator
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertTrue(note_etudiant.inscrit_tardivement)

    @mock.patch("infrastructure.messages_bus.InscriptionExamenTranslator")
    def test_should_renvoyer_desinscrit_tardivement(self, mock_inscr_exam):
        periode_ouverte = self.periode_soumission_translator.get()
        date_apres_ouverture = periode_ouverte.debut_periode_soumission.to_date() + datetime.timedelta(days=1)
        inscr_exam_translator = InscriptionExamenTranslatorInMemory()
        desinscrit_tardivement = InscriptionExamenDTO(
            annee=self.annee,
            noma=self.noma,
            code_unite_enseignement=self.code_unite_enseignement,
            nom_cohorte=self.nom_cohorte,
            date_inscription=DateDTO(
                jour=date_apres_ouverture.day,
                mois=date_apres_ouverture.month,
                annee=date_apres_ouverture.year,
            ),
        )
        inscr_exam_translator.search_inscrits = lambda *args, **kwargs: set()
        inscr_exam_translator.search_desinscrits = lambda *args, **kwargs: {desinscrit_tardivement}
        mock_inscr_exam.return_value = inscr_exam_translator
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertTrue(note_etudiant.desinscrit_tardivement)

    def test_should_renvoyer_note_est_soumise(self):
        result = message_bus_instance.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        self.assertFalse(note_etudiant.est_soumise)

    def test_should_renvoyer_valeur_note(self):
        result = self.message_bus.invoke(self.cmd)
        note_etudiant = result.notes_etudiants[0]
        expected_result = ""
        self.assertEqual(expected_result, note_etudiant.note)

    def test_should_renvoyer_liste_des_notes_ordonee_par_nom_de_cohorte_nom_prenom(self):
        self.repository.delete(self.note_etudiant.entity_id)

        self.repository.save(NoteManquanteEtudiantFactory(entity_id__noma=self.noma))
        self.repository.save(NoteManquanteEtudiantFactory(entity_id__noma='99999999'))

        result = message_bus_instance.invoke(self.cmd)
        self.assertEqual(len(result.notes_etudiants), 2)

        self.assertEqual(result.notes_etudiants[0].nom, 'Arogan')
        self.assertEqual(result.notes_etudiants[0].prenom, 'Adrien')
        self.assertEqual(result.notes_etudiants[1].nom, 'Dupont')
        self.assertEqual(result.notes_etudiants[1].prenom, 'Marie')

    def test_should_renvoyer_contact_responsable_notes(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(result.contact_responsable_notes.matricule_fgs, self.matricule_enseignant)
        self.assertEqual(result.contact_responsable_notes.email, "charles.smith@email.com")
        expected_address = AdresseDTO(
            code_postal='1410',
            ville='Waterloo',
            rue_numero_boite='Rue de Waterloo, 123',
        )
        self.assertEqual(result.contact_responsable_notes.adresse_professionnelle, expected_address)

    def test_should_renvoyer_aucun_contact_responsable_notes(self):
        self.resp_notes_repository.delete(self.responsable_notes.entity_id)
        result = self.message_bus.invoke(self.cmd)
        self.assertIsNone(result.contact_responsable_notes)
        self.resp_notes_repository.save(self.responsable_notes)
