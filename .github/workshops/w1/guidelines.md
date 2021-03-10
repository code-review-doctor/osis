## Guidelines

### Application services

- [W1] Ne peut pas être modifié ! (Sauf en cas de bug). Un application service étant un use case, son contenu ne devrait jamais être modifié - sauf si le use case métier a changé.


-------------------------------

### Repository

- [W1] Les repository peuvent instancier un objet du domaine ("DTO" via l'ORM)

- [W1] 1 repository par RootEntity
    - Pas de repository pour des ValueObjects
    - persistence : 1 transaction par aggregate root


-------------------------------

### Domain

- [W1] Tip : si du code utilise des termes techniques dans le domaine, c'est un indice
indiquant qu'il n'est pas au bon endroit
- [W1] Si EntityIdentity via clé naturelle n'est pas possible, il faut utiliser un UUID (pas d'ID)
    - Exemple : Une personne (l'identifiant naturel est difficile) ==> UUID
    - TODO :: na pas dupliquer avec autre guideline similaire

- [W1] Pas de get_or_create / update_or_create pour les Entities mis uniquement pour les values objetcs 

-------------------------------

### Commandes
- [W1] Les paramètres d'une commande ne peuvent jamais être considérés comme une valeur "valide" : 
le domaine ne peut pas s'y fier. Interdit de passer des valeurs calculées "businessement" dans une commande.

