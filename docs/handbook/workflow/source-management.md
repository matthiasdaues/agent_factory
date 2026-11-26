---
title: Manage a fork and its Factory installs
type: concept
status: implemented
order: 10
description: Keep upstream, fork changes, and project installations traceable.
---

# Manage a fork and its Factory installs

Keep three locations straight. **Upstream** is the repository the Factory maintainers release from. **Your fork** is a Git repository where you can propose changes or maintain patches. **The installed Factory** is the copy a project runs from `.agent-factory/factory/`. Git manages the history of the first two. The installer and updater manage the third.

## Send a contribution upstream

In a clone of your fork, a common naming convention is `origin` for your fork and `upstream` for the project. Fetch upstream and keep the branches you use as mirrors free of your own commits. Put each contribution on a separate branch and submit it to the branch the project expects. For Factory feature work, start from `dev` and follow the [feature branch policy](../../../packages/factory/rulebooks/conventions/branching-policy.md#feature-branch). Confirm the target before opening the change for review.

```text
Upstream --fetch--> Local clone --push topic branch--> Your fork
    ^                                                      |
    +--------------------- pull request -------------------+
```

## Maintain a downstream fork

If a team needs to ship Factory changes it will carry across releases, record the upstream tag or commit it builds on. Keep each carried change reviewable and record why it exists, who owns it, and whether upstream has accepted it. Revisit that list when you update. A team-specific procedure can often live in a [project playbook](../getting-started/add-a-project-playbook.md). A reusable extension point can be a [contribution upstream](../getting-started/bring-a-change-upstream.md).

A small patch stack can be replayed on each new upstream release if its maintainers can coordinate the history rewrite. A shared downstream branch can merge upstream to keep its published history. In either case, review the resulting changes and run both the upstream tests and the downstream checks before updating consumer projects. For a backport, record the upstream commit it came from.

## Update a project installation

A downstream team integrates upstream changes in its fork, then updates project installations from the source it has tested.

```text
Upstream tag or commit
          |
          v
Downstream source + carried patches
          |
          | install or update
          v
Project copy at .agent-factory/factory/
```

The install manifest records the source the updater uses by default. Review the candidate source and version before approving an update. Switching between local and remote sources, or to another remote base URL, requires separate approval.

With a checksum baseline, `update-factory --check` reports modified, added, and removed files in the installed tree. An update stops on those changes unless you use `--force`. A forced update saves modified and added files under `.agent-factory/user-changes/<timestamp>/` before replacing the installed tree. It does not replay them or carry forward deletions. Keep the maintained copy in your project repository or downstream fork, then reinstall and test the changes you still need. For the commands, see [Update the Factory](../../../packages/factory/docs/handbook/installation-and-updates/update-the-factory.md).
