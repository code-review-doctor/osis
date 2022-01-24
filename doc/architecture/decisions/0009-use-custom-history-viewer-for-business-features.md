# 9. Use custom history viewer for business features

Date: 2021-11-18

## Status

Accepted

## Context

We track model changes with the extension called Django-Reversion (cf. https://django-reversion.readthedocs.io/en/stable/).
With DDD approach (cf. ADR 0006) and hexagonal architecture (cf. ADR 0007), it can be difficult to track changes because 
the same database model can be updated by two different commands.

Moreover, Django-Reversion is implicit and tightly coupled to Django Model (=Implementation) 
so it doesn't respect the fact if it's a business need, it should be explicitly stated in DDD domain logic.

## Decision

For business feature, we will use OSIS-History (cf. https://github.com/uclouvain/osis-history) as default history viewer.
For intern/technical use, we will choose Django-Reversion.


## Consequences

+) Consistent way of treating history feature.

+) More explicit behaviour when reading code.
