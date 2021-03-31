
- W5 : mettre à jour la partie "abroerscence des packages" dans le CONTRIBUTING (suite à workshop)

- Référencer les Aggregates à travers leur EntityIdentity pour assurer découplage

- mettre "exceptions" dans /validators !

- Toute fonction impélmentée dans Repository doit se trouver dans l'interface coté domaine

-------------------------------

### Commandes

- [W6] # GUIDELINES :: 1 commande par service obligatoire !
- [W6] Un service == CommandHandler
 - [W4] Les paramètres d'une commande ne peuvent jamais être considérés comme une valeur "valide" : 
 le domaine ne peut pas s'y fier. Interdit de passer des valeurs calculées "businessement" dans une commande.


-------------------------------

### Repository

- repository : regroupe uniquement les interfaces
      - Nomenclature : IRepository
      - Exemple : ProgramTreeIRepository.search_from_children()
- Seul à connaître les Querysets


-------------------------------

### Shared Kernel

- Regroupe les ValueObject et Entity qui sont réutilisés à travers différents bounded contexts.
- Pour le moment, privilégier la duplication de mêmes Entity / ValueObject dans les bounded contexts 
- L'ajout d'un Entity / ValueObject est à discuter avec l'équipe
- TODO :: documenter avantages et inconvénient d'un shared kernel
   

-------------------------------

### Application services

- [W5] Note importante : un service NE PEUT PAS être réutilisable et ne doit faire qu'une seule chose à la fois.
Par exemple, un service de mise à jour ne doit faire qu'une mise à jour et rien de plus (pas de report !).
En d'autres termes, si une action (bouton) utilisateur nécessite de créer un training, reporter ce training, créer le programme type, le reporter, créer le gorupement et le reporter, etc... cela doit être 1 service qui fait appel à tous les RootEntity/DomainServices implémentés dans des domaines différents.
- [W6] Injection de dépendances des repositories

