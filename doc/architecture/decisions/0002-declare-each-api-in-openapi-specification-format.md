# 2. Declare each API in OpenAPI Specification format

Date: 2021-11-18

## Status

Accepted

## Context

OSIS (Open Student Information System) is designed to manage the core business of the university. 
External application can leverage services provided by OSIS. 

## Decision

We will declare all services and 'how to use them' in a YAML file (schema.yml) following 
the OpenAPI Specification 3.0 syntax.

## Consequences

+) Allow external application to use services provided by OSIS
+) Allow SDK generation (cf. https://github.com/OpenAPITools/openapi-generator)
