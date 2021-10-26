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
import attr
import mock
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseFeuilleDeNotesSpecifique
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance
from infrastructure.shared_kernel.academic_year.repository.in_memory.academic_year import AcademicYearInMemoryRepository


class TestEncoderAddressFeuilleDeNotesSpecifique(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = EncoderAdresseFeuilleDeNotesSpecifique(
            nom_cohorte="SINF1BA",
            destinataire="Destination",
            rue_numero="Rue de l'Empereur",
            code_postal="1452",
            ville="",
            pays="",
            telephone="",
            fax="",
            email="temp@temp.com",
        )

        self.repo = AdresseFeuilleDeNotesInMemoryRepository()
        self.repo.entities.clear()

        self.periode_encodage_notes_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.academic_year_repository = AcademicYearInMemoryRepository()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repo,
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_notes_translator,
            AcademicYearRepository=lambda: self.academic_year_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_encoder_valeurs_de_la_commande_pour_adresse(self):
        result = message_bus_instance.invoke(self.cmd)

        adresse_sauvegardee = self.repo.get(result)

        self.assertEqual(adresse_sauvegardee.nom_cohorte, self.cmd.nom_cohorte)
        self.assertEqual(adresse_sauvegardee.destinataire, self.cmd.destinataire)
        self.assertEqual(adresse_sauvegardee.rue_numero, self.cmd.rue_numero)
        self.assertEqual(adresse_sauvegardee.code_postal, self.cmd.code_postal)
        self.assertEqual(adresse_sauvegardee.ville, self.cmd.ville)
        self.assertEqual(adresse_sauvegardee.pays, self.cmd.pays)
        self.assertEqual(adresse_sauvegardee.telephone, self.cmd.telephone)
        self.assertEqual(adresse_sauvegardee.fax, self.cmd.fax)
        self.assertEqual(adresse_sauvegardee.email, self.cmd.email)
        self.assertEqual(adresse_sauvegardee.type_entite, None)

    def test_should_raise_exception_if_encoded_address_of_first_year_bachelor_is_the_same_as_bachelor(self):
        adresse_bachelier = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self.repo.save(adresse_bachelier)

        cmd = attr.evolve(
            self.cmd,
            nom_cohorte=adresse_bachelier.nom_cohorte.replace('1BA', '11BA'),
            email=adresse_bachelier.email,
            destinataire=adresse_bachelier.destinataire,
            rue_numero=adresse_bachelier.rue_numero,
            code_postal=adresse_bachelier.code_postal,
            ville=adresse_bachelier.ville,
            pays=adresse_bachelier.pays,
            telephone=adresse_bachelier.telephone,
            fax=adresse_bachelier.fax
        )

        with self.assertRaises(AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException):
            message_bus_instance.invoke(cmd)
