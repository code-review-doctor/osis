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
import uuid
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.preparation_programme_annuel_etudiant.commands import AnnulerAjustementDAjoutCommand
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    GroupementAjusteInscriptionCours, IdentiteGroupementAjusteInscriptionCours
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement_ajoutee import \
    UniteEnseignementAjoutee, UniteEnseignementAjouteeIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from education_group.ddd.domain.group import GroupIdentity
from infrastructure.messages_bus import message_bus_instance
from infrastructure.preparation_programme_annuel_etudiant.repository.in_memory.groupement_ajuste_inscription_cours \
    import \
    GroupementAjusteInscriptionCoursInMemoryRepository
from program_management.ddd.domain.program_tree_version import STANDARD


class TestAnnulerAjustementDAjoutUE(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2021
        self.code_programme = 'LECGE100B'
        self.code_groupement = 'LECGE100T'
        self.code_unite_enseignement = 'LESPO2236'

        self.version_formation = STANDARD
        self.transition_formation = ''
        ue_ajoutee = GroupementAjusteInscriptionCours(
                    entity_id=IdentiteGroupementAjusteInscriptionCours(uuid=uuid.uuid4()),
                    groupement_id=GroupIdentity(code=self.code_groupement, year=self.annee),
                    programme_id=GroupIdentity(code=self.code_programme, year=self.annee),
                    unites_enseignement_ajoutees=[
                        UniteEnseignementAjoutee(
                            entity_id=UniteEnseignementAjouteeIdentity(uuid=uuid.uuid4()),
                            unite_enseignement_identity=LearningUnitIdentity(
                                academic_year=AcademicYearIdentity(year=self.annee),
                                code=self.code_unite_enseignement
                            ),
                            a_la_suite_de=None)
                    ],
                    unites_enseignement_supprimees=[],
                    unites_enseignement_modifiees=[],
                )
        self.repository = GroupementAjusteInscriptionCoursInMemoryRepository()
        self.repository.save(ue_ajoutee)

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            GroupementAjusteInscriptionCoursInMemoryRepository=lambda: self.repository,
        )
        message_bus_patcher.start()

        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_annuler_ajustement_ajout_UE(self):
        self.assertEqual(len(self.repository.entities[0].unites_enseignement_ajoutees), 1)
        self.message_bus.invoke(
            AnnulerAjustementDAjoutCommand(
                annee=self.annee,
                code_programme=self.code_programme,
                code_groupement=self.code_groupement,
                code_unite_enseignement=self.code_unite_enseignement,
            )
        )
        self.assertEqual(self.repository.entities[0].unites_enseignement_ajoutees, [])
