#!/usr/bin/env bash
# demo.sh — Two demonstrations of Agent Factory's playbook execution.
#
# Part 1: Human-in-the-loop (you press enter, you check gates, you advance)
# Part 2: Orchestrated (run-playbook does exactly what you did, unattended)
#
# Both use the same FSM. The only difference is who presses "enter."
#
# Every action is logged to .agent-factory/audit.log — the same file the
# real orchestrator and gate scripts use. The AF_SESSION_LOG environment
# variable (see factory/scripts/_session_log.py) activates this: gate
# scripts automatically append JSONL records when it is set.
#
# The demo adds its own structured entries alongside the gate records,
# so you get a complete timeline: setup, dispatch, human actions, gate
# results, advances, and halts — all in one file, all in JSONL.
#
# Usage:
#   cd agent_factory
#   bash orchestrator/demo.sh
#
# Output:
#   Interactive terminal walk-through.
#   Session log: .agent-factory/audit.log (inside the temporary demo project)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_DIR="$(mktemp -d)"
trap 'rm -rf "$DEMO_DIR"' EXIT

# ─── Colors ──────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ─── Session log ─────────────────────────────────────────────────────────
# All logging goes to .agent-factory/audit.log as JSONL.
# AF_SESSION_LOG is exported so gate scripts (_session_log.py) also write here.
# The demo's own entries use the same format: one JSON object per line.

session_session_log_init() {
    mkdir -p "$DEMO_DIR/.agent-factory"
    export AF_SESSION_LOG="$DEMO_DIR/.agent-factory/audit.log"
    : > "$AF_SESSION_LOG"
    session_log "system" "init" "demo-start" "Demo session started"
    session_log "system" "init" "demo-dir" "dir=$DEMO_DIR"
}

session_log() {
    # session_log <category> <state> <action> <detail>
    local category="$1" state="$2" action="$3" detail="${4:-}"
    python3 -c "
import json, sys
from datetime import datetime, timezone
entry = {
    'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'source': '${DEMO_PART:-init}',
    'category': '$category',
    'state': '$state',
    'action': '$action',
    'detail': '''$detail'''
}
with open('$AF_SESSION_LOG', 'a') as f:
    f.write(json.dumps(entry) + '\n')
"
}

session_log_show() {
    local part="$1"
    echo ""
    echo -e "${BOLD}─── Session log ($part) ───${RESET}"
    echo -e "${DIM}File: $AF_SESSION_LOG${RESET}"
    echo ""
    python3 -c "
import json, sys
for line in open('$AF_SESSION_LOG'):
    e = json.loads(line)
    source = e.get('source', '?')
    if source != '$part' and 'script' not in e:
        continue
    ts = e.get('ts', '?')[:19]
    if 'script' in e:
        # Gate script entry (from _session_log.py)
        script = e['script']
        exit_code = e.get('exit_code', '?')
        files = len(e.get('files_changed', []))
        color = '\033[0;32m' if exit_code == 0 else '\033[0;31m'
        print(f'  {color}{ts}  GATE      {script:30s} exit={exit_code}  files_changed={files}\033[0m')
    else:
        cat = e.get('category', '?').upper()
        state = e.get('state', '-')
        action = e.get('action', '-')
        detail = e.get('detail', '')
        colors = {'GATE':'\033[0;36m','ADVANCE':'\033[0;32m','HALT':'\033[1;33m',
                  'DISPATCH':'\033[1m','HUMAN':'\033[0m','SYSTEM':'\033[2m'}
        c = colors.get(cat, '\033[0m')
        print(f'  {c}{ts}  {cat:9s} {state:30s} {action:12s} {detail}\033[0m')
"
    echo ""
}

# ─── Display helpers ─────────────────────────────────────────────────────
info()  { echo -e "${CYAN}▸${RESET} $*"; }
step()  { echo -e "\n${BOLD}${GREEN}═══ $* ═══${RESET}\n"; }
wait_for_enter() { echo -e "${DIM}  (press Enter to continue)${RESET}"; read -r; }
show_file() { echo -e "${DIM}── $1 ──${RESET}"; cat "$1"; echo; }

