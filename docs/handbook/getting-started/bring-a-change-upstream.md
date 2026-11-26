---
title: Bring a change upstream
type: how-to
status: implemented
order: 30
description: Turn a demonstrated project need into a change to the Factory source.
---

# Bring a change upstream

Start with a case another Factory user can recognize. For example, the currency review belongs to your billing team. If an existing Factory workflow makes it difficult to discover project playbooks, show how that affects the billing review and how someone could see the same problem with a different playbook.

1. **Find the entry point.** Follow [Workflow](../workflow/index.md) to start from a proposal, finding, or existing story. Describe the behavior you need, the evidence from your project, and how a reviewer can tell whether the change works.
2. **Set up a Factory checkout.** Follow [From clone to a passing test run](from-clone-to-a-passing-test-run.md) to see how editable source and the installed copy fit together. Use a separate project when you need to test what an ordinary installation sees.
3. **Locate the owner.** Read [How a Factory run works](../architecture/how-a-factory-run-works.md) to follow a request from the CLI through the playbook, the agent, and the executable checks. Use the [repository map](../architecture/repository-layout.md) to find the source. A discovery problem may involve catalog generation or CLI wiring. A review result may depend on an instruction or a script.
4. **Exercise the behavior.** Refresh the test installation from your checkout and repeat the example that demonstrated the need. Use [Testing](../testing/index.md) to choose focused checks. For CLI wiring, verify discovery and invocation. For a usage change, follow a [CLI event through the stored record and report](../architecture/from-cli-session-to-usage-report.md).
5. **Take it through review.** Include what you changed, how you verified it, and the relevant generated output or test result. Follow the review and merge steps in [Workflow](../workflow/index.md). If the change affects a release, check [Release](../release/index.md).
