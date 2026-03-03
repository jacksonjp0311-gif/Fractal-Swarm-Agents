# ASTS `memory/` Package Snapshot

This directory is a verbatim copy of the upstream `ASTS-Control-Kernel/memory/` package (snapshot date: 2026-03-03) to keep the workspace-memory-bridge skill self-contained.

## Why it exists
- Lets the skill run or patch the ASTS memory subsystem (bridge, episodic, summaries) even if the main repo is absent.
- Serves as an offline reference for regeneration; drop these files back into `ASTS-Control-Kernel/memory/` to restore the original state.

## Maintenance notes
- Re-sync after making changes upstream (e.g., improvements to `memory/bridge/openclaw_workspace.py`).
- Avoid editing files here unless you intend to upstream the change back into ASTS; otherwise the copies will drift.
- Observer wiring still happens in the ASTS repo — this snapshot just preserves the source scripts for portability.
