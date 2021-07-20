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

from django.test import SimpleTestCase

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, DateDTO, AttributionEnseignantDTO, \
    InscriptionExamenDTO, DesinscriptionExamenDTO, SignaletiqueEtudiantDTO, EtudiantPepsDTO, UniteEnseignementDTO
from ddd.logic.encodage_des_notes.soumission.use_case.read.get_feuille_de_notes_service import get_feuille_de_notes
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecNotesEncodees
from infrastructure.encodage_de_notes.soumission.domain.service.attribution_enseignant import \
    AttributionEnseignantTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.inscription_examen import InscriptionExamenTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.periode_soumission_notes import \
    PeriodeSoumissionNotesTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.signaletique_etudiant import \
    SignaletiqueEtudiantTranslator
from infrastructure.encodage_de_notes.soumission.domain.service.unite_enseignement import UniteEnseignementTranslator
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository


class GetFeuilleDeNotesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.matricule_enseignant = '00321234'

        self.feuille_de_notes = FeuilleDeNotesAvecNotesEncodees()
        self.repository = FeuilleDeNotesInMemoryRepository()
        self.repository.save(self.feuille_de_notes)

        self.resp_notes_repository = ResponsableDeNotesInMemoryRepository()

        self.code_unite_enseignement = self.feuille_de_notes.code_unite_enseignement
        self.cmd = GetFeuilleDeNotesCommand(
            code_unite_enseignement=self.code_unite_enseignement,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )

        self.annee = self.feuille_de_notes.annee
        self.periode_soumission_ouverte = PeriodeSoumissionNotesDTO(
            annee_concernee=self.annee,
            session_concernee=self.feuille_de_notes.numero_session,
            debut_periode_soumission=DateDTO(jour=1, mois=1, annee=date.today().year),
            fin_periode_soumission=DateDTO(jour=31, mois=12, annee=date.today().year),
        )
        self.periode_soumission_translator = PeriodeSoumissionNotesTranslator()
        self.periode_soumission_translator.get = lambda *args: self.periode_soumission_ouverte

        self.attribution_dto = AttributionEnseignantDTO(  # TODO :: Utiliser InMemoryDomainService + réutiliser dans autres tests
            code_unite_enseignement=self.code_unite_enseignement,
            annee=self.annee,
            nom="Smith",
            prenom="Charles",
        )
        self.attribution_translator = AttributionEnseignantTranslator()
        self.attribution_translator.search_attributions_enseignant = lambda *args, **kwargs: {self.attribution_dto}

        self.sigle_formation = 'DROI1BA'
        notes_etudiants = list(self.feuille_de_notes.notes)
        premier_etudiant = notes_etudiants[0]
        self.inscription_examen_dto = InscriptionExamenDTO(
            annee=self.annee,
            noma=premier_etudiant.noma,
            code_unite_enseignement=self.code_unite_enseignement,
            sigle_formation=self.sigle_formation,
            date_inscription=DateDTO(
                jour=1,
                mois=1,
                annee=2020,
            ),
        )
        self.inscr_examen_translator = InscriptionExamenTranslator()
        self.inscr_examen_translator.search_inscrits = lambda *args, **kwargs: {self.inscription_examen_dto}
        self.desiscription_examen_dto = DesinscriptionExamenDTO(
            annee=self.annee,
            noma=notes_etudiants[1].noma,
            code_unite_enseignement=self.code_unite_enseignement,
            sigle_formation=self.sigle_formation,
        )
        self.inscr_examen_translator.search_desinscrits = lambda *args, **kwargs: {self.inscription_examen_dto}

        self.signaletique_etudiant_dto = SignaletiqueEtudiantDTO(
            noma=premier_etudiant.noma,
            nom="Dupont",
            prenom="Marie",
            peps=EtudiantPepsDTO(
                type_peps=PepsTypes.ARRANGEMENT_JURY.name,
                tiers_temps=True,
                copie_adaptee=True,
                local_specifique=True,
                autre_amenagement=True,
                details_autre_amenagement="details_autre_amenagement",
                accompagnateur="Accompagnateur",
            ),
        )
        self.signaletique_translator = SignaletiqueEtudiantTranslator()
        self.signaletique_translator.search = lambda *args, **kwargs: {self.signaletique_etudiant_dto}

        self.unite_esneignement_dto = UniteEnseignementDTO(
            annee=self.annee,
            code=self.code_unite_enseignement,
            intitule_complet="Intitule complet unite enseignement",
        )
        self.unite_enseignement_trans = UniteEnseignementTranslator()
        self.unite_enseignement_trans.get = lambda *args, **kwargs: self.unite_esneignement_dto

    # def test_should_aggreger_donnees(self):
    #     result = get_feuille_de_notes(
    #         self.cmd,
    #         feuille_de_note_repo=self.repository,
    #         responsable_notes_repo=self.resp_notes_repository,
    #         periode_soumission_note_translator=self.periode_soumission_translator,
    #         inscription_examen_translator=self.inscr_examen_translator,
    #         signaletique_etudiant_translator=self.signaletique_translator,
    #         attribution_translator=self.attribution_translator,
    #         unite_enseignement_translator=self.unite_enseignement_trans,
    #     )
    #     expected_result =

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
        self.assertEqual(result.responsable_note.nom, 'Smith')
        self.assertEqual(result.responsable_note.prenom, 'Charles')

    def test_should_renvoyer_unite_enseignement(self):
        pass

    def test_should_renvoyer_autres_enseignants(self):
        pass

    def test_should_renvoyer_signaletique_etudiant(self):
        pass

    def test_should_renvoyer_numero_de_session_et_annee(self):
        pass

    def test_should_renvoyer_inscrit_tardivement(self):
        pass

    def test_should_renvoyer_desinscrit_tardivement(self):
        pass

    def test_should_renvoyer_note_est_soumise(self):
        pass

    def test_should_renvoyer_valeur_note(self):
        pass

