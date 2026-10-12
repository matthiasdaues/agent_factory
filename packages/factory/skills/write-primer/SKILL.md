---
name: write-primer
description: >-
  Write a short primer for a proposal: a plain-language introduction that lets
  a reader who knows nothing about the project follow the full document.
  Writes it into the proposal's Primer section.
category: requirements
version: 0.1.0
---

# Write Primer

A primer prepares a newcomer for a proposal. They read it once, before the
full document. Afterwards they can follow the proposal and explain the core
idea to a colleague.

A primer is not a summary. It gives the reader the map, not every street. The
full proposal holds the details.

Use this skill after `draft-proposal` has filled the proposal, and again when
a review pass changes the design.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Run it fresh

The author of a proposal knows too much to see what a newcomer lacks. Run this
skill in a fresh subagent that has not seen the conversation behind the
proposal. Give it the proposal path and this skill. It returns the primer
text; the calling session writes it into the proposal.

## How it should sound

Write the way one normal person explains a topic to another over a desk: calm,
plain, in connected sentences. Not a pitch, not a summary slide, not a spec.

- Use plain words. Name every right, role, and rule in everyday language. Use
  no code-formatted identifiers, table names, role keys, or ticket IDs.
- Spell out every abbreviation. Explain every right or term you name, or leave
  it out.
- Write mostly prose paragraphs. Use a list only for items that really are a
  list, such as separate rules or open questions. Use no bold section labels.
- Each sentence is complete, short, and active. No fragments, no semicolon
  chains, no arrows.
- Connect the ideas: say why one thing leads to the next ("so", "because",
  "that is why"). A newcomer needs the links, not only the facts.
- Use one concrete example and carry it through. Build it only from names and
  facts in the proposal. Do not invent numbers, sizes, or circumstances.
- No buzzwords and no drama: no "robust", "seamless", "leverage", "powerful",
  "crucial", "ensures", and no rhetorical flourishes.

## Procedure

### 1. Extract (do not print)

Read the proposal in full. Read linked documents only to settle a fact the
proposal leaves unclear. Note, each with the sentence that supports it:

1. The 3–5 terms a newcomer needs first, and how they relate (which contains
   which, how many of each).
2. The framing concepts the design rests on but treats as known (views,
   layers, classes, splits).
3. The problem, as a concrete situation a person runs into.
4. The core idea, in one sentence.
5. Every actor the rules mention, including special roles that set up the
   structure or stand outside the normal rules.
6. The major rules, each with the real case or reason that drives it.
7. The alternative a newcomer from the predecessor system or common practice
   would suggest, and why the proposal does not take it.
8. What the design keeps over time.
9. The open questions.

Drop anything you cannot support from the proposal text. Add nothing from
general knowledge or inference.

### 2. Rank (do not print)

Sort the items from step 1 into two groups.

**Must appear:** the framing concepts, every actor, the rules the core idea
depends on, and the open questions that block the design.

**May be grouped or left out:** the remaining rules and open questions. Group
them in one sentence ("The proposal also settles who may publish and who may
move Tasks.") or leave them to the full proposal. A primer that names
everything has become a summary.

### 3. Write

Follow this order, as plain paragraphs:

1. The setting: what the system is and the first terms, defined in passing.
2. The problem, told as a situation.
3. The framing concepts, and where this proposal's subject fits among them.
4. The idea and how it works, using the running example.
5. The obvious alternative and why it is not taken, in one or two sentences.
6. The must-appear rules. Give each rule its reason in the same or the next
   sentence. Name every actor.
7. What the design keeps over time.
8. The blocking open questions.

### 4. Check

1. Length: 400–500 words. If longer, cut from the "may be grouped or left out"
   group first. Never shorten by compressing sentences, dropping linking
   words, or using identifiers.
2. Check every claim against the proposal, including every detail in the
   running example. Fix or remove what the text does not support.
3. Check that no term is used before it is explained, that every abbreviation
   is spelled out, and that every named right is explained.
4. Check that every must-appear item from step 2 is present, and that each
   rule has its reason.
5. Final pass: assume the text still reads like buzzword bingo or a breathless
   pitch. Find those sentences and rewrite each one the way a colleague would
   say it out loud.

### 5. Place

The calling session writes the primer into a `## Primer` section directly
below the proposal's title, before `## Summary`. It replaces the section if
one exists. The primer describes the proposal as it stands; it carries no
history of earlier versions.

## Validation

Run `.agent-factory/factory/scripts/mdformat --number docs/proposals/<name>.md`
after writing the section.

## Completion

The proposal has a `## Primer` section of 400–500 words that passes every
check in step 4, and `mdformat` is clean.
