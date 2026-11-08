---
type: migration-review
title: Migration of the open findings to the classification rules
date: 2026-11-08
status: defects
reviewer: developer-agent
findings_filed: 9
story: ST-0406
scope: the 47 open finding files without review_class and the 26 lines of the three old registers in docs/findings/
---

# Migration of the open findings

**2 of the 47 results are `critical`: BUG-0086 and BUG-0105.** A third file became `critical` as a correction: BUG-0116, see [Correction outside the 47](#correction-outside-the-47). Each of the three needs the stakeholder's checks under `## Possible damage` and both confirmation fields.

Phase 1 classified the findings against commit `40a03a470fc4500e1b325d34b2f6e4b76f0056e2`.

## Results

| Result      |  Count | What the migration wrote                               |
| ----------- | -----: | ------------------------------------------------------ |
| `critical`  |      2 | Finding file stays `open`, with `## Possible damage`   |
| `major`     |      7 | Finding file stays `open`                              |
| `minor`     |     14 | Register file; the finding file is removed             |
| `note`      |     20 | Finding file stays as a record with `status: resolved` |
| no artifact |      4 | Todo entry; the finding file gets `status: deferred`   |
| **Total**   | **47** |                                                        |

The 26 lines of `architecture.jsonl`, `code.jsonl`, and `document.jsonl` became one register file each, with `status: open`. The three `.jsonl` files are removed.

The `release_tag_patterns` setting in `docs/factory-settings.yaml` landed in ST-0405, before this migration.

## Correction outside the 47

BUG-0116 carried `review_class` and `status: resolved`, so it was not among the 47. It recorded `harms_downstream: true` with `severity: major`, and BR-081 computes `critical`. The stakeholder decided on 2026-11-08 to correct the severity backwards. The file now holds `severity: critical`, the same basis, status, and Why line, and a `## Possible damage` section. The defect stood on `dev` from `80bdb99a` to `ff6245eb` and was in no release.

## One changed value in a moved line

The Why line of FAGAN-0032 lacked the marker that BR-087 requires. The stakeholder decided on 2026-11-08 to write the sentence of the rulebook's calibration row. Its meaning stays the same. Every other moved line keeps its values.

## Each migrated finding

| ID                     | Class    | Severity   | What the migration wrote                                               |
| ---------------------- | -------- | ---------- | ---------------------------------------------------------------------- |
| ATAM-0010              | document | `note`     | finding file stays as a record, `resolved`                             |
| ATAM-0011              | code     | `minor`    | `docs/findings/register/code/ATAM-0011.json`; finding file removed     |
| ATAM-0012              | document | `note`     | finding file stays as a record, `resolved`                             |
| ATAM-0013              | document | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0008               | runtime  | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0013               | code     | `major`    | finding file stays `open`                                              |
| BUG-0014               | runtime  | `major`    | finding file stays `open`                                              |
| BUG-0016               | code     | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0020               | code     | `minor`    | `docs/findings/register/code/BUG-0020.json`; finding file removed      |
| BUG-0023               | document | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0029               | code     | `major`    | finding file stays `open`                                              |
| BUG-0065               | runtime  | `major`    | finding file stays `open`                                              |
| BUG-0067               | code     | `minor`    | `docs/findings/register/code/BUG-0067.json`; finding file removed      |
| BUG-0076               | runtime  | `major`    | finding file stays `open`                                              |
| BUG-0079               | runtime  | `minor`    | `docs/findings/register/runtime/BUG-0079.json`; finding file removed   |
| BUG-0086               | code     | `critical` | finding file stays `open`                                              |
| BUG-0088               | code     | `minor`    | `docs/findings/register/code/BUG-0088.json`; finding file removed      |
| BUG-0097               | code     | `minor`    | `docs/findings/register/code/BUG-0097.json`; finding file removed      |
| BUG-0098               | code     | `minor`    | `docs/findings/register/code/BUG-0098.json`; finding file removed      |
| BUG-0099               | code     | `minor`    | `docs/findings/register/code/BUG-0099.json`; finding file removed      |
| BUG-0100               | code     | `minor`    | `docs/findings/register/code/BUG-0100.json`; finding file removed      |
| BUG-0101               | code     | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0104               | code     | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0105               | code     | `critical` | finding file stays `open`                                              |
| BUG-0106               | code     | `minor`    | `docs/findings/register/code/BUG-0106.json`; finding file removed      |
| BUG-0107               | code     | `minor`    | `docs/findings/register/code/BUG-0107.json`; finding file removed      |
| BUG-0108               | code     | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0109               | code     | `note`     | finding file stays as a record, `resolved`                             |
| BUG-0114               | code     | `major`    | finding file stays `open`                                              |
| PROP-0020              | document | `note`     | finding file stays as a record, `resolved`                             |
| PROP-0021              | document | `note`     | finding file stays as a record, `resolved`                             |
| PROP-0022              | document | `note`     | finding file stays as a record, `resolved`                             |
| PROP-0023              | document | `note`     | finding file stays as a record, `resolved`                             |
| PROP-0024              | document | `note`     | finding file stays as a record, `resolved`                             |
| RECON-0018             | code     | `note`     | finding file stays as a record, `resolved`                             |
| RECON-0019             | code     | `note`     | finding file stays as a record, `resolved`                             |
| RECON-0023             | document | `note`     | finding file stays as a record, `resolved`                             |
| RECON-cycle-retirement | document | `note`     | finding file stays as a record, `resolved`                             |
| SEC-0004               | security | `major`    | finding file stays `open`                                              |
| SPEC-0055              | document | `note`     | finding file stays as a record, `resolved`                             |
| SPEC-0056              | document | `minor`    | `docs/findings/register/document/SPEC-0056.json`; finding file removed |
| SPEC-0057              | document | `minor`    | `docs/findings/register/document/SPEC-0057.json`; finding file removed |
| SPEC-0058              | document | `minor`    | `docs/findings/register/document/SPEC-0058.json`; finding file removed |
| RETRO-0001             | none     | none       | `deferred` to T-0408                                                   |
| RETRO-0002             | none     | none       | `deferred` to T-0409                                                   |
| RETRO-0003             | none     | none       | `deferred` to T-0410                                                   |
| RETRO-0004             | none     | none       | `deferred` to T-0411                                                   |

## Each moved register line

| ID         | Class        | Severity | Register file                                        |
| ---------- | ------------ | -------- | ---------------------------------------------------- |
| ATAM-0015  | architecture | `minor`  | `docs/findings/register/architecture/ATAM-0015.json` |
| ATAM-0016  | architecture | `minor`  | `docs/findings/register/architecture/ATAM-0016.json` |
| ATAM-0017  | architecture | `minor`  | `docs/findings/register/architecture/ATAM-0017.json` |
| ATAM-0020  | architecture | `minor`  | `docs/findings/register/architecture/ATAM-0020.json` |
| IMPL-0007  | code         | `minor`  | `docs/findings/register/code/IMPL-0007.json`         |
| FAGAN-0032 | code         | `minor`  | `docs/findings/register/code/FAGAN-0032.json`        |
| BUG-0117   | code         | `minor`  | `docs/findings/register/code/BUG-0117.json`          |
| IMPL-0011  | code         | `minor`  | `docs/findings/register/code/IMPL-0011.json`         |
| IMPL-0012  | code         | `minor`  | `docs/findings/register/code/IMPL-0012.json`         |
| IMPL-0013  | code         | `minor`  | `docs/findings/register/code/IMPL-0013.json`         |
| BUG-0119   | code         | `minor`  | `docs/findings/register/code/BUG-0119.json`          |
| RECON-0027 | document     | `minor`  | `docs/findings/register/document/RECON-0027.json`    |
| RECON-0028 | document     | `minor`  | `docs/findings/register/document/RECON-0028.json`    |
| RECON-0029 | document     | `minor`  | `docs/findings/register/document/RECON-0029.json`    |
| SPEC-0061  | document     | `minor`  | `docs/findings/register/document/SPEC-0061.json`     |
| SPEC-0062  | document     | `minor`  | `docs/findings/register/document/SPEC-0062.json`     |
| SPEC-0063  | document     | `minor`  | `docs/findings/register/document/SPEC-0063.json`     |
| SPEC-0064  | document     | `minor`  | `docs/findings/register/document/SPEC-0064.json`     |
| SPEC-0065  | document     | `minor`  | `docs/findings/register/document/SPEC-0065.json`     |
| SPEC-0066  | document     | `minor`  | `docs/findings/register/document/SPEC-0066.json`     |
| SPEC-0067  | document     | `minor`  | `docs/findings/register/document/SPEC-0067.json`     |
| SPEC-0068  | document     | `minor`  | `docs/findings/register/document/SPEC-0068.json`     |
| SPEC-0069  | document     | `minor`  | `docs/findings/register/document/SPEC-0069.json`     |
| SPEC-0070  | document     | `minor`  | `docs/findings/register/document/SPEC-0070.json`     |
| RECON-0032 | document     | `minor`  | `docs/findings/register/document/RECON-0032.json`    |
| RECON-0033 | document     | `minor`  | `docs/findings/register/document/RECON-0033.json`    |
