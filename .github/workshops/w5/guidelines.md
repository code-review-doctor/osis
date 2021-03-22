

-------------------------------

### Commandes

- [W6] # GUIDELINES :: 1 commande par service obligatoire !
- [W6] Un service == CommandHandler


-------------------------------

### Application service

- [W6] Injection de dépendances des repositories

-------------------------------

### Repository

- repository : regroupe uniquement les interfaces
      - Nomenclature : IRepository
      - Exemple : ProgramTreeIRepository.search_from_children()

-------------------------------

### Coding styles

- [W5] Correction d'un bug = obligation d'un test unitaire.

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

