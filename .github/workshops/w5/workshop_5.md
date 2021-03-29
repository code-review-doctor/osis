## [W6] Formation 5 :

    Théorie :
        Architecture iognon : définition + structure dossiers (attention à inclure la position des views, forms...)
        Command bus : définition
        DTO : définition
    Workshop [contenu à développer]
        Refactorer notre code selon cette architecture
        Injection des dépendances des repositories dans les application services
        Créer un Form, une view, un template pour créer une UE
        Command bus : implémentation


## Cas d'utilisation
### user story
En tant qu'utilisateur facultaire, je veux visualiser le nombre d'inscrits à une UE. 
### business rules
- Je veux le nombre total d'inscrits à l'UE
- Les inscriptions à l'UE sont obligatoirement dans le contexte d'une inscription à une formation
- Je veux le nombre d'inscrits à l'UE divisés par formation
- L'état de l'inscription à la formation doit être SUBSCRIBED ou PROVISORY

