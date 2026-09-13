---
name: vue-best-practices
category: implementation
description: Project-specific Vue conventions for packages/server. Load before any Vue/frontend implementation task.
---

# Vue Best Practices

Read `rulebooks/principles/vue3-composition-api.md` before proceeding.
Skip only if you can state the Composition API reactivity model, SFC
structure, and composable pattern without reading.

Source: <https://www.ui-skills.com/skills/vuejs-ai/vue-best-practices>

## Project stack

Vue 3 + Composition API + `<script setup lang="ts">`. If the project
uses Options API or JSX, load the corresponding skill if available.

## Project-specific deviations

- Prefer feature folder layout (`components/<feature>/...`,
  `composables/use<Feature>.ts`) when adding more than one component.
- Entry/root and route view components stay thin — composition surfaces,
  not feature hosts. Single-file exception only for small throwaway demos
  with explicit justification.
- Performance optimization is a post-functionality pass. Do not optimize
  before core behavior is verified.
