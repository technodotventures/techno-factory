# Factory Architecture v0

## Decision

`techno-factory` is the factory's bounded context and codebase — a separate private repository from Coffee, Smartware, expresso, and the personal Control Room — **deployed as a module of the Techno OS monolith** (one deployable, one shell = Optimus OS), NOT as its own service in v1. Module boundaries are enforced as if separate (typed artifacts only, no cross-module internals), so the module can be extracted to its own deployable later if a trigger materializes (enterprise isolation/audit requirement, scale, or a non-founder consumer).

```text
Personal Hermes ──────┐
                      ▼
   TECHNO OS (one system, modular monolith)
   ┌──────────────────────────────────────┐
   │ Shell + decision layer (Optimus OS)  │
   │   Decision Orchestrator · programs   │
   │                                      │
   │ Factory module (this repo's code)    │ ◄────── Coffee SaaS (surface)
   │   gateway/contracts · stations ·     │
   │   evidence · policy · adapters       │
   └──────────────────────────────────────┘
        │                        │
   Pod/Smartware            GitHub / GitLab
   (substrate)              (delivery)
        expresso (language/runtime, peer)
```

## Repository boundary

This repository owns:

- canonical work, event, artifact, identity, and approval contracts;
- authentication and project-scoped authorisation;
- task idempotency and audit history;
- HTTP and MCP adapters over one application service;
- project policy-pack interfaces;
- worker orchestration contracts;
- factory deployment and operations assets.

It does not own:

- Coffee's product UI or general workspace model;
- Smartware's protocol implementation;
- expresso's language/runtime implementation;
- Stevie's private Hermes state;
- the eventual public Protocol Evolution Loop specification.

## Control surfaces and state

Coffee is the authoritative collaborative surface for Techno team activity. Personal Hermes is Stevie's private founder surface. They may address the same factory service, but they do not merge raw conversations or memory.

A work request carries stable organisation, workspace, project, thread, actor, agent, correlation, and idempotency identifiers. Shared continuity comes from work IDs, artifacts, events, decisions, and explicitly approved project context.

Private personal-Hermes context crosses into Coffee/factory state only through an explicit promotion action.

## Adapter decision

The typed application service and API are canonical. MCP is an agent-facing adapter over the same service; it must not reimplement policy or persistence.

- Coffee application traffic: API plus streaming/events.
- Invited Coffee agent teammates: MCP tools bound to a Coffee-issued service identity and project grant.
- Personal Hermes: remote API or MCP tools with an independent client identity and narrower publication controls.

## Authority v0

The tracer supports accepted work and read-only audit access. It does not execute repositories, publish to GitHub, merge, release, deploy, manage credentials, change infrastructure, or amend governance.
