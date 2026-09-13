---
title: Vue 3 Composition API
version: 1.0.0
---

# Vue 3 Composition API

Core principles of the Vue 3 Composition API with `<script setup>`.

## Reactivity model

- `ref()` for primitive values, `reactive()` for objects.
- Derive everything possible with `computed()`. Keep source state minimal.
- Use `watch()` / `watchEffect()` for side effects only.

## Single-File Component structure

Order: `<script setup>` → `<template>` → `<style scoped>`.

## Composables

Extract reusable stateful logic into `useXxx()` functions. A composable
returns reactive state and methods. Keep the API small and typed.

## Component data flow

- Props down, events up (`defineProps`, `defineEmits`).
- `v-model` for true two-way binding contracts.
- `provide` / `inject` for deep-tree dependencies.

## Component sizing

Split when a component has more than one responsibility. Entry and route
view components stay thin — composition surfaces, not feature hosts.
