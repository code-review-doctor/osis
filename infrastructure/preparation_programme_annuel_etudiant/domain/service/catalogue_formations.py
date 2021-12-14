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
from decimal import Decimal

from django.utils.datastructures import OrderedSet

from base.models.enums.constraint_type import ConstraintTypeEnum

from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, GroupementCatalogueDTO, \
    ProgrammeDetailleDTO, UniteEnseignementCatalogueDTO
from program_management.ddd.command import GetProgramTreeVersionCommand
from program_management.ddd.domain.link import LinkIdentity
from program_management import formatter
from django.utils.translation import gettext_lazy as _


class CatalogueFormationsTranslator(ICatalogueFormationsTranslator):
    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str, transition_name: str) -> 'FormationDTO':
        from infrastructure.messages_bus import message_bus_instance
        program_tree_version = message_bus_instance.invoke(GetProgramTreeVersionCommand(
            year=annee,
            acronym=sigle,
            version_name=version,
            transition_name=transition_name
        ))
        tree = program_tree_version.get_tree()
        groupements = OrderedSet()
        ues = OrderedSet()
        parents_par_niveau = {}
        noeud_parents_par_niveau = {0: tree.root_node}
        tous_liens = tree.get_all_links()
        for path, child_node in tree.root_node.descendents:
            level = len(path.split("|")) - 1
            noeud_parent = noeud_parents_par_niveau.get(level - 1)
            lien = cls._get_lien(child_node, noeud_parent, tous_liens)

            if child_node.is_learning_unit():
                ue = UniteEnseignementCatalogueDTO(
                    inclus_dans=parents_par_niveau.get(level-1),
                    bloc=lien.block if lien else None,
                    code=child_node.code,
                    intitule_complet=child_node.title,
                    quadrimestre=child_node.quadrimester,
                    credits_absolus=child_node.credits,
                    volume_annuel_pm=child_node.volume_total_lecturing,
                    volume_annuel_pp=child_node.volume_total_practical,
                    obligatoire=lien.is_mandatory if lien else False,
                    informations_principales_agregees=_get_detail_lien(lien)
                )
                ues.add(ue)
            else:
                group_inclus_dans = None
                if level != 1:
                    group_inclus_dans = parents_par_niveau.get(level-1)

                ce_group = GroupementCatalogueDTO(
                    inclus_dans=group_inclus_dans,
                    intitule=child_node.title,
                    remarque=child_node.remark_fr,
                    obligatoire=lien.is_mandatory if lien else False,
                    informations_principales_agregees=_get_detail_lien(lien)
                )
                parents_par_niveau.update({level: ce_group})
                noeud_parents_par_niveau.update({level: child_node})
                groupements.add(ce_group)

        return FormationDTO(
            programme_detaille=ProgrammeDetailleDTO(groupements=groupements, unites_enseignement=ues),
            annee=annee,
            sigle=sigle,
            version=version,
            intitule_complet=tree.root_node.offer_title_fr
        )

    @classmethod
    def _get_lien(cls, child_node, noeud_parent, tous_liens):
        if noeud_parent:
            link_id = LinkIdentity(
                parent_code=noeud_parent.code,
                child_code=child_node.code,
                parent_year=noeud_parent.year,
                child_year=child_node.year
            )

            return next(
                filter(lambda link: link.entity_id == link_id, tous_liens),
                None
            )
        return None


def get_verbose_title_group(node: 'NodeGroupYear') -> str:
    if node.is_finality():
        return format_complete_title_label(node, node.offer_partial_title_fr)
    if node.is_option():
        return format_complete_title_label(node, node.offer_title_fr)
    else:
        return node.group_title_fr


def format_complete_title_label(node, title_fr) -> str:
    version_complete_label = formatter.format_version_complete_name(node, "fr-be")
    return "{}{}".format(title_fr, version_complete_label)


def get_verbose_credits(link: 'Link') -> str:
    if link.relative_credits or link.child.credits:
        return "{} ({} {})".format(
            get_verbose_title_group(link.child),
            link.relative_credits or link.child.credits or 0, _("credits")  # FIXME :: Duplicated line
        )
    else:
        return "{}".format(get_verbose_title_group(link.child))


def get_verbose_title_ue(node: 'NodeLearningUnitYear') -> str:
    verbose_title_fr = node.full_title_fr
    return verbose_title_fr


def _get_detail_lien(link: 'Link') -> str:
    if link.is_link_with_group():
        return get_verbose_credits(link)
    elif link.is_link_with_learning_unit():
        return "{} {} [{}] ({} {})".format(
            link.child.code,
            get_verbose_title_ue(link.child),
            get_volume_total_verbose(link.child),
            link.relative_credits or link.child.credits or 0, _("credits")  # FIXME :: Duplicated line
        )


def get_volume_total_verbose(node: 'NodeLearningUnitYear') -> str:
    return "%(total_lecturing)gh + %(total_practical)gh" % {
        "total_lecturing": node.volume_total_lecturing or Decimal(0.0),
        "total_practical": node.volume_total_practical or Decimal(0.0)
    }

