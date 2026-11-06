---
id: ATAM-0012
source: atam-review
severity: medium
category: defect
artifact: docs/arc42/08_crosscutting_concepts.md#818-id-allocation
status: open
owner: architecture-agent
traces: [ADR-0031, QS-18, BR-072, DEC-23]
---

# A claim can hang instead of failing with a named reason

**What is wrong:** Section 8.18 says "A failed claim stops" and names the reason. The Claim Lifecycle moves to `FAILED` on `RemoteUnreachable` and `FetchRefused`. That assumes git returns. Neither the architecture nor the `next-id` contract gives the fetch or the push a time limit. Neither says how git must behave when it wants credentials it does not have.

Take an agent that runs `next-id FAGAN` against an HTTPS `origin`. The user's global setup has no cached credentials. Depending on the machine, git asks for a user name on the terminal, or a credential manager opens a login window, or ssh asks for a key passphrase. Each of these waits for a person who is not there. A remote that drops packets has the same effect: the fetch waits until the operating system gives up, which can take minutes. The agent's command then hangs or is killed by the CLI's own time limit. Either way, `next-id` names no reason. This review did not check which of these prompts appears in a Claude Code or Codex shell. A test on such a shell would settle it.

The retry loop makes the case worse. Ten stale leases with a slow remote take ten fetch and push round trips plus up to ten seconds of waiting, and the architecture gives no bound for the whole claim.

**Fix:** Decide in section 8.18, and in ADR-0031 if the stakeholder wants it recorded there, how `next-id` keeps a claim bounded. One way: `next-id` runs every git call with `GIT_TERMINAL_PROMPT=0` and `GIT_SSH_COMMAND="ssh -o BatchMode=yes"`, and stops a git call after a fixed time, such as 30 seconds, as `RemoteUnreachable`. Leave the prompt on for `next-id --seed`, which a person runs. Then file the contract change with the domain-modeling agent: a time limit in the `next-id` contract, and a timeout event in the Claim Lifecycle.
