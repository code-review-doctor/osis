# 6. Use Tactical Domain-Driven Design

Date: 2021-11-18

## Status

Accepted

## Context

Having a tightly coupled code (Template, View, Model) is very hard to maintain and make change mainly when there are many business rules.
Developers have fear of modification because it's very difficult to predict the result of a change.
Moreover, each developer has it's own codestyle/approach which can lead to inconsistent way to 
treat same problems.


## Decision

If we use Domain-Driven-Design approach for a business case, we will use a set of patterns defined in the tactical part:
- Repository
- Entities
- Value Objects
- Aggregates
- Domain Services
- Application Services
- Factories
- DTO

Each components have one and only one purpose, we will use them accordingly.


## Consequences

+) Consistent way of treating a part of business problem.

+) Business logic is encapsulated in one place.

-) Use Domain Driven Design approach with business (Strategic part) can lead to organisational issues.