

#### Pattern Factory / Builder

- [W3] Builder reçoit en paramètre une cmd pour pouvoir construire (instancier) une instance d'un objet du domaine. 
Et seulement lui !! Il est interdit de créer uen nstante d'un objet du domaine en dehors de ce builder.

- [W3] Créer une factory pour les EntityIdentity ? Qui a accès à cette couche ? Séparer Identité dans fichier séparé ?

- [W3] Les services ne peuvent pas instancier les objets du domaine s'il existe un pattern factory / builder

- [W3] Quid arborescence des fichiers lorsqu'on a une factory / builder ?? ==> Pour éviter la confusion, ne devrait-on pas avoir un dossier genre : program_tree/root_entity.py, program_tree/builder.py, program_tree/entity_identity.py ?? Afin de ne pas avoir trop de classes dans un même fichier ?

-------------------------------

### Application services

- [W3] Note importante : un service DOIT être réutilisable et ne doit faire qu'une seule chose à la fois.
Par exemple, un service de mise à jour ne doit faire qu'une mise à jour et rien de plus (pas de report !).
En d'autres termes, si une action (bouton) utilisateur nécessite de créer un training, reporter ce training, créer le programme type, le reporter, créer le gorupement et le reporter, etc... cela doit être 1 service qui fait appel à tous ces services implémentés dans des domaines différents.

