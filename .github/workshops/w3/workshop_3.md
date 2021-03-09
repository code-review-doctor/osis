
#### Pattern Factory / Builder

- [W3] Builder reçoit en paramètre une cmd pour pouvoir construire (instancier) une instance d'un objet du domaine. 
Et seulement lui !! Il est interdit de créer uen nstante d'un objet du domaine en dehors de ce builder.

- [W3] Créer une factory pour les EntityIdentity ? Qui a accès à cette couche ? Séparer Identité dans fichier séparé ?

- [W3] Les services ne peuvent pas instancier les objets du domaine s'il existe un pattern factory / builder

- [W3] Quid arborescence des fichiers lorsqu'on a une factory / builder ?? ==> Pour éviter la confusion, ne devrait-on pas avoir un dossier genre : program_tree/root_entity.py, program_tree/builder.py, program_tree/entity_identity.py ?? Afin de ne pas avoir trop de classes dans un même fichier ?

-------------------------------

### Application services

- [W3] Note importante : un service DOIT être réutilisable et ne doit faire qu'une seule chose à la fois.


-------------------------------

## Cas d'utilisation 1
### user story
En tant qu'utilisateur facultaire, je veux recopier une UE vers l'année suivante

### business rules
- Interdit de recopier si : 
    - l'UE existe déjà l'année suivante (sigle, année)
    - si sa date de fin d'enseignement est dépassée


## Cas d'utilisation 2
### user story
En tant qu'utilisateur facultaire, je veux prolonger une UE jusqu'à N+6

### business rules
- Le "N" de "N+6" représente l'année académique officielle (14/09/X -> 13/09/X+1) en cours

