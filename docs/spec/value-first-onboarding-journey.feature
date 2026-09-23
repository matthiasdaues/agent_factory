# scope: value-first-onboarding-journey

Feature: Value-first onboarding journey

  A newcomer diagnoses the host, installs a verified Factory release, receives
  project-specific insight, and completes one isolated task before advanced
  configuration. Every change requires explicit consent and remains reversible.

  Proposal trace: docs/proposals/value-first-onboarding-journey.md

  Rule: Release maintainer publishes reproducible installation assets
    # actor: Release maintainer

    Scenario: Release build produces the required asset set
      Given a versioned Agent Factory source tree
      When the release maintainer runs the release build twice for the same version
      Then each build produces install-agent-factory, agent-factory.tar.gz, and SHA256SUMS
      And both archives have the same SHA-256 digest

    Scenario: Distribution remotes publish identical archives
      Given two approved distribution remotes publish the same Factory version
      When the release maintainer compares their agent-factory.tar.gz assets
      Then both assets have the digest recorded for that version

  Rule: Newcomer diagnoses installation readiness without changes
    # actor: Newcomer
    # @packages/factory/scripts/init-factory

    Scenario: Bootstrap requires one source and an explicit target
      Given the newcomer has saved the bootstrap for inspection
      When the newcomer omits --target or supplies zero or two source selectors
      Then the bootstrap prints usage and exits without changing the host or target

    Scenario: Local source resolves from the invocation directory
      Given the newcomer selects --from-local with a relative path
      When preflight resolves the installation input
      Then preflight displays the absolute source path
      And preflight verifies that the path contains an Agent Factory source tree

    Scenario: Version selection is valid only for remote sources
      Given the newcomer supplies --version with --from-local
      When bootstrap validates its arguments
      Then bootstrap reports the invalid combination and exits without changes

    Scenario: Unsafe target is rejected
      Given --target resolves to the filesystem root, the user home, or unsupported content
      When preflight classifies the target
      Then preflight reports the unsafe target and exits without changes

    Scenario: Supported host receives one readiness result
      Given the host is macOS or Linux on x86_64 or arm64, or Linux under Windows Subsystem for Linux
      When preflight checks the host, tools, Git state, network, interfaces, and target
      Then preflight reports Ready, Ready with limitations, or Blocked
      And preflight does not install software or edit files

    Scenario: Unsupported host stops safely
      Given the host platform, architecture, or shell is unsupported
      When preflight runs
      Then preflight explains the incompatibility and exits without changes

    Scenario: Missing prerequisite explains its remedy
      Given preflight detects a missing prerequisite
      When preflight reports the result
      Then the report states the prerequisite purpose, proposed fix, change scope, reversal, and verification command

  Rule: Newcomer controls each prerequisite fix
    # actor: Newcomer

    Scenario: Confirmed fix runs and is verified alone
      Given preflight offers a supported fix for uv or managed Python
      When the newcomer gives affirmative consent
      Then the bootstrap shows and runs only that fix command
      And the bootstrap repeats the related check before offering another fix

    Scenario: Declined or blank fix input stops the sequence
      Given preflight offers a prerequisite fix
      When the newcomer declines, cancels, or submits blank input
      Then the bootstrap does not run that fix
      And the bootstrap reports completed fixes and their reversal commands

    Scenario: Failed fix verification stops the sequence
      Given the bootstrap ran a confirmed prerequisite fix
      When the related verification still fails
      Then the bootstrap stops the fix sequence
      And the bootstrap shows recovery guidance

    Scenario: Unsupported fix receives guidance only
      Given Git, shell support, network access, or a coding command-line interface is missing
      When preflight offers remediation
      Then it does not run sudo, a system package manager, a global package install, or a coding interface installer

  Rule: Newcomer installs a verified Factory release with explicit consent
    # actor: Newcomer
    # @packages/factory/scripts/init-factory
    # @packages/factory/scripts/remove-factory

    Scenario: Remote release resolves to immutable verified assets
      Given the newcomer selects an HTTPS release base
      When bootstrap resolves latest or a named --version release
      Then bootstrap uses the immutable versioned release URL
      And bootstrap verifies agent-factory.tar.gz against SHA256SUMS before extraction

    Scenario: Missing or mismatched digest blocks extraction
      Given the remote archive digest is missing or differs from SHA256SUMS
      When bootstrap verifies the release
      Then bootstrap refuses to extract the archive
      And bootstrap leaves the target unchanged

    Scenario: Installation preview names every planned effect
      Given preflight permits installation
      When bootstrap presents the installation preview
      Then the preview shows the source, version, target, selected interfaces, affected paths, instruction files, and uninstall command
      And a remote preview shows the resolved release URL and digest

    Scenario: Ambiguous interface selection does not select all interfaces
      Given zero or several detected interfaces make the default choice ambiguous
      When the newcomer submits blank interface input
      Then bootstrap asks again or stops
      And bootstrap does not select all interfaces

    Scenario: Declined installation leaves target unchanged
      Given the installation preview is visible
      When the newcomer declines, cancels, or submits blank approval
      Then bootstrap leaves the target unchanged

    Scenario: Approved installation returns a verifiable receipt
      Given the newcomer approves the displayed installation
      When installation and verification succeed
      Then the receipt lists every changed path, selected interface, installed version, resolved source, uninstall command, and one exact next command

    Scenario: Installation injects headers into existing instruction files
      Given the target contains regular AGENTS.md or copilot-instructions.md files outside the documented exclusions
      When installation runs
      Then one marker-delimited Factory header is prepended to each discovered file
      And each header uses repository links relative to its file location
      And the manifest records each injection and the original newline state

    Scenario: Instruction discovery preserves excluded and linked content
      Given matching files exist inside excluded trees or as external symlinks
      When installation discovers instruction files
      Then those matches remain unchanged and are reported accurately
      And installation does not create missing nested instruction files

    Scenario: Header installation and removal are reversible
      Given installation has injected Factory headers
      When installation repeats and remove-factory later runs
      Then repeated installation adds no duplicate header
      And removal deletes only the Factory blocks and restores original newline states

  Rule: Project maintainer updates an installation within its trust boundary
    # actor: Project maintainer
    # @packages/factory/scripts/update-factory

    Scenario: Update check reports candidate changes without writing
      Given an installation manifest records a local or remote source
      When the maintainer runs update-factory --check
      Then the report shows installed and candidate versions, source, digest, local modifications, and planned header changes
      And no file changes

    Scenario: Remote update verifies and stages before applying
      Given a remote installation has an available verified release
      When the maintainer approves a normal update
      Then update-factory verifies downloaded assets before changing the installation
      And stages the Factory tree, derived interface files, hook configuration, and header edits before applying them

    Scenario: Failed update restores the prior installation
      Given an approved update has started applying staged changes
      When application fails
      Then update-factory restores the previous Factory tree and instruction headers
      And reports the recovery result

    Scenario: Modified Factory files stop update by default
      Given Factory-owned files differ from their installed state
      When update preflight runs without an explicit preservation choice
      Then update-factory stops before replacing files

    Scenario: Source change requires separate consent
      Given the maintainer selects a different source kind or remote URL
      When update-factory previews the trust-boundary change
      Then update-factory requires separate affirmative confirmation
      And no automatic fallback crosses the source boundary

    Scenario: Successful update records its resolved input and effects
      Given an approved update completes
      When update-factory writes its manifest and receipt
      Then both record the selected source, resolved version or local revision, remote digest when applicable, and changed paths

  Rule: Newcomer receives project insight before advanced configuration
    # actor: Newcomer
    # @packages/factory/agents/virgil.md
    # @packages/factory/skills/capture-context/SKILL.md

    Scenario: First session reports evidence without changing the project
      Given installation completed on an existing repository
      When the newcomer opens the first Factory session
      Then the session reports the detected stack and test entry point or states that each was not detected
      And the session reports one observed safety signal or its absence
      And the session recommends one next action
      And the project files remain unchanged

    Scenario: Ready-host insight meets the decision and time bounds
      Given an existing repository on a ready host with one detected interface
      When the first Factory session opens after installation approval
      Then the project insight appears within two minutes
      And no more than three user decisions occur before the insight

    Scenario: Advanced configuration waits for a dependent action
      Given the newcomer has not selected an action that needs model tiers, hooks, or extended context
      When the first session recommends a next action
      Then it does not request those configuration decisions

    Scenario: Context capture is explained before scanning
      Given the selected action needs project context
      When onboarding offers capture-context
      Then it explains the scan, confirmation decisions, docs/agent-context.md output, concern-lint validation, and human and agent use
      And it defines a concern as a routing topic rather than a problem or warning

    Scenario: Context capture can be deferred before scanning
      Given onboarding has explained context capture
      When the newcomer defers or cancels
      Then capture-context does not scan the repository or create files

  Rule: Newcomer sees gate value before choosing hooks
    # actor: Newcomer
    # @packages/factory/agents/virgil.md
    # @packages/factory/config/pre-commit-config.yaml

    Scenario: Gate demonstration shows one failure-to-pass cycle
      Given fitting has not asked the newcomer to configure hooks
      When the newcomer accepts the one-minute gate demonstration
      Then a real Factory gate reports a specific failure on a Factory-owned disposable fixture
      And the corrected fixture passes the same gate
      And cleanup removes the fixture and leaves the target project unchanged

    Scenario: Skipping the gate demonstration preserves defaults
      Given onboarding offers the gate demonstration
      When the newcomer skips it
      Then onboarding continues with the same recommended hook defaults

    Scenario: Hook choices describe protected outcomes and material trade-offs
      Given fitting introduces hook configuration
      When it presents the available hooks
      Then it groups them by protected outcome
      And it asks only about automatic file changes or material execution cost
      And it describes unavailable hooks without treating them as errors or choices

    Scenario: Consumer hook set omits source-only triggers
      Given Factory installs hooks into a consumer project
      When hook configuration is generated
      Then no hook can match only ignored Factory runtime paths
      And the consumer hook set omits index-lint
      And matrix-lint runs after model configuration and before dispatch

  Rule: Newcomer completes one isolated task and chooses its outcome
    # actor: Newcomer
    # @packages/factory/playbooks/poc-spike.md

    Scenario: First task preview requires approval
      Given onboarding recommends a first task
      When it presents the task for approval
      Then it shows the goal, expected duration, expected artifacts, required decisions, and cleanup method
      And blank or declined approval creates no sandbox

    Scenario: Repository with a commit uses a detached worktree
      Given the repository has a current HEAD and the newcomer approves the task
      When onboarding creates the first-task sandbox
      Then it creates a detached worktree from HEAD under .current-work/onboarding-spike/<session-id>/
      And it creates no branch or commit
      And uncommitted active-working-tree changes are absent from the sandbox

    Scenario: Repository without a commit uses a plain sandbox
      Given the repository has no commit and the newcomer approves the task
      When onboarding creates the first-task sandbox
      Then it creates a plain sandbox under .current-work/onboarding-spike/<session-id>/
      And the task runs only inside that sandbox

    Scenario: First task produces an inspectable checked result
      Given an approved sandbox exists
      When the poc-spike workflow completes
      Then onboarding shows the runnable or directly inspectable result
      And onboarding shows which checks ran and how to remove the result

    Scenario: Ready-host first result meets the decision and time bounds
      Given the defined ready-host onboarding path
      When the newcomer approves and runs the first task
      Then an inspectable result appears within ten minutes of session start
      And no more than five user decisions occur after installation approval

    Scenario: Newcomer discards the first task
      Given the first task has completed
      When the newcomer chooses discard
      Then onboarding removes the worktree or sandbox
      And verifies that its path no longer exists

    Scenario: Newcomer retains selected reference artifacts
      Given the first task has completed
      When the newcomer separately confirms selected artifacts for retention
      Then onboarding copies only those artifacts to a named docs/spikes/ path
      And it does not preserve or promote the sandbox as production work

    Scenario: Newcomer begins real work explicitly
      Given the first task has completed
      When the newcomer chooses to begin real work and approves the normal workflow
      Then onboarding creates or selects a normal production workstream
      And the first-task sandbox does not become production work

  Rule: Quality researcher measures the complete newcomer journey
    # actor: Quality researcher

    Scenario: Automated journey checks the safe non-interactive path
      Given the onboarding implementation is ready for acceptance testing
      When the automated journey runs
      Then it checks diagnosis, cancellation, explicit consent, installation, receipt, and first-session routing

    Scenario: Moderated session records newcomer comprehension
      Given a participant did not build Agent Factory
      When the quality researcher runs the moderated usability protocol
      Then the record contains elapsed time, decisions, unclear terms, abandonment points, recovery attempts, and the participant's stated next action
