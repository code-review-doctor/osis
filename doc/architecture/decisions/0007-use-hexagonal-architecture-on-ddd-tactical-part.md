# 7. Use Hexagonal architecture on DDD Tactical part

Date: 2021-11-18

## Status

Accepted

## Context

The role of incremental change in Agile involves frequent database changes, 
technology changes (ex: API Rest, Javascript, ...) in order to accomplish business needs.
Moreover, we don't make a distinction between the interface and the implementation 
which implies that we cannot create fake services (=in memory) when we test our applications.

## Decision

If we use Domain-Driven-Design approach for a business case, we will make distinction between the declaration 
of a service and it's implementation (cf. Ports and adapters architecture - https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)).

We will group all declarations inside 'ddd/logic' folder

We will group all implementations inside 'infrastructure/' folder

We will use Dependency Injection mechanism in order to prevent implementation's leak into DDD logic. 

## Consequences

+) It's easier to change the implementation of a service without impacting client which use this service 
 (Enforced by declaration contract)

+) Improve test performance when use memory implementation

-) More code to write (Declaration + Implementation)

-) More difficult to debug because add indirections
