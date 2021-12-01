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

from assessments.models.enums.score_sheet_address_choices import ScoreSheetAddressEntityType
from ddd.logic.encodage_des_notes.soumission.commands import GetAdresseFeuilleDeNotesServiceCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import EntitesCohorteDTO
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesSpecifiqueFactory, \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory, AdresseFeuilleDeNotesVideFactory
from ddd.logic.shared_kernel.entite.tests.factory.entiteucl import EPLEntiteFactory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.entites_cohorte import \
    EntitesCohorteTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance
from infrastructure.shared_kernel.academic_year.repository.in_memory.academic_year import AcademicYearInMemoryRepository
from infrastructure.shared_kernel.entite.repository.in_memory.entiteucl import EntiteUCLInMemoryRepository


class TestGetAdresseFeuilleDeNotesService(SimpleTestCase):
    def setUp(self) -> None:
        self.repository = AdresseFeuilleDeNotesInMemoryRepository()
        self.addCleanup(self.repository.reset)

        self.cmd = GetAdresseFeuilleDeNotesServiceCommand(
            nom_cohorte="SINF1BA"
        )
        self.periode_encodage_notes_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.academic_year_repository = AcademicYearInMemoryRepository()

        self.entite_repository = EntiteUCLInMemoryRepository()
        self.epl_entite = EPLEntiteFactory()
        self.entite_repository.entities.append(EPLEntiteFactory())

        self.entites_cohorte_translator = EntitesCohorteTranslatorInMemory()
        self.entites_cohorte_translator.datas.append(
            EntitesCohorteDTO(
                administration=self.epl_entite.entity_id,
                gestion=self.epl_entite.entity_id,
            )
        )

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repository,
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_notes_translator,
            AcademicYearRepository=lambda: self.academic_year_repository,
            EntiteUCLRepository=lambda: self.entite_repository,
            EntitesCohorteTranslator=lambda: self.entites_cohorte_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_return_dto(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        cmd = attr.evolve(self.cmd, nom_cohorte=adresse.nom_cohorte)
        self.repository.save(adresse)

        result = message_bus_instance.invoke(cmd)
        self.assert_dto_corresponds_to_adress(
            result,
            adresse,
        )

    def test_should_base_value_on_entity_if_adresse_est_basee_sur_entite(self):
        adresse = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self.repository.save(adresse)

        cmd = attr.evolve(self.cmd, nom_cohorte=adresse.nom_cohorte)

        result = message_bus_instance.invoke(cmd)
        self.assert_dto_corresponds_to_adress(
            result,
            adresse,
        )

    def test_should_retourner_adresse_de_feuille_de_notes_entite_gestion_si_adresse_non_definie_pour_la_cohorte(self):
        cmd = attr.evolve(self.cmd, nom_cohorte="DROI1BA")

        result = message_bus_instance.invoke(cmd)

        expected = AdresseFeuilleDeNotesDTO(
            nom_cohorte=cmd.nom_cohorte,
            annee_academique=2020,
            type_entite=ScoreSheetAddressEntityType.ENTITY_MANAGEMENT.name,
            destinataire="{} - {}".format(self.epl_entite.sigle, self.epl_entite.intitule),
            rue_numero=self.epl_entite.adresse.rue_numero,
            code_postal=self.epl_entite.adresse.code_postal,
            ville=self.epl_entite.adresse.ville,
            pays=self.epl_entite.adresse.pays,
            telephone=self.epl_entite.adresse.telephone,
            fax=self.epl_entite.adresse.fax,
            email=''
        )
        self.assertEqual(result, expected)

    def assert_dto_corresponds_to_adress(
            self,
            dto_obj: AdresseFeuilleDeNotesDTO,
            adresse: AdresseFeuilleDeNotes,
    ):
        self.assertEqual(dto_obj.nom_cohorte, adresse.nom_cohorte)
        self.assertEqual(dto_obj.type_entite, adresse.type_entite.name if adresse.type_entite else "")
        self.assertEqual(dto_obj.destinataire, adresse.destinataire)
        self.assertEqual(dto_obj.rue_numero, adresse.rue_numero)
        self.assertEqual(dto_obj.code_postal, adresse.code_postal)
        self.assertEqual(dto_obj.ville, adresse.ville)
        self.assertEqual(dto_obj.pays, adresse.pays)
        self.assertEqual(dto_obj.telephone, adresse.telephone)
        self.assertEqual(dto_obj.fax, adresse.fax)
        self.assertEqual(dto_obj.email, adresse.email)
