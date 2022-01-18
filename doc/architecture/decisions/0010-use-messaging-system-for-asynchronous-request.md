# 10. Use messaging system for asynchronous request

Date: 2021-11-18

## Status

Accepted

## Context

For some features, OSIS need to call external legacy system. 
In order to prevent external system overloading - unavailability, we use a messaging system with queue to reach them.

## Decision

We will use RabbitMQ as default messaging system.

## Consequences

+) Prevent to depend on external system state for a request.

+) Prevent overloading external system.

-) Add some complexities to manage/reason about asynchronous request.
