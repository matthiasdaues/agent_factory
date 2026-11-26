---
title: Add a project playbook
type: how-to
status: implemented
order: 20
description: Install, try, and maintain a billing review playbook for your team.
---

# Add a project playbook

Use this example in a project with Agent Factory installed. You will keep a copy in the project repository and install a second copy for the CLI to discover.

## Write and register the playbook

Create `team-playbooks/billing-review.md` and track it in your project. This example assumes that your team expects the CSV to preserve each invoice's currency.

```markdown
---
title: Billing review
category: orchestration
type: runbook
scenario: billing-review
version: 1.0.0
---

# Billing review

Review a billing change for currency mistakes before the team accepts it.

1. Ask for the change to review and the example invoice or fixture.
2. Compare the invoice currency with the CSV row and its test expectations.
3. Report each mismatch with the input, the actual result, and the expected
   result. If the evidence is missing, say what you need to complete the review.
4. Show the report to the maintainer. Let them decide whether to accept the change.
```

Run these commands from the project root:

```bash
cp team-playbooks/billing-review.md .agent-factory/factory/playbooks/
.agent-factory/factory/scripts/index-lint
```

In your coding CLI, open **Project Work**, then choose **Run an agent or playbook directly** and select **Billing review**.

## Check discovery and review separately

First, confirm the playbook appears in the selection list. If it is missing, check that the installed Markdown file and its entry in `.agent-factory/factory/INDEX.yaml` exist. If the CLI still misses it, check the [CLI integration](../cli-integrations/index.md) to see which catalog it reads.

Try a sample invoice in EUR with a CSV row labeled EUR. Then use the same invoice with a CSV row labeled USD. Ask for the review report in each case. The first should have no currency mismatch. The second should show the invoice currency, the incorrect CSV value, and the expected value. If the playbook runs but reaches the wrong conclusion, check the instructions and the evidence you supplied.

## Share it and keep it through updates

Commit the maintained playbook and its setup instructions in your project. Teammates can register their own installed copies with the same commands. The installed copy lives under the local, Git-ignored `.agent-factory/` directory.

The updater can stop when it finds local changes in the Factory installation. If you choose to proceed with `--force`, it saves changed or added files under `.agent-factory/user-changes/<timestamp>/` and installs the new Factory copy. After the update, repeat the registration commands from the tracked playbook and run both examples again. See [Update the Factory](../../../packages/factory/docs/handbook/installation-and-updates/update-the-factory.md) for the update procedure.
