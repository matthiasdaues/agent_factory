---
name: vue-best-practices
category: implementation
description: Core Vue development best practices for component architecture, reactivity, and maintainable code. Load before any Vue/frontend implementation task in packages/server.
---

# Vue Best Practices Workflow

Source: <https://www.ui-skills.com/skills/vuejs-ai/vue-best-practices>

Use this skill as an instruction set. Follow the workflow in order unless the user explicitly asks for a different order.

## Core Principles

- Keep state predictable: one source of truth, derive everything else.
- Make data flow explicit: Props down, Events up for most cases.
- Favor small, focused components: easier to test, reuse, and maintain.
- Avoid unnecessary re-renders: use computed properties and watchers wisely.
- Readability counts: write clear, self-documenting code.

## 1) Confirm architecture before coding (required)

- Default stack: Vue 3 + Composition API + `<script setup lang="ts">`.
- If the project explicitly uses Options API, load `vue-options-api-best-practices` skill if available.
- If the project explicitly uses JSX, load `vue-jsx-best-practices` skill if available.

### 1.1 Plan component boundaries before coding (required)

Create a brief component map before implementation for any non-trivial feature.

- Define each component's single responsibility in one sentence.
- Keep entry/root and route-level view components as composition surfaces by default.
- Move feature UI and feature logic out of entry/root/view components unless the task is intentionally a tiny single-file demo.
- Define props/emits contracts for each child component in the map.
- Prefer a feature folder layout (`components/<feature>/...`, `composables/use<Feature>.ts`) when adding more than one component.

## 2) Apply essential Vue foundations (required)

These are essential, must-know foundations. Apply all of them in every Vue task.

### Reactivity

- Keep source state minimal (`ref`/`reactive`), derive everything possible with `computed`.
- Use watchers for side effects if needed.
- Avoid recomputing expensive logic in templates.

### SFC structure and template safety

- Keep SFC sections in this order: `<script>` → `<template>` → `<style>`.
- Keep SFC responsibilities focused; split large components.
- Keep templates declarative; move branching/derivation to script.
- Apply Vue template safety rules (`v-html`, list rendering, conditional rendering choices).

### Keep components focused

Split a component when it has more than one clear responsibility (e.g. data orchestration + UI, or multiple independent UI sections).

- Prefer smaller components + composables over one "mega component".
- Move UI sections into child components (props in, events out).
- Move state/side effects into composables (`useXxx()`).

Apply objective split triggers. Split the component if any condition is true:

- It owns both orchestration/state and substantial presentational markup for multiple sections.
- It has 3+ distinct UI sections (for example: form, filters, list, footer/status).
- A template block is repeated or could become reusable (item rows, cards, list entries).

Entry/root and route view rule:

- Keep entry/root and route view components thin: app shell/layout, provider wiring, and feature composition.
- Do not place full feature implementations in entry/root/view components when those features contain independent parts.
- For CRUD/list features (todo, table, catalog, inbox), split at least into:
  - feature container component
  - input/form component
  - list (and/or item) component
  - footer/actions or filter/status component
- Allow a single-file implementation only for very small throwaway demos; if chosen, explicitly justify why splitting is unnecessary.

### Component data flow

- Use props down, events up as the primary model.
- Use `v-model` only for true two-way component contracts.
- Use provide/inject only for deep-tree dependencies or shared context.
- Keep contracts explicit and typed with `defineProps`, `defineEmits`, and `InjectionKey` as needed.

### Composables

- Extract logic into composables when it is reused, stateful, or side-effect heavy.
- Keep composable APIs small, typed, and predictable.
- Separate feature logic from presentational components.

## 3) Consider optional features only when requirements call for them

### 3.1 Standard optional features

Do not add these by default. Use only when the requirement exists.

- **Slots**: parent needs to control child content/layout.
- **Fallthrough attributes**: wrapper/base components must forward attrs/events safely.
- **`<KeepAlive>`**: stateful view caching.
- **`<Teleport>`**: overlays/portals.
- **`<Suspense>`**: async subtree fallback boundaries.
- **Animation**: pick the simplest approach that matches the required motion behavior.
  - `<Transition>` for enter/leave effects.
  - `<TransitionGroup>` for animated list mutations.
  - Class-based animation for non-enter/leave effects.
  - State-driven animation for user-input-driven animation.

### 3.2 Less-common optional features

Use these only when there is explicit product or technical need.

- **Directives**: behavior is DOM-specific and not a good composable/component fit.
- **Async components**: heavy/rarely-used UI should be lazy loaded.
- **Render functions**: only when templates cannot express the requirement.
- **Plugins**: when behavior must be installed app-wide.
- **State management patterns**: app-wide shared state crosses feature boundaries.

## 4) Run performance optimization after behavior is correct

Performance work is a post-functionality pass. Do not optimize before core behavior is implemented and verified.

- Large list rendering bottlenecks → virtualize large lists.
- Static subtrees re-rendering unnecessarily → `v-once` / `v-memo` directives.
- Over-abstraction in hot list paths → avoid component abstraction in lists.
- Expensive updates triggered too often → review watcher/computed usage.

## 5) Final self-check before finishing

- Core behavior works and matches requirements.
- Reactivity model is minimal and predictable.
- SFC structure and template rules are followed.
- Components are focused and well-factored, splitting when needed.
- Entry/root and route view components remain composition surfaces unless there is an explicit small-demo exception.
- Component split decisions are explicit and defensible (responsibility boundaries are clear).
- Data flow contracts are explicit and typed.
- Composables are used where reuse/complexity justifies them.
- Moved state/side effects into composables if applicable.
- Optional features are used only when requirements demand them.
- Performance changes were applied only after functionality was complete.
