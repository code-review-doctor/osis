# Update or create ?

## Besoin métier

- En tant qu'utilisateur facultaire, je veux recopier une formation et son contenu de l'année N vers N+1.
- Si ma formation existe déjà ou qu'une partie de son contenu existe déjà, il faut l'écraser.


## Implémentation

```python

# Application service
@transaction.atomic()
def copy_training_to_next_year(cmd: CommandRequest) -> EntityIdentity:
    # GIVEN
    existing_training = TrainingRepository().get(
        entity_id=TrainingIdentity(acronym=copy_cmd.acronym, year=copy_cmd.postpone_from_year)
    )
    existing_training_next_year = TrainingRepository().get(
        entity_id=existing_training.get_identity_for_next_year()
    )
    
    # WHEN
    new_training_next_year = TrainingBuilder().copy_to_next_year(existing_training, existing_training_next_year)

    # THEN
    try:
        with transaction.atomic():
            identity = repository.create(new_training_next_year)
    except exception.TrainingAcronymAlreadyExistException:
        identity = repository.update(new_training_next_year)

```


## Questions : 

- Le update or create est-il une règle métier ?
- Notre EntityRoot (formation) est-elle en état consistant ?
- Quelle couche est responsable de la persistence des données ?


<br/><br/><br/><br/><br/><br/><br/><br/>


## Responsabilité : le repository

- Il est le seul à pouvoir déterminer si un aggrégat (EntityRoot) existe ou non en base de données
- Nouvelle fonction : Repository.save()
- Fonctions à déprécier : 
    - Repository.create()
    - Repository.update()
- Avantages :
    - Encapsulation de la logique de persistence dans la couche Repository
    - Facilité d'utilisation du Repository par no Application services
        - Pas d'ambiguïté : dois-je create ou dois-je update mon aggregate ?



<br/><br/><br/><br/><br/><br/><br/><br/>


## Solution

```python

# Application service
@transaction.atomic()
def copy_training_to_next_year(cmd: CommandRequest) -> EntityIdentity:
    # GIVEN
    existing_training = TrainingRepository().get(
        entity_id=TrainingIdentity(acronym=copy_cmd.acronym, year=copy_cmd.postpone_from_year)
    )
    existing_training_next_year = TrainingRepository().get(
        entity_id=existing_training.get_identity_for_next_year()
    )
    
    # WHEN
    new_training_next_year = TrainingBuilder().copy_to_next_year(existing_training, existing_training_next_year)

    # THEN
    identity = TrainingRepository().save(new_training_next_year)
    return identity

```



<br/><br/><br/><br/><br/><br/><br/><br/>



# Design patterns "Builder" et "Factory"

## Design pattern "Factory"

### Définition

https://refactoring.guru/fr/design-patterns/factory-method

- Le pattern **Factory** est un patron de conception de création qui définit une interface 
pour créer des objets dans une classe mère, mais délègue le choix des types d’objets à créer aux sous-classes.

### Problème

- Gestion d'un programme de formation (ProgramTree) qui contient des enfants appelés "groupements" (Node)
- Ces groupements peuvent être de plusieurs natures
    - une unité d'enseignement
    - une classe
    - un groupement
- Ces groupements ont des logiques à la fois communes et spécifiques à leurs natures



### Solution

- Utiliser une **Factory**, capable de créer un groupement en fonction des attributs
```python
from osis_common.ddd import interface


class Node(interface.Entity):
    """Classe comportant les logiques communes"""
    pass

class NodeGroupYear(interface.Entity):
    """Classe comportant les logiques spécifiques aux groupements"""
    pass

class NodeLearningUnitYear(interface.Entity):
    """Classe comportant les logiques spécifiques aux Unités d'Enseignement"""
    pass

class NodeLearningClassYear(interface.Entity):
    """Classe comportant les logiques spécifiques aux classes"""
    pass


class NodeFactory:
    def get_node(self, type: NodeType, **node_attrs) -> 'Node':
        if type == GROUP:
            return NodeGroupYear(**node_attrs)
        if type == LEARNING_UNIT:
            return NodeLearningUnitYear(**node_attrs)
        if type == LEARNING_CLASS:
            return NodeLearningClassYear(**node_attrs)
        raise Exception("Unknown type")

# Utilisation
learning_unit_node = NodeFactory().get_node(
    type=LEARNING_UNIT,
    code='LDROI1001',
    year=2021,
    # ... 
)



node_factory = NodeFactory()

``` 
    
### Avantages et inconvénients

