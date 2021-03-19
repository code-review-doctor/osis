- [W6] message bus - pour aider aux unit tests https://github.com/uclouvain/osis/commit/520789ff538cc2046237f817f439c273c9093cae


- [W6] Pourquoi ne pas utiliser l'héritage pour les commandes qui ont (et qui doivent avoir ! ) les mêmes paramètres que d'autres commandes? (Exemple : UpdateAndPostpone hériterait d'Update, etc.)

- Quid des value objects réutilisables ? 

- Changer le dossier "service" en "use cases" ?

- POurquoi DTo ? Car nécessaire de pouvoir proposer du contenu en lecture uniquement dans un premier temps (le DDD pourrait venir par rapèrs)
- FAQ : Quand utiliser les DTO pour la consultation quand utiliser nos objets du domaine ?
- Un DTO peut il être utilisé dans le Domaine ??
- Utiliser un IReadRepository pour les DTO (afin de séparer les repo READ / WRITE == CQS)
- DTO : les Django serializers aident facilement à la conversion en DTO : est-ce qu'on ne les réutiliserait pas ?
- données initiales de Forms filtrées : DTO ou domain service ? (exemple : filtrer les etds en états X ou Y)
- Nos Interface.CommandRequest sont des DTO

Ok donc on va partir sur des DTO + repository qui renvoient des DTO + querysets UNIQUEMENT dans les repos. 
Les Serializers, forms, views utilisent alors un applicaiton service qui renvoie DTO à parir d'un repo 

- W5 : mettre à jour la partie "abroerscence des packages" dans le CONTRIBUTING (suite à workshop)
- W5 : ou placer les exceptions.py ? (exceptions business)

- W5? Bounded contexts
    - [ALES] ApplicationService peutil appeler plusieurs repositories de plusieurs domaines différents ?

- W5 Shared Kernel ?
