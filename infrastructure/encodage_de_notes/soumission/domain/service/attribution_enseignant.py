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
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        dtos = _search_attributions_unite_enseignement(code_unite_enseignement, annee)
        dtos |= _search_repartition_classes(code_unite_enseignement, annee)
        return dtos


def _search_attributions_unite_enseignement(
        code_unite_enseignement: str,
        annee: int
) -> Set['AttributionEnseignantDTO']:
    attributions_unite_enseignement = AttributionNew.objects.filter(
        learning_container_year__academic_year__year=annee,
        learning_container_year__acronym=code_unite_enseignement,
    ).annotate(
        matricule_fgs_enseignant=F('tutor__person__global_id'),
        code_unite_enseignement=F('learning_container_year__acronym'),
        nom=F('tutor__person__last_name'),
        prenom=F('tutor__person__first_name'),
    ).values(
        'matricule_fgs_enseignant',
        'code_unite_enseignement',
        'nom',
        'prenom',
    ).distinct()
    return {
        AttributionEnseignantDTO(
            matricule_fgs_enseignant=attribution_as_dict['matricule_fgs_enseignant'],
            code_unite_enseignement=attribution_as_dict['code_unite_enseignement'],
            annee=annee,
            prenom=attribution_as_dict['prenom'],
            nom=attribution_as_dict['nom'],
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
        nom=F('attribution_charge__attribution__tutor__person__last_name'),
        prenom=F('attribution_charge__attribution__tutor__person__first_name'),
    ).values(
        'learning_unit_code',
        'class_code',
        'nom',
        'prenom',
    ).distinct()
    dtos = set()
    for class_repartition_as_dict in classes_repartition:
        code_classe = class_repartition_as_dict['class_code']
        code_unite_enseignement = class_repartition_as_dict['code_unite_enseignement'] + code_classe
        dto = AttributionEnseignantDTO(
            code_unite_enseignement=code_unite_enseignement,
            annee=annee,
            prenom=class_repartition_as_dict['prenom'],
            nom=class_repartition_as_dict['nom'],
        )
        dtos.add(dto)
    return dtos
