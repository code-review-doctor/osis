from typing import List

from program_management.ddd.repositories.program_tree_version import build_unite_enseignement_DTO_depuis_link


def build_unites_enseignement_contenues_dans_pgm(node: 'Node', contenu: List['UniteEnseignementDTO'] = []) \
        -> List['UniteEnseignementDTO']:
    for lien in node.children:
        if lien.child.is_learning_unit():
            contenu.append(
                build_unite_enseignement_DTO_depuis_link(lien)
            )
        else:
            contenu = build_unites_enseignement_contenues_dans_pgm(lien.child, contenu)
    return contenu
