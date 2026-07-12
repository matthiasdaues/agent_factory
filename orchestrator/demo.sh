#!/usr/bin/env bash
# demo.sh — Two demonstrations of Agent Factory's playbook execution.
#
# Part 1: Human-in-the-loop (you press enter, you check gates, you advance)
# Part 2: Orchestrated (run-playbook does exactly what you did, unattended)
#
# Both use the same FSM. The only difference is who presses "enter."
#
# Every action is logged to a structured demo log. At the end of each part,
# the log is printed as a summary so you can compare the two workflows
# side by side.
#
# Usage:
#   cd agent_factory
#   bash orchestrator/demo.sh
#
# Output:
#   Interactive terminal walk-through + demo log at /tmp/agent-factory-demo.log

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_DIR="$(mktemp -d)"
DEMO_LOG="/tmp/agent-factory-demo.log"
trap 'rm -rf "$DEMO_DIR"' EXIT

# ─── Colors ──────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ─── Logging ─────────────────────────────────────────────────────────────
# Every interesting event is logged as a structured line:
#   TIMESTAMP | PART | CATEGORY | STATE | ACTION | DETAIL
#
# CATEGORY is one of:
#   GATE     — a gate check (pass or fail)
#   ADVANCE  — marker moved forward
#   DISPATCH — an agent was dispatched (real or stub)
#   HUMAN    — a human action (file creation, approval)
#   HALT     — the workflow stopped (human gate, final, error)
#   SYSTEM   — setup, teardown, meta events

log_init() {
    : > "$DEMO_LOG"
    log "SYSTEM" "-" "INIT" "Demo log started at $(date -Iseconds)"
    log "SYSTEM" "-" "INIT" "Demo dir: $DEMO_DIR"
    log "SYSTEM" "-" "INIT" "Repo root: $REPO_ROOT"
}

log() {
    local category="$1" state="$2" action="$3" detail="${4:-}"
    local ts
    ts="$(date '+%H:%M:%S')"
    printf '%s | %-7s | %-8s | %-25s | %-12s | %s\n' \
        "$ts" "$DEMO_PART" "$category" "$state" "$action" "$detail" \
        >> "$DEMO_LOG"
}

log_show_summary() {
    local part="$1"
    echo ""
    echo -e "${BOLD}─── Log summary ($part) ───${RESET}"
    echo ""
    printf "${DIM}%-8s | %-7s | %-8s | %-25s | %-12s | %s${RESET}\n" \
        "TIME" "PART" "CATEGORY" "STATE" "ACTION" "DETAIL"
    echo -e "${DIM}$(printf '%.0s─' {1..100})${RESET}"
    grep "| $part " "$DEMO_LOG" | while IFS= read -r line; do
        # Color by category
        if echo "$line" | grep -q "| GATE "; then
            echo -e "${CYAN}$line${RESET}"
        elif echo "$line" | grep -q "| ADVANCE "; then
            echo -e "${GREEN}$line${RESET}"
        elif echo "$line" | grep -q "| HALT "; then
            echo -e "${YELLOW}$line${RESET}"
        elif echo "$line" | grep -q "| DISPATCH"; then
            echo -e "${BOLD}$line${RESET}"
        else
            echo "$line"
        fi
    done
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
    log "SYSTEM" "-" "SETUP" "Creating demo project in $target"

    mkdir -p "$target"
    cd "$target"
    git init --quiet
    log "SYSTEM" "-" "SETUP" "git init complete"

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
    log "SYSTEM" "-" "SETUP" "Demo FSM written: INIT → DESIGN → APPROVAL → BUILD → DONE"
}


