---
id: 0036
status: accepted
evaluation: none
---

# The TypeScript tests run as a `node:test` suite

## Context

The guard entry of the Pi extension and the guard-only OpenCode plugin are
TypeScript ([ADR-0035](0035-guard-human-fields-in-every-cli.md)). Their tests
need a runner that a gate can call. `docs/testing.yaml` declares no
TypeScript suite today, so no gate runs the 23 tests that already exist under
`packages/factory/config/extensions/__tests__/` (FC-QG25).

Those tests already use `node:test`. They pass with
`node --experimental-strip-types --import ./envelope-loader.mjs --test`, which
needs Node 22.6 or later and no package. A pytest wrapper around that command
or a switch to vitest or bun would also run them. The wrapper adds a layer
that runs the same command. Vitest and bun add a dependency and rewrite tests
that already pass.

## Decision

The TypeScript tests in `packages/factory/config/**/*.test.ts` run as one
`node:test` suite on Node 22.6 or later, with no new dependency (DEC-62). The
test-strategy agent writes the suite entry into `docs/testing.yaml` after the
stakeholder confirms it.

## Consequences

- Node 22.6 or later becomes a prerequisite for this repository's own test
  run. A consumer project that installs the Factory does not run these tests.
- The guard tests of Pi and OpenCode join the existing tests in one suite, so
  one gate runs all TypeScript tests.
- The flag `--experimental-strip-types` may change in a later Node release.
  The suite command then changes in `docs/testing.yaml` only.
