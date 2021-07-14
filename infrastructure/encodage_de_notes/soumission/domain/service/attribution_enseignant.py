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
from typing import Set

from django.db.models import F

from attribution.models.attribution_class import AttributionClass
from attribution.models.attribution_new import AttributionNew
from ddd.logic.encodage_des_notes.soumission.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO


class AttributionEnseignantTranslator(IAttributionEnseignantTranslator):

    @classmethod
    def search_attributions_enseignant(
            cls,
            matricule_fgs_enseignant: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        dtos = _search_attributions_unite_enseignement(matricule_fgs_enseignant, annee)
        dtos |= _search_repartition_classes(matricule_fgs_enseignant, annee)
        return dtos


def _search_attributions_unite_enseignement(matricule_fgs: str, annee: int) -> Set['AttributionEnseignantDTO']:
    attributions_unite_enseignement = AttributionNew.objects.filter(
        tutor__person__global_id=matricule_fgs,
        learning_container_year__academic_year__year=annee,
    ).annotate(
        code_unite_enseignement=F('learning_container_year__acronym'),
    ).values().distinct()
    return {
        AttributionEnseignantDTO(
            code_unite_enseignement=attribution_as_dict['code_unite_enseignement'],
            annee=annee,
        )
        for attribution_as_dict in attributions_unite_enseignement
    }


def _search_repartition_classes(matricule_fgs: str, annee: int) -> Set['AttributionEnseignantDTO']:
    # TODO :: réutiliser message_bus et domaine "effective_class_repartition"
    classes_repartition = AttributionClass.objects.filter(
        attribution_charge__attribution__tutor__person__global_id=matricule_fgs,
        learning_class_year__learning_component_year__learning_unit_year__academic_year__year=annee,
    ).annotate(
        learning_unit_code=F('learning_class_year__learning_component_year__learning_unit_year__acronym'),
        class_code=F('learning_class_year__acronym'),
    ).values().distinct()
    dtos = set()
    for class_repartition_as_dict in classes_repartition:
        code_classe = class_repartition_as_dict['class_code']
        code_unite_enseignement = class_repartition_as_dict['code_unite_enseignement'] + code_classe
        dto = AttributionEnseignantDTO(
            code_unite_enseignement=code_unite_enseignement,
            annee=annee,
        )
        dtos.add(dto)
    return dtos
