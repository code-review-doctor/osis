# CQS : Command Query Separation


## Définition

- En français : séparation commande-requête

- Principe de programmation qui vise à séparer les objets/fonctions en 2 catégories
    - Les "requêtes" : 
        - retournent un résultat 
        - ne modifient pas l'état du système 
        - pas de "side effect" possible

    - Les "commandes" :
        - modifient l'état du système
        - ne renvoient pas de résultat
        - synonymes : "modifiers", "mutators"

- Exemple :

```python
from typing import List

# Non CQS
fruit = next(["pomme", "fraise", "orange"])

# CQS :
# Commande
def avancer(fruits: List['str']) -> None:
    pass

# requête 
def element_courant(fruits) -> str:
    pass
```

<br/><br/><br/><br/><br/><br/><br/><br/>


## CQS : Avantages

- Visibilité claire sur le code qui modifie l'état du système du code qui le consulte

- Facilité de maintenance en cas de problème de performance (souvent, en lecture)



## CQS : Notre implémentation

- Application services read / write
- Cf. [interface DDD](https://github.com/uclouvain/osis-common/blob/e9496bc8bc4b586a8ba2dafa5292992ae2f6c09b/ddd/interface.py)
