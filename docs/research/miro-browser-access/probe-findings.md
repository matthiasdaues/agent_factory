# Miro Browser Access: Probe Findings

These findings come from thirteen probes against Miro on 2026-11-20. A Playwright
browser with its own profile signed in to Miro, and the probes read and wrote
through the board page. They were made for the
[SaaS browser switchboard proposal](../../proposals/saas-browser-switchboard.md),
which leaves Miro out of its scope. The test board is kept by the stakeholder
for later probes.

## Reading

Miro draws its board on a canvas, and its WebSocket traffic is binary and
undocumented. The skill reads the board through Miro's accessibility outline
instead, the text view Miro offers for screen readers . The skill
turns the outline on through its button, with a key press on the focused
button. Then it moves the focus through the outline by script, with no key
presses on the board, until every item has been rendered.

For each item, the outline gives:

| Field          | Example                                  |
| -------------- | ---------------------------------------- |
| item ID        | `3458764691092562104`                    |
| text           | `S1 plain yellow.`                       |
| type and color | `light yellow sticky note`               |
| position       | `N of M` within its parent               |
| box            | left, top, width, height in board pixels |
| parent         | the frame or group that holds the item   |

- **Coordinates.** A top-level item's box is in board coordinates. A child's
  box is relative to its parent frame or group, so the skill adds the parent's
  position to get board coordinates. The box matches Miro's selection frame,
  which is slightly larger than the drawn item.
- **Links.** The item ID gives the link `<board URL>?moveToWidget=<item ID>`,
  which opens the board centred on that item.
- **Comments.** A comment appears as its own item, with its text, its author,
  and the item it is attached to. The replies appear only in the open thread.
  The skill opens a thread with a key press on the comment's outline element
  and reads each entry's author, text, and relative time, such as
  "7 minutes ago".
- **New replies.** The thread gives no exact date and no reply ID. The skill
  keeps the number of entries per thread in its local log, and treats entries
  beyond that number as new.

The WebSocket route is ruled out: the board talks to
`wss://miro.com/rtc-gateway/mux`, and its messages are binary. The public REST
API at `api.miro.com` does not answer a call from inside the board page.

## Writing

The skill keeps an offline layout model of the board and plans each write in
it. The screen only carries out the plan:

1. **Sync.** The skill reads the whole outline into the layout model, together
   with the board's `updatedAt`.
2. **Plan.** The skill fixes the new item's box in board coordinates and checks
   it against every box in the model, with a margin of 30 board pixels.
3. **Open a targeted view.** The skill opens the board with
   `?moveToViewport=<x>,<y>,<width>,<height>` around the planned box. Miro
   centres that area in the whole window and ignores its side panels, so the
   skill widens the area on the side where a panel covers the canvas.
4. **Check the view.** The skill fits the mapping from board to screen
   coordinates with the outline's screen boxes. It acts only when the fitted
   scale matches Miro's zoom label, every corner of the planned box lies on
   the canvas, and `updatedAt` still matches the sync. Otherwise it syncs and
   plans again.
5. **Place.** The skill creates the item with Miro's tool. A sticky note is
   created centred on the click point. Its size follows from the zoom: at
   150 %, a new sticky note measures 107.46 × 123.12 board pixels. So the
   skill sets the zoom with Miro's zoom buttons to get the planned size.
6. **Check the result.** The skill syncs again and compares the new item's box
   with the plan.

A resize after the placement is not part of the procedure. The plan fixes the
size, and the placement produces it.

Two failed resize attempts showed why the view check needs the zoom label: a
mapping fitted from the outline's screen boxes can agree with itself and still
differ from the canvas. In both attempts the drag moved the note instead of
resizing it. `Ctrl + Z` in the same browser session undid the move.

Moving the view: `?moveToViewport=<x>,<y>,<width>,<height>` and
`?moveToWidget=<item ID>` work, and so do Miro's zoom buttons. The mouse wheel
did not move the view. A drag with the space bar held moved it by an amount
that did not match the drag.

## Known limits

- **Connector ends.** The outline gives a connector's label and box, but not
  the two items it connects.
- **Reply dates.** A thread shows only relative times, so the skill cannot
  order replies across threads.
- **Outline layer.** The outline is a separate layer of page elements. After a
  `moveToViewport` jump, its scale differed from the canvas until the view was
  changed again with the zoom buttons. Step 4 of the writing procedure catches
  that case with the zoom label.
- **Accessibility setting.** Turning the outline on may save the setting in
  the user's Miro account.

## Open points

- **Thread reply.** Writing a reply in a comment thread is untested.
- **Sticky note size and zoom.** At 150 %, a new sticky note measured
  107.46 × 123.12 board pixels. At 75 %, it measured 212.93 × 243.96. The
  on-screen widths differ by 1.5 pixels, so the relation is close to, but not
  exactly, a fixed size on screen.
- **Other item types.** Shapes, text, frames, cards, connectors, text edits,
  and moves each need a probe of their creation or edit step. Composing whole
  boards is filed as
  [T-0416](../../spec/work/todo.md#t-0416--write-a-canvas-composer-proposal-with-drawio-on-confluence-first).
