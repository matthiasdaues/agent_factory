---
title: Migrate old usage transcripts
type: how-to
status: implemented
order: 30
description: Convert the transcript store of version 1.13.0 or earlier, which kept a full copy per capture.
---

# Migrate old usage transcripts

Version 1.13.0 and earlier stored a full copy of the transcript for each capture. Later versions store each chain once and append to it, as [How usage capture works](usage-capture.md#records-and-transcripts) explains.

1. See what the migration would do:

   ```bash
   .agent-factory/factory/scripts/migrate-usage-transcripts
   ```

2. Wait until no capture is pending.

3. Run the migration:

   ```bash
   .agent-factory/factory/scripts/migrate-usage-transcripts --apply
   ```