# ─── Set up a self-contained demo project ────────────────────────────────
setup_demo_project() {
    local target="$1"
    info "Creating demo project in $target"
    session_log "system" "-" "SETUP" "Creating demo project in $target"

    mkdir -p "$target"
    cd "$target"
    git init --quiet
    session_log "system" "-" "SETUP" "git init complete"

    # Copy factory/ from the real repo
    cp -r "$REPO_ROOT/factory" "$target/factory"
    mkdir -p config
    cp "$REPO_ROOT/config/model.conf" config/model.conf 2>/dev/null || true

    # Create a tiny demo FSM — three states, simple file gates
    cat > factory/playbooks/demo.fsm.yml << 'FSM'
version: 1.0.0
type: workflow-state-machine
playbook: demo

gate_conditions:
  project_initialized:
    type: file_exists
    path: .git/config

  design_exists:
    type: files_exist
    paths:
      - docs/design.md

  code_exists:
    type: files_exist
    paths:
      - src/app.py

  review_clean:
    type: no_open_findings
    pattern: REVIEW-*.md

states:
  INIT:
    description: Project is ready
    entry_conditions:
      - project_initialized
    on:
      Start:
        transitions:
          to: DESIGN

  DESIGN:
    description: Write the design document
    agent: architecture-agent
    entry_conditions:
      - project_initialized
    on:
      DesignComplete:
        exit_conditions:
          - design_exists
        transitions:
          - if: design_exists
            to: APPROVAL
          - else:
            to: DESIGN

  APPROVAL:
    description: Human reviews and approves the design
    agent: null
    entry_conditions:
      - design_exists
    on:
      Approved:
        transitions:
          to: BUILD

  BUILD:
    description: Write the code
    agent: developer-agent
    entry_conditions:
      - design_exists
    on:
      BuildComplete:
        exit_conditions:
          - code_exists
        transitions:
          - if: code_exists
            to: DONE
          - else:
            to: BUILD

  DONE:
    description: All work complete
    entry_conditions:
      - design_exists
      - code_exists
    final: true

halt_conditions:
  - type: max_iterations
    state: DESIGN
    event: DesignComplete
    limit: 3
    message: "Design looped 3 times. Step back and rethink."
  - type: max_iterations
    state: BUILD
    event: BuildComplete
    limit: 3
    message: "Build looped 3 times. Something is fundamentally wrong."
FSM

    # Create docs/findings dir (for no_open_findings checks)
    mkdir -p docs/findings

    info "Demo project ready: 5-state FSM (INIT → DESIGN → APPROVAL → BUILD → DONE)"
    session_log "system" "-" "SETUP" "Demo FSM written: INIT → DESIGN → APPROVAL → BUILD → DONE"
}


