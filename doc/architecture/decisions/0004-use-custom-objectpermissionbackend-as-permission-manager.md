# 4. Use custom ObjectPermissionBackend as permission manager

Date: 2021-11-18

## Status

Accepted

## Context

OSIS support a wide range of groups/roles. 
The RBAC (role based access) provided by Django Framework is not enough to allow/deny permission 
related to ressource's attributes.

Selected solutions : 
 - Django Guardian: https://django-guardian.readthedocs.io/en/stable/
 - Django Rules: https://github.com/dfunckt/django-rules
 - Custom

## Decision

We will create a custom solution (called OSIS-Role) heavily based on Django Rules.

We won't take Django Guardian because all permissions for a resource is saved as entries (tuple user/resource) into a table.
It will be difficult to maintain all rules for all different roles. 

## Consequences

+) Consistent way of managing role and permission.

+) Attribute-base access control is easier thanks to Django Rules with predicates. No data to maintain

-) Attribute-base access control computed on-the-fly is resource intensive.