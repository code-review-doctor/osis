# Entity VS ValueObject

## Entity

- Cf. [interface.Entity](https://github.com/uclouvain/osis-common/blob/master/ddd/interface.py#L32)
- Possède une identité (EntityIdentity)
- Deux entités sont identiques ssi leurs identités sont les mêmes
- Mutable
    - Toute modification de l'objet change l'état de l'objet
    - Possède un historique (à travers le temps)
- Exemples : 
    - Une formation (Training)
    - Un groupement (Group)
    - Un professeur (Tutor)


## ValueObject

- Cf. [interface.ValueObject](https://github.com/uclouvain/osis-common/blob/master/ddd/interface.py#L20)
- Ne possède pas d'identité
    - L'ensemble de ses attributs composent son identité
- Deux ValueObjects sont les mêmes ssi l'ensemble des valeurs de leurs attributs sont les mêmes
- Immuable
    - Toute modification de l'objet signifie que c'est un nouvel objet
    - Ne possède pas d'historique
- Appartient d'office à une Entity
- Exemples : 
    - Une date
    - Une adresse


## EntityIdentity

- Cf. [interface.EntityIdentity](https://github.com/uclouvain/osis-common/blob/master/ddd/interface.py#L28)
- Représente l'indentité d'une entité de notre domaine
- Si elle change, c'est U'on ne parle plus du même "objet"
    - C'est donc un ValueObject
- Exemple : 
```python

@attr.s(frozen=True, slots=True)
class TrainingIdentity(interface.EntityIdentity):
    acronym = attr.ib(type=str, converter=to_upper_case_converter)
    year = attr.ib(type=int)

```



<br/><br/><br/><br/><br/><br/><br/><br/>



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
class MyFruitsList:
    fruits : List['str'] = None
    _curent_element_position = None
    
    def next(self):
        if self._curent_element_position is None:
            self._curent_element_position = 0
        else: 
            self._curent_element_position += 1
        return self.fruits[self._curent_element_position]

my_fruits = MyFruitsList(fruits=["pomme", "fraise", "orange"])
pomme = my_fruits.next()
fraise = my_fruits.next()
orange = my_fruits.next()


# CQS
class MyFruitsList:
    fruits : List['str'] = None
    _curent_element_position = 0
    
    # Commande
    def move_forward(self) -> None:
        self._curent_element_position += 1
    
    # requête 
    def current_element(self) -> str:
        return self.fruits[self._curent_element_position]


my_fruits = MyFruitsList(fruits=["pomme", "fraise", "orange"])
pomme = my_fruits.current_element()

my_fruits.move_forward()
fraise = my_fruits.current_element()

my_fruits.move_forward()
orange = my_fruits.current_element()

```

<br/><br/><br/><br/><br/><br/><br/><br/>


## CQS : Avantages

- Visibilité claire sur le code qui modifie l'état du système du code qui le consulte

- Facilité de maintenance en cas de problème de performance (souvent, en lecture)



## CQS : Notre implémentation

- Application services read / write
- Cf. [interface DDD](https://github.com/uclouvain/osis-common/blob/e9496bc8bc4b586a8ba2dafa5292992ae2f6c09b/ddd/interface.py)
