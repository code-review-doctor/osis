## ResponsibleEntity

Dans notre domaine des UEs, ResponsibleEntity (et son validateur) ne respectent pas nos guidelines vues précédemment
 en workshop.

- Quelle(s) guideline(s) et/ou quel(s) principe(s) ResponsibleEntity ne respecte-il pas ? 
- Comment pourrait-on améliorer notre code ?


## BusinessValidator : frozen=True ? Quid des propriétés calculées ?

- Si une propriété ne doit être calculée qu'une seule fois : sandwich pattern.
    - À calculer au départ de la fonction "validate" **dans le domaine**
    - Propriété (variable) à passer en paramètre de chaque sous fonction, qui seront "statiques"
        - Car ne modifie pas l'état de l'objet

```python

@attr.s(frozen=True, slots=True)
class ComplexBusinessValidator(BusinessValidator):

    root_entity = attr.ib(type=RootEntity)
    attr2 = attr.ib(type=PrimitiveType)
    attr3 = attr.ib(type=PrimitiveType)
    attr4 = attr.ib(type=PrimitiveType)

    def validate(self, *args, **kwargs):
        complex_result = self.root_entity._complex_computation()
        other_result = self.some_computation(complex_result)
        another_result = self.some_other_computation(complex_result)
        # if ... raise ...
        
    @staticmethod
    def some_computation(complex_result):
        pass
            
    @staticmethod
    def some_other_computation(complex_result):
        pass    

```



## DTO : Data Transfer Object


### Définition

- "Objet de transfert de données"
- Patron de conception d'architecture
- Objectif : simplifier le transfert des données entre les couches d'une application logicielle 
- Possède uniquement des déclarations d'attributs
- Aucune logique technique, métier, fonction...
- "Contrat de données" qui nous aide à atteindre la compatibilité entre les différentes couches d'une application
- Enlève l'interdépendance entre couches
    - Facilite le refactoring

- Question : avons-nous déjà des DTO dans notre code actuel ?


<br/><br/><br/><br/><br/><br/><br/><br/>



### Problème

- En tant qu'utilisateur, je veux rechercher toutes les UEs sur base d'un formulaire de recherche :
    - code
    - année académique
    - intitulé
    - type
    - entité de charge (et entités subordonées)
- Dans la vue "liste", je veux afficher 
    - année académique
    - code
    - intitulé complet
    - type
    - entité de charge
    - entité d'attribution
    
```python
# Application service
def search_learning_units_service(cmd: interface.CommandRequest) -> List['LearningUnit']:
    return LearningUnitRepository().search(**cmd)
```

Constats : 
- la recherche est (trop) lente
- charge beaucoup de données inutiles
    - je n'affiche que 5 champs de l'objet LearningUnit
    - renvoie LearningUnit objet complet du domaine avec toutes entities imbriquées



<br/><br/><br/><br/><br/><br/><br/><br/>



### Solution


```python

class SearchLearningUnitDTO(interface.DTO):
    academic_year = attr.ib(type=int)
    code = attr.ib(type=str)
    complete_title = attr.ib(type=str)
    type = attr.ib(type=str)
    responsible_entity = attr.ib(type=str)


# TODO : create IReadLearningUnitRepository ? 
class LearningUnitRepository(interface.AbstractRepository):

    def search(self, **searchparams) -> List[SearchLearningUnitDTO]:
        # To implement
        return []

```


Inconvénients :
- Logique métier encapsulée dans la query de sélection
    - intitulé complet
- Peut devenir difficile si nécessite d'afficher des données de domaines différents


Avantages :
- Découplage de la DB (et des querysets)
    - Contrat de données attendues pour la recherche d'une liste de LearningUnit
- performances


Question : 
- Doit-on créer un DTO par ListView / form de recherche ?



<br/><br/><br/><br/><br/><br/><br/><br/>



## Quand utiliser un DTO ?

- Toujours maximiser la réutilisation de nos objets du domaine
    - Mapping avec la DB déjà effectuée (via repository)
    - Logique métier encapsulée dans nos objets du domaine

