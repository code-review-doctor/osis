## [W4] Formation 4

- Partie 1
    - Théorie : les validateurs, questions posées :
        - Appliquer les validateurs avant ou après modification de l'objet du domaine? (pour valider sa consistance avant persistence) ?
        - Quid des validateurs dans les forms par rapport aux validateurs du domaine?
    - Workshop :
        - Refactoring de notre code (UE) selon les réponses à ces questions
- Partie 2
    - Théorie :
        - Comment gérer les "check" / rapports d'une action ?
            - Comment afficher tous les messages d'erreurs d'une action plutôt que de s'arrêter à la première ?
            - Comment gérer les fonctions du style check_paste_node_service (éviter le duplication) ?
        - Pattern "Mediator"
    - Pratique [contenu à développer] :
        - Use case : En tant qu'utilisateur, je veux obtenir un rapport (à l'écran) de toutes les erreurs lorsque je soumets mon formulaire de création d'une UE
