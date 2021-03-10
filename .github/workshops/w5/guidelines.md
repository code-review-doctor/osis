

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
   