# ═══════════════════════════════════════════════════════════════════════════
# PART 1: HUMAN IN THE LOOP
# ═══════════════════════════════════════════════════════════════════════════
demo_human_in_the_loop() {
    DEMO_PART="HUMAN"
    log "SYSTEM" "-" "START" "Part 1: Human in the Loop"

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

    log "GATE" "INIT" "CHECK" "entry_conditions: project_initialized"
    python3 factory/scripts/phase advance --playbook demo --by human
    log "ADVANCE" "INIT→DESIGN" "PASS" "marker moved to DESIGN"
    echo ""
    show_file .agent-factory/playbook-state.yml

    info "We're at DESIGN now. The gate (project_initialized) passed automatically."
    wait_for_enter

    # ── Step 2: Try to advance without doing work ───────────────────
    step "Step 2: Try to advance to APPROVAL (without doing work)"
    info "Running: phase advance --playbook demo"
    info "This should FAIL — docs/design.md doesn't exist yet."
    echo ""

    log "GATE" "DESIGN→APPROVAL" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human 2>&1 || true
    log "GATE" "DESIGN→APPROVAL" "FAIL" "docs/design.md missing"
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

    log "HUMAN" "DESIGN" "CREATE" "docs/design.md (simulating architecture-agent)"
    info "Created docs/design.md"
    echo ""
    show_file docs/design.md
    wait_for_enter

    # ── Step 4: Now advance ─────────────────────────────────────────
    step "Step 4: Advance to APPROVAL (now the gate should pass)"
    log "GATE" "DESIGN→APPROVAL" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    log "ADVANCE" "DESIGN→APPROVAL" "PASS" "marker moved to APPROVAL"
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

    log "HALT" "APPROVAL" "HUMAN-GATE" "agent: null — waiting for human decision"
    log "HUMAN" "APPROVAL" "APPROVE" "design reviewed and approved"
    log "GATE" "APPROVAL→BUILD" "CHECK" "entry_conditions: design_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    log "ADVANCE" "APPROVAL→BUILD" "PASS" "marker moved to BUILD"
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

    log "HUMAN" "BUILD" "CREATE" "src/app.py (simulating developer-agent)"
    info "Created src/app.py"
    show_file src/app.py
    wait_for_enter

    # ── Step 7: Advance to DONE ─────────────────────────────────────
    step "Step 7: Advance to DONE"
    log "GATE" "BUILD→DONE" "CHECK" "entry_conditions: design_exists, code_exists"
    python3 factory/scripts/phase advance --playbook demo --by human
    log "ADVANCE" "BUILD→DONE" "PASS" "marker moved to DONE (final)"
    echo ""
    show_file .agent-factory/playbook-state.yml

    echo -e "\n${GREEN}${BOLD}✓ Playbook complete!${RESET}"
    log "HALT" "DONE" "COMPLETE" "playbook finished — all gates passed"
    echo ""
    echo "You pressed Enter 7 times. You checked gates, created files,"
    echo "and advanced the marker — one step at a time."

    log_show_summary "HUMAN"

    echo "Now let's see the orchestrator do exactly the same thing."
    wait_for_enter
}


