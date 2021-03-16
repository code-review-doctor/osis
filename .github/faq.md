## FAQ

Regroupe les questions dont les réponses ne peuvent pas être formalisée sous forme de guideline/règle stricte, 
mais plutôt sous forme de "philosophie de développement".

<br/><br/>

#### :question: L'analyse est en français, le code en anglais : comment traduire correctement le métier ?

 Les développeurs doivent être d'accord sur un terme en anglais qui identifie clairement l'élément métier, l'objet, la variable... 
 Si lors de la review, le développeur comprend le code (assez explicite) et identifie clairement la correspondance en français : c'est un accord.
 > :information_source: [WordReference - Dictionnaire en ligne fournissant toutes les traductions possibles d'un mot en fonction de son contexte](https://www.wordreference.com/fr/)

<br/><br/>


#### :question: Jusqu'où doit-on modifier un code non lié à notre ticket ? 

Cf. [Boyscout rule](https://www.matheus.ro/2017/12/11/clean-code-boy-scout-rule/)

Attention à ne pas tomber dans l'excès, qui mènerait à une PR complexe et longue à reviewer, ou trop détachée de l'objectif original du ticket.

<br/><br/>


#### :question: Quid si un code "legacy" que je dois modifier ne respecte pas nos guidelines ?

Il est possible que certaines parties de code (plus anciennes) ne respectent pas l'ensemble de ces guidelines
(qui sont en constante évolutions - comme nos compétences). 
Si cet ancien code doit être modifié, ces guidelines restent d'application (dans la mesure du bon sens bien évidemment ; 
la correction d'un bug dans du code "non DDD" ne demande pas la réécriture complète du module en DDD). 

La mise en application de certaines guidelines dans un ancien code peut mener à du travail supplémentaire. 
Ce travail supplémentaire est un gain de temps pour tout prochain développeur qui rentrera dans cette partie du code.

Si vous ne le faites pas, c'est votre collègue qui perdra du temps.

<br/><br/>

#### :question: Quand doit-on appliquer le DDD ? Quid du CRUD ? Quid des views de recherche, fichiers excels, pdfs ?

Le DDD n'est pas une réponse à tout. Comme le décrit très bien l'article [Domain Driven Design : des armes pour affronter la complexité](https://blog.octo.com/domain-driven-design-des-armes-pour-affronter-la-complexite/),
il y a des avantanges et inconvénients.

Dans le cadre du projet Osis, nous privilégions - pour le moment - l'utilisation du DDD pour les services `Read` et `Write` pour 2 raisons :
- Détacher notre base de code au maximum de la DB et limiter les coût de refactoring : Osis étant la réécriture d'un projet Legacy, sa base de code et son modèle DB est en constante évolution
- Éviter d'intégrer trop de nouveaux concepts en même temps dans l'équipe et dans le projet

Si des problèmes de performances sont constatés, diverses solutions pourront être mises en place (lazy load, ORM/SQL pour les services `Read`...). 
Nous modifierons notre manière de travailler et adapterons nos guidelines en conséquence.
