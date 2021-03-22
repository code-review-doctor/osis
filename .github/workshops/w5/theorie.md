## DTO : Data Transfer Objects


### Définition

- Patron de conception d'architecture
- Objectif : simplifier le transfert des données entre les couches d'une application logicielle 
- "Objet de transfert de données"
- Possède uniquement des déclarations d'attributs
- Aucune logique technique, métier, fonction...
 
- Question : avons-nous déjà des DTO dans notre code actuel ?



<br/><br/><br/><br/><br/><br/><br/><br/>



### Problème 1

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

Solution : 


```python

class SearchLearningUnitDTO(interface.DTO):
    academic_year = attr.ib(type=int)
    code = attr.ib(type=str)
    complete_title = attr.ib(type=str)
    type = attr.ib(type=str)
    responsible_entity = attr.ib(type=str)


class LearningUnitRepository(interface.AbstractRepository):

    def search(self, **searchparams) -> List[SearchLearningUnitDTO]:
        # To implement
        return []

```


Inconvénients : 
- Couplage fort avec la DB
- Logique métier encapsulée dans la query de sélection
    - intitulé complet
    
- Peut devenir difficile si nécessite d'afficher des données de domaines différents

Avantages :
- performances


### Problème 2

- En tant qu'utilisateur, je veux consulter la liste des groupements et formations qui utilisent une UE

```python

# Application service
def search_formations_by_learning_unit_service(cmd: interface.CommandRequest) -> List['ProgramTreeVersion']:
    return ProgramTreeVersionRepository().search(learning_unit_identity=LearningUnitIdentity(com.code, cmd.year))

```

- Même constat et mémé solution que le cas ci-dessus


- POurquoi DTo ? Car nécessaire de pouvoir proposer du contenu en lecture uniquement dans un premier temps (le DDD pourrait venir par rapèrs)
- FAQ : Quand utiliser les DTO pour la consultation quand utiliser nos objets du domaine ?
- Un DTO peut il être utilisé dans le Domaine ??
- Utiliser un IReadRepository pour les DTO (afin de séparer les repo READ / WRITE == CQS)
- DTO : les Django serializers aident facilement à la conversion en DTO : est-ce qu'on ne les réutiliserait pas ?
- données initiales de Forms filtrées : DTO ou domain service ? (exemple : filtrer les etds en états X ou Y)
- Nos Interface.CommandRequest sont des DTO

Ok donc on va partir sur des DTO + repository qui renvoient des DTO + querysets UNIQUEMENT dans les repos. 
Les Serializers, forms, views utilisent alors un application service qui renvoie DTO à parir d'un repo 


## Architecture en oignon

### Interface : définition


### Shared Kernel

- Quid des value objects réutilisables ?

### Schéma et couches


### Arborescence des packages

- Changer le dossier "service" en "use cases" ?
- W5 : ou placer les exceptions.py ? (exceptions business)
- Où placer les command.py ?  



## Message bus

- [W6] message bus - pour aider aux unit tests https://github.com/uclouvain/osis/commit/520789ff538cc2046237f817f439c273c9093cae
- injection des repositories
- [W6] Pourquoi ne pas utiliser l'héritage pour les commandes qui ont (et qui doivent avoir ! ) les mêmes paramètres que d'autres commandes? (Exemple : UpdateAndPostpone hériterait d'Update, etc.)

