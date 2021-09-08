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

from assessments.views.serializers.score_sheet_xls import ScoreSheetXLSSerializer
from ddd.logic.encodage_des_notes.shared_kernel.dtos import FeuilleDeNotesDTO, DateDTO, NoteEtudiantDTO, EnseignantDTO,\
    DetailContactDTO
from ddd.logic.encodage_des_notes.soumission.dtos import DonneesAdministrativesFeuilleDeNotesDTO, \
    AdresseFeuilleDeNotesDTO


class ScoreSheetXLSSerializerTest(SimpleTestCase):
    @classmethod
    def setUp(cls) -> None:
        cls.feuille_de_notes = FeuilleDeNotesDTO(
            code_unite_enseignement='LDROI1200',
            intitule_complet_unite_enseignement='Introduction au droit',
            note_decimale_est_autorisee=True,
            responsable_note=EnseignantDTO(nom="Durant", prenom="Thomas"),
            contact_responsable_notes=DetailContactDTO(
                matricule_fgs="987654321",
                email="thomas.durant@email.be",
                adresse_professionnelle=None
            ),
            autres_enseignants=[],
            annee_academique=2021,
            numero_session=2,
            notes_etudiants=[
                NoteEtudiantDTO(
                    code_unite_enseignement='LDROI1200',
                    annee_unite_enseignement=2021,
                    intitule_complet_unite_enseignement='Introduction au droit',
                    est_soumise=False,
                    date_remise_de_notes=DateDTO.build_from_date(datetime.date.today() - datetime.timedelta(days=1)),
                    nom_cohorte='DROI2M',
                    noma='999999999',
                    nom='Helios',
                    prenom='Jean',
                    peps=None,
                    email='dummy@gmail.com',
                    note=10,
                    inscrit_tardivement=False,
                    desinscrit_tardivement=False,
                ),
                NoteEtudiantDTO(
                    code_unite_enseignement='LDROI1200',
                    annee_unite_enseignement=2021,
                    intitule_complet_unite_enseignement='Introduction au droit',
                    est_soumise=True,
                    date_remise_de_notes=DateDTO.build_from_date(datetime.date.today() + datetime.timedelta(days=5)),
                    nom_cohorte='DROI2M',
                    noma='999999998',
                    nom='Palus',
                    prenom='Pierre',
                    peps=None,
                    email='dummy@gmail.com',
                    note=19,
                    inscrit_tardivement=False,
                    desinscrit_tardivement=False,
                )
            ],
        )

        cls.donnees_administrative = DonneesAdministrativesFeuilleDeNotesDTO(
            sigle_formation='DROI2M',
            code_unite_enseignement='LDROI1200',
            date_deliberation=DateDTO.build_from_date(datetime.date.today() + datetime.timedelta(days=10)),
            contact_feuille_de_notes=AdresseFeuilleDeNotesDTO(
                nom_cohorte='DROI2M',
                entite="",
                destinataire='Durant Thomas',
                rue_numero='Chemin de lasne',
                code_postal=1200,
                ville="Bruxelles",
                pays="Belgique",
                telephone='',
                fax='',
                email='',
            ),
        )

        cls.instance = {
            'feuille_de_notes': cls.feuille_de_notes,
            'donnees_administratives': [cls.donnees_administrative]
        }

    def test_assert_rows_filtered_by_score_which_deadline_is_not_reached(self):
        sheet_serialized = ScoreSheetXLSSerializer(instance=self.instance).data

        self.assertEqual(len(sheet_serialized['rows']), 1)

    def test_assert_keys_exists(self):
        sheet_serialized = ScoreSheetXLSSerializer(instance=self.instance).data

        self.assertTrue("numero_session" in sheet_serialized)
        self.assertTrue("titre" in sheet_serialized)
        self.assertTrue("code_unite_enseignement" in sheet_serialized)
        self.assertTrue("annee_academique" in sheet_serialized)
        self.assertTrue("note_decimale_est_autorisee" in sheet_serialized)
        self.assertTrue("rows" in sheet_serialized)

        self.assertTrue("noma" in sheet_serialized['rows'][0])
        self.assertTrue("nom" in sheet_serialized['rows'][0])
        self.assertTrue("prenom" in sheet_serialized['rows'][0])
        self.assertTrue("note" in sheet_serialized['rows'][0])
        self.assertTrue("nom_cohorte" in sheet_serialized['rows'][0])
        self.assertTrue("email" in sheet_serialized['rows'][0])
        self.assertTrue("date_remise_de_notes" in sheet_serialized['rows'][0])
        self.assertTrue("est_soumise" in sheet_serialized['rows'][0])
        self.assertTrue("inscrit_tardivement" in sheet_serialized['rows'][0])
        self.assertTrue("desinscrit_tardivement" in sheet_serialized['rows'][0])
        self.assertTrue("type_peps" in sheet_serialized['rows'][0])
        self.assertTrue("tiers_temps" in sheet_serialized['rows'][0])
        self.assertTrue("copie_adaptee" in sheet_serialized['rows'][0])
        self.assertTrue("local_specifique" in sheet_serialized['rows'][0])
        self.assertTrue("autre_amenagement" in sheet_serialized['rows'][0])
        self.assertTrue("details_autre_amenagement" in sheet_serialized['rows'][0])
        self.assertTrue("accompagnateur" in sheet_serialized['rows'][0])
        self.assertTrue("enrollment_state_color" in sheet_serialized['rows'][0])
