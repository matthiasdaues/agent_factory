---
name: remark-grid-deck
description: Build a remark.js presentation deck on a monospace character grid that fills the 16:9 slide — one source line per row, one character per cell, images placed on whole cells. Use when someone asks for a presentation, slide deck, slides, or a remark deck, or wants slides in a monospace, terminal or ASCII-diagram look.
category: utility
---

# Remark Grid Deck

A deck is a folder with `slides.txt`, the source, and `<date>_<topic>.html`, the
page built from it, for example `2026-11-17_agent-factory.html`. The command
`.agent-factory/factory/scripts/remark-deck` creates the folder, checks the
source and builds the page. The page runs offline: fonts, remark and their
licences are copied into the folder.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Commands

```bash
D=.agent-factory/factory/scripts/remark-deck
$D new path/to/deck --title "Agent Factory" --lang de   # starter deck
$D new path/to/deck --title "Agent Factory" --topic af  # shorter file name
$D new path/to/deck --sample                            # ten sample slides
$D check path/to/deck                                   # grid check only
$D build path/to/deck                                   # check, then write the page
```

Exit 0 means done and no problem found. Exit 1 means the grid check found a
problem; `build` then writes no page. Exit 2 means a precondition failed.

A slide in `slides.txt`:

````
```grid 62x14

  **TEXT LEFT,**
  **IMAGE RIGHT**

  Text: columns 2 to 28.
```
@img media/photo.jpg 31 0 31 14 cover
@footer by matthias daues
````

## Workflow

1. Agree on the outline with the user: one point per slide, in the order told.
2. Ask where the deck goes. `new` does not overwrite an existing `slides.txt`.
3. Run `new`. Copy the user's images into `DIR/media/`.
4. Pick a grid per slide from the table below. Write the rows in `slides.txt`.
5. Run `build`. Fix every reported problem and build again until it reports 0.
6. If a headless Chrome or Chromium is at hand, screenshot
   `file://DIR/<date>_<topic>.html#N` at 1210 x 681 and look at each slide.
7. Give the user the path of the page. The `g` key shows the grid in the browser.

## Grids

| Grid              | Use                                     |
| ----------------- | --------------------------------------- |
| `40x10`           | title, one statement                    |
| `62x14` (default) | text slide, text and image side by side |
| `80x24`           | terminal session, code                  |
| `99x25`           | diagram, wide split, two text columns   |
| `132x36`          | dense table or diagram                  |

Any `COLSxROWS` works. Every grid fills the whole slide, so content in column 0
touches the edge. Keep a margin of two to four columns unless an image bleeds.

## Writing rows

- Count cells, not keystrokes: the markers `**` `~~` `__` `!!` `%%` take no cells.
- Use spaces only. A tab breaks the column count.
- For two columns or boxes, generate the rows with a short script that pads each
  segment to its column. Hand-padding drifts.
- Box characters `─│┌┐└┘├┤┬┴┼` join from row to row; use them for diagrams.

The full syntax, layout recipes and pitfalls are in [REFERENCE.md](REFERENCE.md).
Ten working slides are in [examples/sample.txt](examples/sample.txt).
