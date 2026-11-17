# Remark Grid Deck — Reference

## Source file

`slides.txt` may start with header lines:

```
% title: Agent Factory
% topic: agent-factory
% date: 2026-11-17
% lang: de
```

`build` writes `<date>_<topic>.html`. `new` sets the date to today; a missing
date means the day of the build. The topic defaults to the title as a slug
(lowercase, words joined by `-`). Change either header to rename the page; the
old page stays and must be removed by hand.

Slides are separated by a line `---` outside a grid block. Remark slide
properties (`class:`, `name:`) and presenter notes after `???` work as usual.

## Grid block

````
```grid COLSxROWS
row 0
row 1
```
````

- Without a size the grid is `62x14`.
- Cell width is 1210 / COLS px, row height 681 / ROWS px, on remark's 1210 x 681 slide.
- The font size follows the cell width (Source Code Pro advances 0.6 em).
- Trailing empty rows are ignored. Missing rows stay empty.

## Markup

| Marker     | Effect    |
| ---------- | --------- |
| `**text**` | bold      |
| `%%text%%` | italic    |
| `__text__` | underline |
| `~~text~~` | grey      |
| `!!text!!` | red       |

Markers take no cells and must be paired within one row.

## Directives

Directives follow the grid block. Coordinates are whole cells, 0-based.

| Directive                     | Effect                                           |
| ----------------------------- | ------------------------------------------------ |
| `@img PATH COL ROW W H`       | image fitted into the rectangle, nothing cropped |
| `@img PATH COL ROW W H cover` | image fills the rectangle, cropped               |
| `@blank COL ROW W H`          | white rectangle that hides the cells below it    |
| `@cross COL ROW W H`          | red cross over the rectangle                     |
| `@footer TEXT`                | small serif line in the bottom right corner      |

Images and blanks are drawn above the text rows. A footer is optional.

## Layout recipes

| Layout                  | Grid  | Text                    | Image                     |
| ----------------------- | ----- | ----------------------- | ------------------------- |
| text left, image right  | 62x14 | columns 2–28            | `@img P 31 0 31 14 cover` |
| image left, text right  | 62x14 | from column 33          | `@img P 0 0 31 14 cover`  |
| text left, image right  | 99x25 | columns 4–45            | `@img P 50 0 49 25 cover` |
| image left, text right  | 99x25 | from column 53          | `@img P 0 0 49 25 cover`  |
| two text columns        | 99x25 | columns 4–46 and 52–94  | —                         |
| full bleed with caption | 62x14 | caption on row 12       | `@img P 0 0 62 11 cover`  |
| title                   | 40x10 | from column 3, rows 1–8 | —                         |

## Checks

`remark-deck check` and the page itself run the same checks:

- row count against the grid, and each row's width without markers
- paired markers in each row
- directive arguments and bounds; `@img` file exists
- grid block closed; no tabs; no `</script>` in the source

In the browser, a slide that fails gets a red frame and the problem printed on it.

## Licences

`new` copies the licences of Source Code Pro and Cormorant Garamond (SIL Open
Font License 1.1) and of remark (MIT) into `DIR/licenses/`. Keep them with the
fonts and `remark.min.js` when the deck is passed on.

## Pitfalls

- Characters above U+00FF are each held to one cell, so a fallback font cannot
  shift the row. Emoji still look out of place; prefer box characters and ASCII.
- A row that only reads `---` inside a grid block stays a row; outside it splits slides.
- `<date>_<topic>.html` is generated. Edit `slides.txt` and rebuild.
- The source is `.txt` on purpose. Markdown formatters such as the mdformat hook
  rewrite `---` and directive lines in a `.md` file and break the deck.
