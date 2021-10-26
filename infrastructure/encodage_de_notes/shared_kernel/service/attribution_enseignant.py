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
import functools
import operator
from typing import Set, List

from django.db.models import F, Q

from attribution.models.attribution_new import AttributionNew
from ddd.logic.effective_class_repartition.commands import SearchTutorsDistributedToClassCommand, \
    SearchAttributionsToLearningUnitCommand, SearchClassesEnseignantCommand, SearchAttributionsEnseignantCommand, \
    SearchClassesParNomEnseignantCommand
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_attribution_enseignant import \
    IAttributionEnseignantTranslator
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO


class AttributionEnseignantTranslator(IAttributionEnseignantTranslator):

    @classmethod
    def search_attributions_enseignant(
            cls,
            code_unite_enseignement: str,
            annee: int,
    ) -> Set['AttributionEnseignantDTO']:
        unites_enseignement_dtos = _search_attributions_unite_enseignement(
            code_unite_enseignement=code_unite_enseignement,
            annee=annee,
        )
        classes_dtos = _search_repartition_classes(code_unite_enseignement=code_unite_enseignement, annee=annee)
        return unites_enseignement_dtos or classes_dtos

    @classmethod
    def search_attributions_enseignant_par_nom_prenom_annee(
            cls,
            annee: int,
            nom_prenom: str,
    ) -> Set['AttributionEnseignantDTO']:
        attributions_unites_enseignement = _search_attributions_unite_enseignement_par_nom_prenom(annee, nom_prenom)
        repartitions_classes = _search_repartitions_classes_par_nom_prenom(annee, nom_prenom)
        return attributions_unites_enseignement | repartitions_classes

    @classmethod
    def search_attributions_enseignant_par_matricule(
            cls,
            annee: int,
            matricule_enseignant: str,
    ) -> Set['AttributionEnseignantDTO']:
        dtos = _search_attributions_unite_enseignement(annee=annee, matricule_enseignant=matricule_enseignant)
        dtos |= _search_repartition_classes(annee=annee, matricule_enseignant=matricule_enseignant)
        return dtos

    @classmethod
    def search_enseignants_par_nom_prenom_annee(
            cls,
            annee: int,
            nom_prenom: str
    ) -> List['EnseignantDTO']:
        attributions = cls.search_attributions_enseignant_par_nom_prenom_annee(annee, nom_prenom)
        enseignants = {EnseignantDTO(nom=attrib.nom, prenom=attrib.prenom) for attrib in attributions}
        return list(
            sorted(
                enseignants,
                key=lambda ens: ens.nom + ens.prenom
            )
        )


def _search_attributions_unite_enseignement(
        annee: int,
        code_unite_enseignement: str = None,
        matricule_enseignant: str = None,
) -> Set['AttributionEnseignantDTO']:
    if matricule_enseignant:
        cmd = SearchAttributionsEnseignantCommand(matricule_fgs_enseignant=matricule_enseignant, annee=annee)
    else:
        cmd = SearchAttributionsToLearningUnitCommand(
            learning_unit_code=code_unite_enseignement,
            learning_unit_year=annee,
        )
    from infrastructure.messages_bus import message_bus_instance
    dtos = message_bus_instance.invoke(cmd)
    return {
        AttributionEnseignantDTO(
            matricule_fgs_enseignant=dto.personal_id_number,
            code_unite_enseignement=dto.learning_unit_code,
            annee=dto.learning_unit_year,
            nom=dto.last_name,
            prenom=dto.first_name,
        ) for dto in dtos
    }


def _search_repartition_classes(
        annee: int,
        code_unite_enseignement: str = None,
        matricule_enseignant: str = None,
) -> Set['AttributionEnseignantDTO']:
    if matricule_enseignant:
        cmd = SearchClassesEnseignantCommand(matricule_fgs_enseignant=matricule_enseignant, annee=annee)
    else:
        code_classe = code_unite_enseignement[-1]
        code_sans_lettre_classe = code_unite_enseignement.replace('_', '').replace('-', '')[:-1]
        cmd = SearchTutorsDistributedToClassCommand(
            learning_unit_code=code_sans_lettre_classe,
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


def _search_repartitions_classes_par_nom_prenom(annee, nom_prenom):
    from infrastructure.messages_bus import message_bus_instance
    cmd = SearchClassesParNomEnseignantCommand(annee=annee, nom_prenom=nom_prenom)
    return {
        AttributionEnseignantDTO(
            nom=obj.last_name,
            prenom=obj.first_name,
            annee=annee,
            matricule_fgs_enseignant=obj.personal_id_number,
            code_unite_enseignement=obj.complete_class_code,
        )
        for obj in message_bus_instance.invoke(cmd)
    }


def _search_attributions_unite_enseignement_par_nom_prenom(annee, nom_prenom):
    filters = [
        Q(tutor__person__first_name__icontains=mot)
        | Q(tutor__person__last_name__icontains=mot)
        for mot in nom_prenom.split(' ')
    ]
    qs_attributions_cours = AttributionNew.objects.filter(
        learning_container_year__academic_year__year=annee,
    ).filter(
        functools.reduce(
            operator.and_,
            filters
        )
    ).annotate(
        nom=F('tutor__person__last_name'),
        prenom=F('tutor__person__first_name'),
        matricule_fgs_enseignant=F('tutor__person__global_id'),
        code_unite_enseignement=F('learning_container_year__acronym'),
    ).values(
        'nom',
        'prenom',
        'code_unite_enseignement',
        'matricule_fgs_enseignant',
    ).distinct().order_by('nom', 'prenom')
    return {
        AttributionEnseignantDTO(
            nom=obj['nom'],
            prenom=obj['prenom'],
            annee=annee,
            matricule_fgs_enseignant=obj['matricule_fgs_enseignant'],
            code_unite_enseignement=obj['code_unite_enseignement'],
        )
        for obj in qs_attributions_cours
    }
