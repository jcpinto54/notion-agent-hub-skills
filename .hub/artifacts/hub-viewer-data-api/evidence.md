# Evidence

### Regression-first backend implementation
First failing result: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3 initially failed for missing set_issue_spec, missing dashboard_snapshot, and missing issue set-spec CLI command.
Final focused result: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3 passed after backend and CLI implementation.
Touched: skills/manage-agent-hub-issues/lib/file_hub_common.py; skills/manage-agent-hub-issues/scripts/agent_hub.py; tests/test_file_hub_backend.py; tests/test_agent_hub_v3.py.
Output contract: dashboard export now includes read-only mode, generated_at, hub metadata, columns, diagnostics, summary, card readiness, done criteria, and verification snippets.

### Review verification
Command: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Result: passed, 23 tests OK
Command: python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change readonly-kanban-viewer
Result: passed, schema version 3, read-only mode, correct change filter and columns
Command: python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change definitely-missing-change
Result: failed as expected with No change packet found
