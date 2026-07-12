#!/bin/bash
# Interactive test script for the flow control harness PoC
# Run each section manually to see the gates in action

set -e

echo "=========================================="
echo "Flow Control Harness - Interactive Test"
echo "=========================================="
echo ""

# Setup
echo "SETUP: Creating .agent-factory directory and initial marker..."
mkdir -p .agent-factory

cat > .agent-factory/playbook-state.yml << 'MARKER'
playbook: greenfield-development
state: INIT
MARKER

echo "✓ Marker created at INIT state:"
cat .agent-factory/playbook-state.yml
echo ""

# Test 1
echo "=========================================="
echo "TEST 1: Advance from INIT → PHASE_1_REQUIREMENTS"
echo "=========================================="
factory/scripts/phase advance
echo ""
echo "✓ Marker after advance:"
cat .agent-factory/playbook-state.yml
echo ""
read -p "Press Enter to continue..."

# Test 2
echo "=========================================="
echo "TEST 2: Try to stage file from FUTURE phase (should BLOCK)"
echo "=========================================="
mkdir -p src
echo "# fake code" > src/app.py
git add src/app.py
echo ""
echo "Running transition-lint on src/app.py (belongs to PHASE_4)..."
factory/scripts/transition-lint || echo "✓ Correctly BLOCKED out-of-phase file!"
echo ""
git reset HEAD src/app.py
rm -rf src/
read -p "Press Enter to continue..."

# Test 3
echo "=========================================="
echo "TEST 3: Stage file from CURRENT phase (should PASS)"
echo "=========================================="
mkdir -p docs/spec
echo "# fake PRD" > docs/spec/prd.md
git add docs/spec/prd.md
echo ""
echo "Running transition-lint on docs/spec/prd.md (belongs to current phase)..."
factory/scripts/transition-lint && echo "✓ Correctly ALLOWED current-phase file!"
echo ""
git reset HEAD docs/spec/prd.md
read -p "Press Enter to continue..."

# Test 4
echo "=========================================="
echo "TEST 4: Try to advance WITHOUT entry_conditions (should BLOCK)"
echo "=========================================="
echo "Current state requires: docs/spec/prd.md, actor-goal-list.md, use_cases/*.md"
echo "Attempting advance without creating them..."
factory/scripts/phase advance 2>&1 || echo "✓ Correctly BLOCKED - entry conditions not met!"
echo ""
read -p "Press Enter to continue..."

# Test 5
echo "=========================================="
echo "TEST 5: Create required files and advance (should SUCCEED)"
echo "=========================================="
mkdir -p docs/spec/use_cases
echo "# PRD" > docs/spec/prd.md
echo "# Actor-Goal List" > docs/spec/actor-goal-list.md
echo "# UC-01" > docs/spec/use_cases/UC-01-example.md
echo ""
echo "Files created. Attempting advance..."
factory/scripts/phase advance && echo "✓ Successfully advanced!"
echo ""
echo "Marker now shows:"
cat .agent-factory/playbook-state.yml
echo ""
read -p "Press Enter to continue..."

# Test 6
echo "=========================================="
echo "TEST 6: Test iteration cap (retry limit)"
echo "=========================================="
cat > .agent-factory/playbook-state.yml << 'MARKER'
playbook: greenfield-development
state: PHASE_1_REQUIREMENTS
iteration: 4
MARKER

echo "Set iteration to 4 (cap is 5)"
echo ""
echo "Retry #1 (should succeed):"
factory/scripts/phase retry && echo "✓ Retry allowed (4→5)"
cat .agent-factory/playbook-state.yml | grep iteration
echo ""
echo "Retry #2 (should BLOCK - cap exceeded):"
factory/scripts/phase retry 2>&1 || echo "✓ Correctly BLOCKED - iteration cap exceeded!"
echo ""

# Cleanup
echo "=========================================="
echo "CLEANUP"
echo "=========================================="
echo "Removing test artifacts..."
rm -rf .agent-factory docs/spec
git reset HEAD . 2>/dev/null || true
echo "✓ Cleanup complete"
echo ""
echo "All tests completed!"
