# 8. Use french in DDD logic

Date: 2021-11-18

## Status

Accepted

## Context

Domain-Driven-Design emphasize on the concept of Ubiquitous Language (cf. https://martinfowler.com/bliki/UbiquitousLanguage.html).

In our context, business people speak in french and we translate terms into english. 
However, sometimes it's very difficult to find the good 'english' translation that every people involved in the project understand.


## Decision

We will write all business terms in french on the DDD logic part of the project (=ddd/logic folder).


## Consequences

+) Respect the notion of Ubiquitous Language.

+) Prevent bad translation.

-) OSIS aims to be open-source and english is the default language in the community.
