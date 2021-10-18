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
from django.test import TestCase

from base.tests.factories.cohort_year import CohortYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_builder import \
    AdresseFeuilleDeNotesBuilder
from ddd.logic.encodage_des_notes.soumission.builder.adresse_feuille_de_notes_identity_builder import \
    AdresseFeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesSpecifiqueFactory, \
    PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory, AdresseFeuilleDeNotesBaseeSurEntiteFactory
from infrastructure.encodage_de_notes.soumission.repository.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesRepository
from reference.tests.factories.country import CountryFactory
from testing.assertions import assert_attrs_instances_are_equal


class TestAdresseFeuilleDeNotesRepository(TestCase):
    def setUp(self) -> None:
        self.repository = AdresseFeuilleDeNotesRepository()

    def test_should_save_adresse_feuille_de_notes(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        assert_attrs_instances_are_equal(
            adresse,
            self.repository.get(adresse.entity_id)
        )

    def test_should_get_adresse_feuille_de_notes_de_1ba_si_non_definie_pour_11ba(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse, with_cohort_year=True)

        self.repository.save(adresse)

        entity_11ba = AdresseFeuilleDeNotesIdentityBuilder().build_from_nom_cohorte(
            adresse.nom_cohorte.replace('1BA', "11BA")
        )

        self.assertTrue(self.repository.get(entity_11ba))

    def test_should_get_adresse_feuille_de_notes_sur_base_de_entite_si_definie(self):
        adresse = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        assert_attrs_instances_are_equal(
            adresse,
            self.repository.get(adresse.entity_id)
        )

    def test_should_save_adresse_feuille_de_notes_pour_premiere_annee_de_bachelier(self):
        adresse = PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        assert_attrs_instances_are_equal(
            adresse,
            self.repository.get(adresse.entity_id)
        )

    def test_should_update_adresse_feuille_de_notes(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        adresse.destinataire = "Nouveau destinataire"
        self.repository.save(adresse)

        assert_attrs_instances_are_equal(
            adresse,
            self.repository.get(adresse.entity_id)
        )

    def test_should_delete_adresse_feuille_de_notes(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        self.assertTrue(self.repository.get(adresse.entity_id))

        self.repository.delete(adresse.entity_id)

        with self.assertRaises(IndexError):
            self.repository.get(adresse.entity_id)

    def test_should_delete_adresse_feuille_de_notes_pour_premiere_annee_de_bachelier(self):
        adresse = PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)

        self.repository.save(adresse)

        self.assertTrue(self.repository.get(adresse.entity_id))

        self.repository.delete(adresse.entity_id)

        with self.assertRaises(IndexError):
            self.repository.get(adresse.entity_id)

    def test_should_search_adresse_feuille_de_notes(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        adresse_premiere_annee_bachelier = PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)
        self._create_necessary_data(adresse_premiere_annee_bachelier)

        self.repository.save(adresse)
        self.repository.save(adresse_premiere_annee_bachelier)

        self.assertListEqual(
            self.repository.search([adresse.entity_id]),
            [adresse]
        )

    def test_should_search_dtos(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        adresse_premiere_annee_bachelier = PremiereAnneeBachelierAdresseFeuilleDeNotesSpecifiqueFactory()
        self._create_necessary_data(adresse)
        self._create_necessary_data(adresse_premiere_annee_bachelier)

        self.repository.save(adresse)
        self.repository.save(adresse_premiere_annee_bachelier)

        result = AdresseFeuilleDeNotesBuilder().build_from_repository_dto(
            self.repository.search_dtos([adresse.entity_id])[0]
        )
        assert_attrs_instances_are_equal(result, adresse)

    def _create_necessary_data(self, adresse: 'AdresseFeuilleDeNotes', with_cohort_year: bool = False):
        if "11BA" in adresse.nom_cohorte:
            CohortYearFactory(
                education_group_year__acronym=adresse.nom_cohorte.replace('11BA', '1BA'),
                education_group_year__academic_year__current=True,
                first_year_bachelor=True
            )
        else:
            egy = EducationGroupYearFactory(acronym=adresse.nom_cohorte, academic_year__current=True)
            if with_cohort_year:
                CohortYearFactory(education_group_year=egy, first_year_bachelor=True)

        CountryFactory(name=adresse.pays)
        if adresse.entite:
            egy.administration_entity.location = adresse.rue_numero
            egy.administration_entity.postal_code = adresse.code_postal
            egy.administration_entity.city = adresse.ville
            egy.administration_entity.country = CountryFactory(name=adresse.pays)
            egy.administration_entity.phone = adresse.telephone
            egy.administration_entity.fax = adresse.fax
            egy.administration_entity.save()

            EntityVersionFactory(
                entity=egy.administration_entity,
                acronym=adresse.destinataire.split(' - ')[0],
                title=adresse.destinataire.split(' - ')[1],
            )
