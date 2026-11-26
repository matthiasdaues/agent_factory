---
title: Configure transcript retention
type: how-to
status: implemented
order: 20
description: Choose whether usage capture stores transcript text or only the token totals.
---

# Configure transcript retention

Usage capture stores the text of each transcript next to its records. To keep the token totals and the audit context but store no transcript text, set the retention to `omit`.

1. Set the retention at initialization:

   ```bash
   .agent-factory/factory/scripts/init-factory --usage-transcript-retention omit
   ```

   The values are `full` and `omit`.

2. To override the setting for a while, set the environment variable `AGENT_FACTORY_USAGE_TRANSCRIPT_RETENTION` to `full` or `omit`. A direct call of the capture script also takes the option.

3. Check a new record. With `omit`, its `transcript_ref` carries the marker `content-omitted` in `span` and no byte range.

On a platform where owner-only file modes cannot be enforced, capture omits the text on its own. An invalid value also falls back to `omit`.
