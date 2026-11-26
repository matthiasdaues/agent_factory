---
title: CLI integrations
type: concept
status: implemented
order: 50
description: This chapter explains how to wire a new CLI into the factory.
---

# CLI integrations

CLI integrations let each supported assistant discover Factory instructions and invoke the hooks or extensions that it supports. Start in `packages/factory/config/` for source templates, hooks, and extensions. The [installer](../../../packages/factory/scripts/init-factory) selects and places the integration files in the target project. Some CLIs also receive generated agent definitions, such as those produced by [generate-codex-agents](../../../packages/factory/scripts/generate-codex-agents).

When changing wiring, trace the path from the source template or generator to the file the CLI reads. Check the installation in a disposable project before trying the affected action. If you are changing a usage hook, [follow a record from the CLI to the usage report](../architecture/from-cli-session-to-usage-report.md).

<!-- handbook-index:start -->

<!-- handbook-index:end -->
