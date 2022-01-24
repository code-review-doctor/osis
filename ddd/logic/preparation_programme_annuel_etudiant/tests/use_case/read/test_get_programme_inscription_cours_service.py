##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import mock

from django.test import SimpleTestCase

from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.domain.service.in_memory.catalogue_formations import \
    CatalogueFormationsTranslator
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours \
    import GroupementAjusteInscriptionCoursRepository


class GetProgrammeInscriptionCoursTest(SimpleTestCase):

    def setUp(self) -> None:
        self.catalogue_formation_translator = CatalogueFormationsTranslator()
        self.groupement_ajustes_repository = GroupementAjusteInscriptionCoursRepository()
        self._mock_message_bus()

    def _mock_message_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            CatalogueFormationsTranslator=lambda: self.catalogue_formation_translator,
            GroupementAjusteInscriptionCoursRepository=lambda: self.groupement_ajustes_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance
