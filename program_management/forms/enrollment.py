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
from django import forms

from ddd.logic.preparation_programme_annuel_etudiant.dtos import GroupementCatalogueDTO, \
    UniteEnseignementCatalogueDTO, ProgrammeDetailleDTO, FormulaireInscriptionCoursDTO
from program_management.forms.education_groups import STANDARD


class DefaultEnrollmentForm(forms.Form):
    title = forms.CharField()
    code = forms.CharField()
    academic_year = forms.CharField()
    program = None

    def __init__(
            self,
            *args,
            year: int,
            acronym: str,
            version_name: str,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        formation_dto = self._get_formation_dto(year, acronym, version_name)
        self.fields['code'].initial = "{}{}".format(
            formation_dto.sigle_formation,
            formation_dto.version_formation if formation_dto.version_formation != STANDARD else ''
        )
        self.fields['title'].initial = formation_dto.intitule_complet_formation
        self.fields['academic_year'].initial = "{}-{}".format(year, str(year + 1)[-2:])
        self.program = formation_dto.programme

    def _get_formation_dto(self, year: int, acronym: str, version_name: str) -> FormulaireInscriptionCoursDTO:
        # TODO : recupérer objet DTO réel
        # cmd = GetFormulaireInscriptionCoursCommand(
        #     annee_formation=year,
        #     sigle_formation=acronym,
        #     version_formation=version_name
        # )
        # return message_bus_instance.invoke(cmd)
        groupement1 = GroupementCatalogueDTO(
            inclus_dans=None,
            intitule='Content:',
            obligatoire=True,
            remarque='Remarque 1',
            commentaire=None

        )
        groupement1_1 = GroupementCatalogueDTO(
            inclus_dans=groupement1,
            intitule='Groupement 1 1',
            obligatoire=True,
            remarque='Remarque 1',
            commentaire=None

        )
        groupement1_1_1 = GroupementCatalogueDTO(
            inclus_dans=groupement1_1,
            intitule='Groupement 1 1 1',
            obligatoire=True,
            remarque='Remarque 1',
            commentaire=None

        )
        groupement2 = GroupementCatalogueDTO(
            inclus_dans=None,
            intitule='Groupement 2',
            obligatoire=False,
            remarque='Remarque 2',
            commentaire='Commentaire 2'
        )
        ue_0 = UniteEnseignementCatalogueDTO(
            inclus_dans=groupement1,
            bloc=1,
            code='LESPO1113',
            intitule_complet='Sociologie et anthropologie des mondes contemporains',
            quadrimestre='Q1',
            credits_absolus=10,
            volume_annuel_pm=5,
            volume_annuel_pp=5,
        )
        ue_1 = UniteEnseignementCatalogueDTO(
            inclus_dans=groupement1_1,
            bloc=1,
            code='ue1',
            intitule_complet='UE1',
            quadrimestre='Q1',
            credits_absolus=10,
            volume_annuel_pm=5,
            volume_annuel_pp=5,
        )
        ue_2 = UniteEnseignementCatalogueDTO(
            inclus_dans=groupement1_1,
            bloc=1,
            code='ue2',
            intitule_complet='UE2',
            quadrimestre='Q1',
            credits_absolus=10,
            volume_annuel_pm=5,
            volume_annuel_pp=5,
        )
        ue_3 = UniteEnseignementCatalogueDTO(
            inclus_dans=groupement1_1_1,
            bloc=1,
            code='ue3',
            intitule_complet='UE3 ',
            quadrimestre='Q1',
            credits_absolus=10,
            volume_annuel_pm=5,
            volume_annuel_pp=5,
        )
        ue_4 = UniteEnseignementCatalogueDTO(
            inclus_dans=groupement2,
            bloc=1,
            code='ue4',
            intitule_complet='UE4 ',
            quadrimestre='Q1',
            credits_absolus=10,
            volume_annuel_pm=5,
            volume_annuel_pp=5,
        )
        programme_detaille = ProgrammeDetailleDTO(
            unites_enseignement=[ue_0, ue_1, ue_2, ue_3, ue_4],
            groupements=[groupement1, groupement2, groupement1_1, groupement1_1_1]
        )
        formation_dto_simule = FormulaireInscriptionCoursDTO(
            programme=programme_detaille,
            annee_formation=2021,
            sigle_formation='ECGE1BA',
            version_formation='STANDARD',
            intitule_complet_formation='Bachelier en sciences économiques et de gestion',
        )
        return formation_dto_simule
