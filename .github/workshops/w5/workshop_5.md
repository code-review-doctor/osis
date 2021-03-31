## [W6] Formation 5 :
- Partie 1
    - (pratique) ResponsibleEntity : refactoring (UE)
    - (théorie) DTO : définition
    - (pratique) Use case : En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE.
    - (pratique) Corriger nos forms pour utiliser DTO ? 

- partie 2
    - Théorie :
        - Architecture oignon : définition + structure dossiers
        - Command bus : définition
    - Workshop
        - Refactorer notre code (dossiers) selon cette architecture
        - Injection des dépendances des repositories dans les application services
        - Command bus : implémentation


## Cas d'utilisation
### user story
- En tant qu'utilisateur, je veux rechercher toutes les UEs sur base d'un formulaire de recherche :
### business rules
- Champs de recherche :
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
        - code
        - intitulé (en helptext)
    - entité d'attribution
        - code
        - intitulé (en helptext)
    