# ═══════════════════════════════════════════════════════════════════════════
# PART 1: HUMAN IN THE LOOP
# ═══════════════════════════════════════════════════════════════════════════
demo_human_in_the_loop() {
    DEMO_PART="HUMAN"
    session_log "system" "-" "START" "Part 1: Human in the Loop"

    step "PART 1: Human in the Loop"
    echo "You are the operator. You will:"
    echo "  1. Check gates manually"
    echo "  2. Do the work (create files)"
    echo "  3. Advance the marker by calling 'phase advance'"
    echo ""
    echo "This is how every playbook worked before the orchestrator existed."
    wait_for_enter

    # ── Step 1: Bootstrap the marker ────────────────────────────────
    step "Step 1: Bootstrap the marker at INIT"
    info "The marker tracks where we are in the FSM."
    info "Running: phase advance --playbook demo"

    session_log "gate" "INIT" "CHECK" "entry_conditions: project_initialized"
    python3 factory/scripts/phase advance --playbook demo --by human
    session_log "advance" "INIT→DESIGN" "PASS" "marker moved to DESIGN"
    echo ""
    show_file .agent-factory/playbook-state.yml

    info "We're at DESIGN now. The gate (project_initialized) passed automatically."
    wait_for_enter

    # ── Step 2: Try to advance without doing work ───────────────────
    step "Step 2: Try to advance to APPROVAL (without doing work)"
    info "Running: phase advance --playbook demo"
    info "This should FAIL — docs/design.md doesn't exist yet."
    echo ""

    session_log "gate" "DESIGN→APPROVAL" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human 2>&1 || true
    session_log "gate" "DESIGN→APPROVAL" "FAIL" "docs/design.md missing"
    echo ""
    info "Gate refused. We haven't written the design yet."
    wait_for_enter

    # ── Step 3: Do the work (simulate what an agent would do) ───────
    step "Step 3: Write the design (simulating what architecture-agent would do)"
    mkdir -p docs
    cat > docs/design.md << 'DESIGN'
# Demo App Design

A greeting service. One endpoint, one function.

## Decision
Keep it simple. Python. No framework.
DESIGN

    session_log "human" "DESIGN" "CREATE" "docs/design.md (simulating architecture-agent)"
    info "Created docs/design.md"
    echo ""
    show_file docs/design.md
    wait_for_enter

    # ── Step 4: Now advance ─────────────────────────────────────────
    step "Step 4: Advance to APPROVAL (now the gate should pass)"
    session_log "gate" "DESIGN→APPROVAL" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    session_log "advance" "DESIGN→APPROVAL" "PASS" "marker moved to APPROVAL"
    echo ""
    show_file .agent-factory/playbook-state.yml

    info "Marker moved to APPROVAL. Agent field is null — this is a human gate."
    wait_for_enter

    # ── Step 5: Human gate ──────────────────────────────────────────
    step "Step 5: You are at the APPROVAL gate"
    echo "In a real workflow, you'd review docs/design.md and decide:"
    echo "  • Approve → advance to BUILD"
    echo "  • Reject → the marker would go back to DESIGN"
    echo ""
    info "Let's approve. Running: phase advance --playbook demo"

    session_log "halt" "APPROVAL" "HUMAN-GATE" "agent: null — waiting for human decision"
    session_log "human" "APPROVAL" "APPROVE" "design reviewed and approved"
    session_log "gate" "APPROVAL→BUILD" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    session_log "advance" "APPROVAL→BUILD" "PASS" "marker moved to BUILD"
    echo ""
    show_file .agent-factory/playbook-state.yml

    info "We're at BUILD now."
    wait_for_enter

    # ── Step 6: Build ───────────────────────────────────────────────
    step "Step 6: Write the code (simulating what developer-agent would do)"
    mkdir -p src
    cat > src/app.py << 'CODE'
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("world"))
CODE

    session_log "human" "BUILD" "CREATE" "src/app.py (simulating developer-agent)"
    info "Created src/app.py"
    show_file src/app.py
    wait_for_enter

    # ── Step 7: Advance to DONE ─────────────────────────────────────
    step "Step 7: Advance to DONE"
    session_log "gate" "BUILD→DONE" "CHECK" "entry_conditions: design_exists, code_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    session_log "advance" "BUILD→DONE" "PASS" "marker moved to DONE (final)"
    echo ""
    show_file .agent-factory/playbook-state.yml

    echo -e "\n${GREEN}${BOLD}✓ Playbook complete!${RESET}"
    session_log "halt" "DONE" "COMPLETE" "playbook finished — all gates passed"
    echo ""
    echo "You pressed Enter 7 times. You checked gates, created files,"
    echo "and advanced the marker — one step at a time."

    session_log_show "HUMAN"

    echo "Now let's see the orchestrator do exactly the same thing."
    wait_for_enter
}


