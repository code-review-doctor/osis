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

from attribution.models.attribution_new import AttributionNew
from ddd.logic.effective_class_repartition.commands import SearchTutorsDistributedToClassCommand
from ddd.logic.encodage_des_notes.shared_kernel.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO


class AttributionEnseignantTranslator(IAttributionEnseignantTranslator):

    @classmethod
    def search_attributions_enseignant(
            cls,
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        dtos = _search_attributions_unite_enseignement(code_unite_enseignement=code_unite_enseignement, annee=annee)
        dtos |= _search_repartition_classes(code_unite_enseignement=code_unite_enseignement, annee=annee)
        return dtos

    @classmethod
    def search_attributions_enseignant_par_matricule(
            cls,
            annee: int,
            matricule_enseignant: str,
    ) -> Set['AttributionEnseignantDTO']:
        dtos = _search_attributions_unite_enseignement(annee=annee, matricule_enseignant=matricule_enseignant)
        dtos |= _search_repartition_classes(annee=annee, matricule_enseignant=matricule_enseignant)
        return dtos


def _search_attributions_unite_enseignement(
        code_unite_enseignement: str = None,
        annee: int = None,
        matricule_enseignant: str = None,
) -> Set['AttributionEnseignantDTO']:
    qs = AttributionNew.objects
    if code_unite_enseignement:
        qs = qs.filter(
            learning_container_year__academic_year__year=annee,
            learning_container_year__acronym=code_unite_enseignement,
        )
    if matricule_enseignant:
        qs = qs.filter(
            tutor__person__global_id=matricule_enseignant,
        )
    qs = qs.annotate(
        matricule_fgs_enseignant=F('tutor__person__global_id'),
        code_unite_enseignement=F('learning_container_year__acronym'),
        nom=F('tutor__person__last_name'),
        prenom=F('tutor__person__first_name'),
        annee=F('learning_container_year__academic_year__year'),
    ).values(
        'matricule_fgs_enseignant',
        'code_unite_enseignement',
        'annee',
        'nom',
        'prenom',
    ).distinct()
    return {
        AttributionEnseignantDTO(
            matricule_fgs_enseignant=attribution_as_dict['matricule_fgs_enseignant'],
            code_unite_enseignement=attribution_as_dict['code_unite_enseignement'],
            annee=attribution_as_dict['annee'],
            prenom=attribution_as_dict['prenom'],
            nom=attribution_as_dict['nom'],
        )
        for attribution_as_dict in qs
    }


def _search_repartition_classes(
        code_unite_enseignement: str = None,
        annee: int = None,
) -> Set['AttributionEnseignantDTO']:
    code_unite_enseignement = code_unite_enseignement[:-1]
    code_classe = code_unite_enseignement[-1]
    cmd = SearchTutorsDistributedToClassCommand(
        learning_unit_code=code_unite_enseignement,
        learning_unit_year=annee,
        class_code=code_classe,
    )
    from infrastructure.messages_bus import message_bus_instance
    dtos = message_bus_instance.invoke(cmd)
    return {
        AttributionEnseignantDTO(
            matricule_fgs_enseignant=dto.personal_id_number,
            code_unite_enseignement=dto.complete_class_code,
            annee=dto.annee,
            nom=dto.last_name,
            prenom=dto.first_name,
        ) for dto in dtos
    }