# ═══════════════════════════════════════════════════════════════════════════
# PART 2: ORCHESTRATED
# ═══════════════════════════════════════════════════════════════════════════
demo_orchestrated() {
    DEMO_PART="ORCH"
    log "SYSTEM" "-" "START" "Part 2: Orchestrated (run-playbook)"

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
    log "SYSTEM" "-" "RESET" "Cleaned docs/, src/, .agent-factory/"

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
    log "SYSTEM" "-" "SETUP" "Created trigger stub at /tmp/demo-trigger-stub.py"

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
    log "SYSTEM" "-" "SETUP" "Created orchestrator runner at /tmp/demo-run-orchestrated.py"

    # ── Run it ──────────────────────────────────────────────────────
    step "Running: run-playbook --playbook demo --from-state DESIGN"
    info "The orchestrator will now step through the FSM automatically."
    info "Watch it dispatch agents, check gates, and advance — or stop at the human gate."
    echo ""

    log "DISPATCH" "DESIGN" "BEGIN" "run-playbook --playbook demo --from-state DESIGN --cli claude"
    python3 /tmp/demo-run-orchestrated.py || true
    log "HALT" "APPROVAL" "HUMAN-GATE" "orchestrator stopped — agent: null"
    echo ""

    # ── Show what happened ──────────────────────────────────────────
    step "The orchestrator stopped at APPROVAL (human gate)"
    info "It dispatched architecture-agent, the gate passed, and it advanced."
    info "Then it hit agent: null — a human decision point. It stopped and told you."
    echo ""
    show_file .agent-factory/playbook-state.yml

    # Log what the orchestrator did internally (read from audit.log)
    if [ -f .agent-factory/audit.log ]; then
        while IFS= read -r line; do
            action=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['action'])")
            state=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['state'])")
            agent=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('agent') or '-')")
            log_action=$(echo "$action" | tr '[:lower:]' '[:upper:]')
            case "$action" in
                advance)  log "ADVANCE" "$state" "PASS" "agent=$agent — gate passed, marker moved" ;;
                human-gate) log "HALT" "$state" "HUMAN-GATE" "agent: null — returned control" ;;
                retry)    log "GATE" "$state" "RETRY" "agent=$agent — gate failed, retrying" ;;
                halt)     log "HALT" "$state" "CAP-HIT" "iteration cap reached" ;;
                done)     log "HALT" "$state" "COMPLETE" "final state reached" ;;
                *)        log "SYSTEM" "$state" "$log_action" "agent=$agent" ;;
            esac
        done < .agent-factory/audit.log
    fi

    wait_for_enter

    # ── Human acts, then re-runs ────────────────────────────────────
    step "You approve. Re-run the orchestrator."
    info "The marker is at APPROVAL. The entry condition for BUILD is"
    info "design_exists — which is already satisfied. So phase advance"
    info "will pass, and the orchestrator continues."
    echo ""

    log "HUMAN" "APPROVAL" "APPROVE" "human reviewed and approved the design"
    log "DISPATCH" "APPROVAL" "RESUME" "run-playbook --playbook demo --cli claude (re-invocation)"
    python3 /tmp/demo-run-orchestrated.py || true
    echo ""

    # Log second run's audit entries
    if [ -f .agent-factory/audit.log ]; then
        # Read only new entries (skip ones we already logged)
        tail -n +2 .agent-factory/audit.log | while IFS= read -r line; do
            action=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['action'])" 2>/dev/null) || continue
            state=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['state'])" 2>/dev/null) || continue
            agent=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('agent') or '-'" 2>/dev/null) || continue
            case "$action" in
                advance)  log "ADVANCE" "$state" "PASS" "agent=$agent — gate passed, marker moved" ;;
                done)     log "HALT" "$state" "COMPLETE" "final state reached" ;;
                *)        : ;;  # already logged
            esac
        done
    fi

    # ── Show final state ────────────────────────────────────────────
    step "Result"
    echo -e "${GREEN}${BOLD}✓ Playbook complete — the orchestrator drove the whole thing.${RESET}"
    log "SYSTEM" "-" "FINISH" "Part 2 complete"
    echo ""
    show_file .agent-factory/playbook-state.yml

    if [ -f .agent-factory/audit.log ]; then
        echo -e "${BOLD}Orchestrator audit log (.agent-factory/audit.log):${RESET}"
        echo ""
        python3 -c "
import json
for line in open('.agent-factory/audit.log'):
    e = json.loads(line)
    icon = {'advance':'✓','human-gate':'⏸','done':'★','halt':'✗','retry':'↻'}.get(e['action'],'?')
    dur = f\" ({e['duration_seconds']}s)\" if e.get('duration_seconds') else ''
    agent = e.get('agent') or '(you)'
    print(f\"  {icon} {e['state']:30s} {agent:25s} {e['action']}{dur}\")
"
    fi

    log_show_summary "ORCH"

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
echo ""
echo -e "Full log written to: ${BOLD}$DEMO_LOG${RESET}"
echo ""

log_init
setup_demo_project "$DEMO_DIR"
wait_for_enter

demo_human_in_the_loop
demo_orchestrated

# ── Final side-by-side comparison ───────────────────────────────────────
step "Side-by-side comparison"
echo "Both parts used the same FSM and the same gate scripts."
echo "Here's what each workflow looked like:"
echo ""

echo -e "${BOLD}HUMAN (Part 1):${RESET}"
grep "| HUMAN " "$DEMO_LOG" | grep -E "GATE|ADVANCE|HALT|DISPATCH|HUMAN" | \
    awk -F'|' '{printf "  %s │%s │%s\n", $4, $5, $6}'
echo ""

echo -e "${BOLD}ORCHESTRATOR (Part 2):${RESET}"
grep "| ORCH " "$DEMO_LOG" | grep -E "GATE|ADVANCE|HALT|DISPATCH|HUMAN" | \
    awk -F'|' '{printf "  %s │%s │%s\n", $4, $5, $6}'
echo ""

echo -e "Full log: ${BOLD}$DEMO_LOG${RESET}"
echo ""
echo -e "${BOLD}Demo complete.${RESET} The demo project has been cleaned up."
echo ""
