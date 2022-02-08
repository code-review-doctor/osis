from typing import List

from program_management.ddd.domain.link import LinkWithChildBranch
from program_management.ddd.repositories.program_tree_version import build_unite_enseignement_DTO_depuis_link
from osis_common.ddd import interface


class GetUnitesEnseignementContenuesDansPgrm(interface.DomainService):

    @classmethod
    def build_unites_enseignement_contenues_dans_pgm(
            cls,
            liens: List['LinkWithChildBranch'],
            contenu: List['UniteEnseignementDTO'] = []
    ) -> List['UniteEnseignementDTO']:
        for lien in liens:
            if lien.child.is_learning_unit():
                contenu.append(
                    build_unite_enseignement_DTO_depuis_link(lien)
                )
        return contenu
