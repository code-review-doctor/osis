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
from django.utils.datastructures import OrderedSet

from ddd.logic.preparation_programme_annuel_etudiant.domain.service.i_catalogue_formations import \
    ICatalogueFormationsTranslator
from ddd.logic.preparation_programme_annuel_etudiant.dtos import FormationDTO, GroupementCatalogueDTO, \
    ProgrammeDetailleDTO, UniteEnseignementCatalogueDTO
from program_management.ddd.command import GetProgramTreeVersionCommand
from program_management.ddd.domain.link import LinkIdentity


class CatalogueFormationsTranslator(ICatalogueFormationsTranslator):
    @classmethod
    def get_formation(cls, sigle: str, annee: int, version: str) -> 'FormationDTO':
        # reutiliser GetProgramTreeVersionCommand et convertir ProgramTreeVersion en FormationDTO
        from infrastructure.messages_bus import message_bus_instance
        program_tree_version = message_bus_instance.invoke(GetProgramTreeVersionCommand(
            year=annee,
            acronym=sigle,
            version_name=version,
            transition_name=""
        ))
        tree = program_tree_version.get_tree()

        groupements = OrderedSet()
        ues = OrderedSet()
        parents_par_niveau = {}
        noeud_parents_par_niveau = {}
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
                    volume_annuel_pp=child_node.volume_total_practical
                )
                ues.add(ue)
            else:
                group_inclus_dans = None
                if level != 1:
                    group_inclus_dans = parents_par_niveau.get(level-1)

                ce_group = GroupementCatalogueDTO(
                    inclus_dans=group_inclus_dans,
                    intitule=child_node.title,
                    commentaire=lien.comment if lien else '',
                    remarque=child_node.remark_fr,
                    obligatoire=lien.is_mandatory if lien else ''
                )
                parents_par_niveau.update({level: ce_group})
                noeud_parents_par_niveau.update({level: child_node})
                groupements.add(ce_group)

        return FormationDTO(
            programme_detaille=ProgrammeDetailleDTO(groupements=groupements, unites_enseignement=ues),
            annee=annee,
            sigle=sigle,
            version=version,
            intitule_complet=tree.root_node.title
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
