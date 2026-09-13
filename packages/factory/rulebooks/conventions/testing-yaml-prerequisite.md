# testing.yaml Prerequisite Guard

Before doing anything else, check `testing.yaml` (at `docs/testing.yaml`):

1. **File does not exist.** Fail immediately. Run `detect-test-regime` first
   to record the project's test suites and testing strategy link. Write no
   output.

2. **File exists but has no `testing_strategy:` key.** Fail immediately. Run
   `detect-test-regime` to populate it.

3. **File exists but has no `suites:` section.** Fail immediately. Run
   `detect-test-regime` to record the project's test suites.
