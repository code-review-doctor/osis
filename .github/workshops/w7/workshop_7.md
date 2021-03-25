## Serializers 


Confusion de l'équipe entr responsabilité de l'affichage et du domaine
Exemples : 
- DROI1BA[CEMS][TRANSITION] : affichage ? Domaine ?
    - réponse perso : attribut "sigle complet" du domaine
- "translate" dans les prérequis : And, et, or, ou... : affichage ? domaine ?


- [???] Ou gérer les traductions ?

- Single respojsibility principle
def __gt__(self, other):
    return other.year > self.year


- W5? Bounded contexts
    - [ALES] ApplicationService peutil appeler plusieurs repositories de plusieurs domaines différents ?
    
- Rapports (warnings, changes...) et events

- Ajouter une classe RequiredBoostrapField pour les "*" - si required=False à tous les forms
