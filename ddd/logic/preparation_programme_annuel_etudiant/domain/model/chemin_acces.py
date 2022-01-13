from typing import Union, List

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement import CodeGroupement
from ddd.logic.preparation_programme_annuel_etudiant.domain.model.unite_enseignement import CodeUniteEnseignement


class CheminAcces(str):

    separateur: str = '|'

    @property
    def dernier_element(self) -> Union['CodeGroupement', 'CodeUniteEnseignement']:
        return self.split(self.separateur)[-1]

    @property
    def racine(self) -> 'CodeGroupement':
        return self.split(self.separateur)[0]

    @property
    def codes_groupements(self) -> List['CodeGroupement']:
        return self.split(self.separateur)