# ═══════════════════════════════════════════════════════════════════════════
# PART 2: ORCHESTRATED
# ═══════════════════════════════════════════════════════════════════════════
demo_orchestrated() {
    DEMO_PART="ORCH"
    session_log "system" "-" "START" "Part 2: Orchestrated (run-playbook)"

    step "PART 2: Orchestrated (run-playbook)"
    echo "Same FSM, same gates, same work — but the orchestrator drives it."
    echo ""
    echo "Since this is a demo (no real AI CLI available), we'll stub"
    echo "'trigger' to simulate what each agent would produce."
    wait_for_enter

    # ── Reset: clean slate ──────────────────────────────────────────
    step "Reset: clean project, fresh start"
    rm -rf docs src .agent-factory
    mkdir -p docs/findings
    session_log "system" "-" "RESET" "Cleaned docs/, src/, .agent-factory/"

    info "Cleaned up. Starting from scratch."
    echo ""

    # ── Create a trigger stub ───────────────────────────────────────
    # This replaces the real trigger for the demo.
    # It simulates what each agent would produce (create the output files).
    cat > /tmp/demo-trigger-stub.py << 'STUB'
#!/usr/bin/env python3
"""Stub trigger for demo — simulates agent output by creating files."""
import sys, os, time

# Parse args: trigger agent <name> --background --cli <cli>
agent = sys.argv[2] if len(sys.argv) > 2 else "unknown"

print(f"[stub-trigger] Simulating {agent}...")
time.sleep(1)  # pretend work is happening

if agent == "architecture-agent":
    os.makedirs("docs", exist_ok=True)
    with open("docs/design.md", "w") as f:
        f.write("# Design\n\nA greeting service. Python. No framework.\n")
    print(f"[stub-trigger] {agent} created docs/design.md")

elif agent == "developer-agent":
    os.makedirs("src", exist_ok=True)
    with open("src/app.py", "w") as f:
        f.write('def greet(name): return f"Hello, {name}!"\n')
    print(f"[stub-trigger] {agent} created src/app.py")

else:
    print(f"[stub-trigger] unknown agent {agent}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
STUB
    session_log "system" "-" "SETUP" "Created trigger stub at /tmp/demo-trigger-stub.py"

    # ── Patch run_playbook to use the stub trigger ──────────────────
    cat > /tmp/demo-run-orchestrated.py << RUNNER
#!/usr/bin/env python3
"""Demo runner — patches trigger to use a stub, then runs the orchestrator."""
import sys, subprocess
sys.path.insert(0, "$REPO_ROOT/orchestrator/src")

import run_playbook

# Replace run_trigger with our stub
_original_run_trigger = run_playbook.run_trigger
def stub_trigger(agent, cli):
    result = subprocess.run(
        [sys.executable, "/tmp/demo-trigger-stub.py", "agent", agent,
         "--background", "--cli", cli],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    return result.returncode, result.stderr

run_playbook.run_trigger = stub_trigger

sys.exit(run_playbook.main([
    "--playbook", "demo",
    "--from-state", "DESIGN",
    "--cli", "claude"
]))
RUNNER
    session_log "system" "-" "SETUP" "Created orchestrator runner at /tmp/demo-run-orchestrated.py"

    # ── Run it ──────────────────────────────────────────────────────
    step "Running: run-playbook --playbook demo --from-state DESIGN"
    info "The orchestrator will now step through the FSM automatically."
    info "Watch it dispatch agents, check gates, and advance — or stop at the human gate."
    echo ""

    session_log "dispatch" "DESIGN" "BEGIN" "run-playbook --playbook demo --from-state DESIGN --cli claude"
    python3 /tmp/demo-run-orchestrated.py || true
    session_log "halt" "APPROVAL" "HUMAN-GATE" "orchestrator stopped — agent: null"
    echo ""

    # ── Show what happened ──────────────────────────────────────────
    step "The orchestrator stopped at APPROVAL (human gate)"
    info "It dispatched architecture-agent, the gate passed, and it advanced."
    info "Then it hit agent: null — a human decision point. It stopped and told you."
    echo ""
    show_file .agent-factory/playbook-state.yml

    # The orchestrator already wrote its entries to .agent-factory/audit.log.
    # Since AF_SESSION_LOG points to the same file, demo entries and
    # orchestrator entries are interleaved in one timeline.

    wait_for_enter

    # ── Human acts, then re-runs ────────────────────────────────────
    step "You approve. Re-run the orchestrator."
    info "The marker is at APPROVAL. The entry condition for BUILD is"
    info "design_exists — which is already satisfied. So phase advance"
    info "will pass, and the orchestrator continues."
    echo ""

    session_log "human" "APPROVAL" "APPROVE" "human reviewed and approved the design"
    session_log "dispatch" "APPROVAL" "RESUME" "run-playbook re-invoked"
    python3 /tmp/demo-run-orchestrated.py || true
    echo ""

    # ── Show final state ────────────────────────────────────────────
    step "Result"
    echo -e "${GREEN}${BOLD}✓ Playbook complete — the orchestrator drove the whole thing.${RESET}"
    session_log "system" "-" "FINISH" "Part 2 complete"
    echo ""
    show_file .agent-factory/playbook-state.yml

    echo -e "${BOLD}Full session log (.agent-factory/audit.log):${RESET}"
    echo ""
    python3 -c "
import json
for line in open('$AF_SESSION_LOG'):
    e = json.loads(line)
    ts = e.get('ts', '?')[:19]
    # Orchestrator entries (have 'action' key)
    if 'action' in e:
        icon = {'advance':'✓','human-gate':'⏸','done':'★','halt':'✗','retry':'↻'}.get(e['action'],'·')
        dur = f' ({e[\"duration_seconds\"]}s)' if e.get('duration_seconds') else ''
        agent = e.get('agent') or '(no agent)'
        print(f'  {icon} {ts}  {e[\"state\"]:25s} {agent:22s} {e[\"action\"]}{dur}')
    # Demo entries (have 'category' key)
    elif 'category' in e:
        cat = e['category'].upper()
        print(f'  · {ts}  {e.get(\"state\",\"-\"):25s} {cat:22s} {e.get(\"action\",\"-\")} {e.get(\"detail\",\"\")}')
    # Gate script entries (have 'script' key, from _session_log.py)
    elif 'script' in e:
        ex = e.get('exit_code', '?')
        icon = '✓' if ex == 0 else '✗'
        print(f'  {icon} {ts}  {\"(gate)\":25s} {e[\"script\"]:22s} exit={ex}')
"
    echo ""

    session_log_show "ORCH"

    echo ""
    echo "Same FSM. Same gates. Same scripts. The only difference:"
    echo "a human pressed Enter 7 times vs. the orchestrator pressed it 0 times."
}


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
DEMO_PART="INIT"
clear
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║          Agent Factory — Orchestrator Demo                  ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo "This demo shows two ways to run the same 5-state playbook:"
echo ""
echo "  Part 1: You drive it by hand (human in the loop)"
echo "  Part 2: The orchestrator drives it (unattended)"
echo ""
echo "Both use the exact same FSM, gates, and scripts."
echo "All events are logged to .agent-factory/audit.log — the same"
echo "file the real orchestrator uses, activated via AF_SESSION_LOG."
echo ""

session_log_init
setup_demo_project "$DEMO_DIR"
wait_for_enter

demo_human_in_the_loop
demo_orchestrated

# ── Final side-by-side comparison ───────────────────────────────────────
step "Side-by-side comparison"
echo "Both parts used the same FSM and the same gate scripts."
echo "Here's what each workflow looked like:"
echo ""

echo -e "${BOLD}HUMAN workflow (Part 1):${RESET}"
session_log_show "HUMAN"

echo -e "${BOLD}ORCHESTRATED workflow (Part 2):${RESET}"
session_log_show "ORCH"

echo -e "Session log: ${BOLD}$AF_SESSION_LOG${RESET}"
echo ""
echo -e "${BOLD}Demo complete.${RESET} The demo project has been cleaned up."
echo ""
