# testing.yaml Prerequisite Guard

Before doing anything else, check `testing.yaml` (at `docs/testing.yaml`).
The test-strategy agent owns the file and writes it with `detect-test-regime`.
Every failure below stops the run and names that agent as the next step.

1. **File does not exist.** Fail immediately. Run the test-strategy agent
   first to record the project's test suites and testing strategy link.
   Write no output.

2. **File exists but has no `testing_strategy:` key.** Fail immediately. Run
   the test-strategy agent to add the key.

3. **File exists but has no `suites:` section.** Fail immediately. Run the
   test-strategy agent to record the project's test suites.