- Lorsque les performances en lecture deviennent excessives. 
    - Cas possibles : 
        - Vue de recherche (vue liste)
        - données initiales de Forms filtrées : DTO ou domain service ? (exemple : filtrer les etds en états X ou Y)
        - Fichier Excel
        - Fichier PDF
    - Dans ce cas, les Views/forms/pdf/excel... réutilisent un ApplicationService qui renvoie un DTO à partir d'un Repository

- Dans les repositories, tout ce qui vient d'un Queryset Django

- Dans les `Repository.get()` qui utilisent les Factory pour créer un objet du domaine
    - Permet de typer les valeurs de retour des querysets


- Utiliser un IReadRepository pour les DTO (afin de séparer les repo READ / WRITE == CQS) ?

- Lorsque le domaine métier n'existe pas encore, mais qu'on doit développer des écrans en lecture seule



<br/><br/><br/><br/><br/><br/><br/><br/>



## Interface : définition

- Déclaration d'un ensemble standardisé de méthode
- Intermédiaire entre 2 logiciels au travers d'un langage commun
- Objectif : cacher la difficulté d'accès à un logiciel
- Plus notre logiciel est modulaire/découplé, plus il y aura d'interfaces 
- Exemple :
    - API : Application Programming Interface
        - Protocole de communication : HTTP / HTTPS


#### :question: avons-nous d'autres interfaces dans notre code ?



<br/><br/><br/><br/><br/><br/><br/><br/>



## Architecture en oignon



### Bounded Context

- cf. Language et Entity dans notre domaine UE

En partant de l'idée qu'on aura 1 seule factory pour 1 Repository et 1 application service :

Et pour les DTO : on utiliserais 1 DTO par AggregateRoot ? Pour fusionner le Builder.cuild_from_command et buildfromrepositry? 

### Shared Kernel

- Quid des value objects réutilisables ?

### Schéma et couches


### Arborescence des packages

- Changer le dossier "service" en "use cases" ?
- W5 : ou placer les exceptions.py ? (exceptions business)
- Où placer les command.py ?  
- Où placer les DTOs ? 
- Où placer les Django views, forms... app django ? 



<br/><br/><br/><br/><br/><br/><br/><br/>



## Message bus


### Commands : rappel

- Représente les actions possibles d'un utilisateur
    - Fait partie entièrement du domaine
- Déclenche une modification dans notre domaine
- Une commande peut ne pas être "valide" pour notre domaine (cf. validateurs) 
    - Les paramètres d'une commande ne peuvent jamais être considérés comme une valeur "valide"
    - Le domaine ne peut pas s'y fier et doit valider les paramètres d'entrée
    - Interdit de passer des valeurs calculées "businessement" dans une commande
- "Appels de méthode sérialisables"
- Exemple :
```python

@attr.s(frozen=True, slots=True)
class CreateOrphanGroupCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    type = attr.ib(type=str)
    abbreviated_title = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    constraint_type = attr.ib(type=str)
    min_constraint = attr.ib(type=int)
    max_constraint = attr.ib(type=int)
    management_entity_acronym = attr.ib(type=str)
    teaching_campus_name = attr.ib(type=str)
    organization_name = attr.ib(type=str)
    remark_fr = attr.ib(type=str)
    remark_en = attr.ib(type=str)
    start_year = attr.ib(type=int)
    end_year = attr.ib(type=Optional[int])
```

- Application service == command handlers (gestionnaire de commandes)


### Événements

- Résultat d'une action métier
    - Résultat d'une commande
- Exemples : 
    - Formation créée
    - Groupement supprimé
    - Unité d'enseignement reportée
    - Volumes de l'UE mis à jour


### Message bus

#### Définition et objectifs


- [W6] message bus - pour aider aux unit tests https://github.com/uclouvain/osis/commit/520789ff538cc2046237f817f439c273c9093cae
- injection des repositories
- [W6] Pourquoi ne pas utiliser l'héritage pour les commandes qui ont (et qui doivent avoir ! ) les mêmes paramètres que d'autres commandes? (Exemple : UpdateAndPostpone hériterait d'Update, etc.)


#### Implémentation

```python

class MessageBus(AbstractMessageBus):
    EVENT_HANDLERS = {}
    COMMAND_HANDLERS = {
        command.CreateOrphanGroupCommand: lambda cmd: create_group_service.create_orphan_group(cmd, GroupRepository())
    }

```