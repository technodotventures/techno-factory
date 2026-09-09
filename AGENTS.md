# Techno Factory — AGENTS.md

## Purpose

This repository contains Techno Ventures' secure agentic software-factory gateway and recursive protocol-development kernel. Coffee is the collaborative human/team control surface. Smartware and expresso are peer projects with separate policy packs, queues, repositories, and evaluations.

## Architecture rules

- One canonical application/service layer backs HTTP API and MCP adapters.
- Keep personal-agent sessions, Coffee threads, and factory execution state explicitly separated.
- Shared continuity uses typed artifacts, stable task IDs, events, and approved project context—not merged raw chat histories.
- Every mutating request is authenticated, authorised, project-scoped, idempotent, and auditable.
- Never store secrets in the repository. Runtime secrets come from environment or an approved secret broker.
- Repository code, dependencies, prompts, issues, and model output are untrusted.
- Agents may autonomously research, evaluate, test, and create bounded draft artifacts. Merge, release, deployment, credentials, infrastructure, and governance remain explicit human gates.
- Do not add direct production deployment or unrestricted GitHub credentials to workers.

## Engineering conventions

- Node.js 22+ and TypeScript ESM.
- Use strict TypeScript and Zod at external boundaries.
- Use Vitest and strict RED → GREEN → REFACTOR TDD for behaviour changes.
- Prefer vertical tracer slices over framework scaffolding.
- Keep HTTP/MCP transport logic thin; domain behaviour belongs in application services.
- Tests must use isolated temporary state and cannot depend on real credentials or networks.
- Run `npm test`, `npm run typecheck`, and `npm run build` before reporting completion.

## Repository boundaries

This repo owns the factory gateway, task/event/artifact contracts, policy engine, adapter surfaces, and local development/deployment manifests. It does not own Coffee product UI, Smartware protocol implementation, expresso runtime implementation, or the eventual public Protocol Evolution Loop specification.
