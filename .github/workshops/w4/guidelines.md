
### forms

- Les validations des forms doivent se trouver dans les validators du domaine
    - Validateurs du domaine :
        - RequiredFieldsValidator
        - MaximumValueValidator
        - MinimumValueValidator
        

-------------------------------

### validateurs

- [W4] Un validateur ne peut pas modifier les arguments qu'elle reçoit pour sa propre validation. Exemple : self.transition_name = "TRANSITION " + transitionname (https://github.com/uclouvain/osis/pull/9680/files#)
- Effectuer toujours les checks AVANT d'effectuer l'action métier sur l'objet
        - évite d'avoir un objet du domaine en état inconsistant -> garantit qu'un objet du domaine tjr consistant (plus facile en mainteance)
        - facilite les tests unitaires
        - si après : oblige à dunder method "add_node" sans validation métier -> porte ouverte
        - Question : qqn voit-il un avantage à faire le check après validation ? 