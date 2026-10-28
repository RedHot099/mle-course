---
name: setup
description: Help prepare the notebook or the small project from A3 and B7.2.
---

# Setup

Read A3 (`lectures/foundations/a3-environment.html`) and the learner's environment notes. For GitHub access read B7.2. Ask which system and exact command are involved if unknown.

1. Diagnose read-only: current directory, uv version, exact traceback and project files. Explain each command before running it. Never print credentials or notebook access tokens.
2. Fix dependencies inside the learner's project when authorized; respect machine-level restrictions. System installation, restarts and administrator work belong to the learner or their administrator, not the agent. Follow the official documentation linked by the lesson. Retry transient downloads using the configured retry options.
3. Verify the immediate outcome: notebook starts, the chosen Python environment runs a cell, and a saved notebook reproduces after kernel restart. For Git, confirm local identity and authentication without exposing secrets. Git push and external writes require explicit instructions.
4. Record the working directory, environment and any deferred issue in `.course/progress.md`. Continue with the next available concept if account access is blocked.

The core uses small tables and CPU. Start with the environment required by the current lesson. For a killed kernel consult `tutor/low-memory.md`.