- (+) Complexité de création (constructeurs complexes) masquée et encapsulée dans une classe dédiée
- (+) Principe de responsabilité unique : code de création d'un Node à un seul et même endroit, découplé de la logique métier (maintenance +++)
- (+) Flexibilité : permet d'ajouter de nouveaux types de Node sans endommager l'existant

- (-) Démultiplication des sous-classes (maintenance ---) 



<br/><br/><br/><br/><br/><br/><br/><br/>



## Design pattern "Builder"

### Définition

https://refactoring.guru/fr/design-patterns/builder

- Le pattern **Builder** est un patron de conception de création qui permet de construire des objets complexes 
étape par étape. Il permet de produire différentes variations ou représentations d’un objet 
en utilisant le même code de construction.

### Problème

- Gestion d'un programme de formation (ProgramTree) qui contient des enfants appelés "groupements" (Node)
- La création d'un programme de formation nécessite la création de groupements, sous-groupements, sous-sous-groupements... de types différents
- En fonction du type groupement racine du programme de formation, la création de son contenu change
- Je peux créer un programme de formation sur une année 2021 sur base de ce même programme en 2020

Constat : la création d'un programme de formation est complexe, avec beaucoup de champs et objets imbriqués


### Solution

- Utiliser un **builder**, capable de créer un groupement en fonction des attributs

```python
from osis_common.ddd import interface


class ProgramTree(interface.RootEntity):
    pass


class ProgramTreeBuilder:

    def create_from_other_tree(self, other_tree: 'ProgramTree') -> 'ProgramTree':
        root = self._duplicate_root(other_tree)
        mandatory_children_types = self._get_mandatory_children_types(other_tree, root)
        children = self._duplicate_children(other_tree)
        new_authorized_relationships = self._get_authorized_relationships(other_tree)
        
        # ... 
        # autres manipulations compliquées
        # ...
        
        return ProgramTree(
            entity_identity=ProgramTreeIdentity(code=root.code, year=root.year),
            root_node=root,
            authorized_relationships=new_authorized_relationships
        )

    def create(self, **program_tree_attrs) -> 'ProgramTree':
        node_attrs = self._extract_root_node_attrs(program_tree_attrs)
        root_node = node_factory.get_node(node_attrs)
        children = self._create_children(root_node, **program_tree_attrs)
        
        # ... 
        # autres manipulations compliquées
        # ...
        
        return ProgramTree(
            entity_identity=ProgramTreeIdentity(code=root.code, year=root.year),
            root_node=root,
            authorized_relationships=new_authorized_relationships
        )
```


### Avantages et inconvénients

- (+) Découplage du code : construire les objets étape par étape et les déléguer ou les exécuter récursivement.
- (+) Réutilisation du code : même code pour plusieurs représentations des ProgramTrees
- (+) Principe de responsabilité unique : code complexe de la construction séparé de la logique métier du ProgramTree

- (-) Démultiplication des classes (maintenance ---)




<br/><br/><br/><br/><br/><br/><br/><br/>



## Design pattern "Singleton"

### Définition

https://refactoring.guru/fr/design-patterns/singleton

- Le pattern **Singleton** est un patron de conception de création qui garantit que l’instance d’une classe 
n’existe qu’en un seul exemplaire, tout en fournissant un point d’accès global à cette instance.

### Avantages et inconvénients

- cf. https://refactoring.guru/fr/design-patterns/singleton

### Question

- Comment implémenter le Singleton pour le ProgramTreeBuilder ?
- Comment implémenter le Singleton pour le NodeFactory ?
- Devrait-on implémenter le Singleton pour les Factories et Builders ? 



<br/><br/><br/><br/><br/><br/><br/><br/>


### Pour Osis : 
- Dossier `Factory` : regroupe l'ensemble des factories et builders pour nos objets du domaine
- Factory utilisée par Repository ET par application service
    - Dossier Factory situé en dehors du domaine
    - Évite la duplication de code pour la reconstitution de l'objet métier
    - Évite de charger un objet métier àpd d'un repository qui serait dans un état inconsistant

- Factory obligatoire pour tous nos objets `RootEntity` et `EntityIdentity`
    - Avantage : pas d'ambiguité : tout objet du domaine ne peut être instancié que via factory
    - Avantage : facilité e distinction privé - publique : ce qui est publique possède une factory
    - Avantage : pas besoin de faire de new Identity(...) -> juste appeler la factory
    - Inconvénient : pattern "factory" complexe pour des objets simples ("overengineering")
