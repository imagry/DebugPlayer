
# Windsurf Global Rules (Enhanced)
*Date: 2025-05-14*
*Project: rectangle pose estimation*
*Prepared for Agentic Coding with Windsurf*

---

## 1. Context and Goal Management
- Always show current module scope, e.g.:
  > "We are working on [current task name]. Goal: [current task goal]."
- Explicitly state if current goal is **Design**, **Implementation**, **Refactor**, or **Optimization**.
- Every new task starts with a 1-2 line recap of previous decisions.

## 2. Change Management
- Never assume unstated requirements.
- Refactors must preserve existing behavior unless instructed otherwise.
- Always summarize intended changes before code updates.
- When modifying algorithms, list all edge cases considered before altering logic.

## 3. Interface and Contract Discipline
- All functions/classes must have well-defined interfaces.
- Any signature change triggers a dependency impact warning.
- Propose interface changes with an explicit list of impacted functions/classes.

## 4. Focus and Step-by-Step Development
- Follow strict modularity: one module, one goal, one step at a time.
- Design and implementation are not to be combined unless explicitly approved.
- No skipping validation or test design stages.
- Large transformations must be micro-staged with explicit checkpoints.

## 5. Testing and Validation Enforcement
- Propose corresponding test cases for every new feature or refactor.
- Tests must cover edge cases and failure modes explicitly.
- Design validation and verification of outputs **alongside code**, not after.
- For optimization-focused stages:
  - Mandatory lightweight profiling (runtime, memory).
  - Profiling outputs (plots/tables) included in PR/test artifacts.

## 6. Traceability and Alignment
- All architectural/algorithmic assumptions must be recorded and referenced.
- Major design decisions must be restated before proceeding.
- Maintain a simple running log of decisions.
- **Enhancement**: Tag each decision log with:
  - **Decision Severity**: Critical, Major, Minor.
  - **Scope of Impact**: Module, Global, Interface.

## 7. Code Style and Documentation
- Match existing project coding style unless specified otherwise.
- Every function must have a docstring answering: **What**, **Why**, and **How**.
- Complex algorithms require short inline explanations for major steps.

## 8. Forbidden Practices
- No silent assumptions.
- No major changes without prior check-in.
- No black-box outputs for algorithmic components (inner workings must be exposed).
- No changes that reduce modularity or testing capability.

## 9. Default Settings
- Python 3.9+
- Use NumPy for numerical operations.
- Use Matplotlib for visualization.
- Type hints are mandatory and consistent.
- Optimize for readability over premature optimization.
- Maintain modular code structure (vehicle model, path loading, adaptation, simulation, visualization in separate files).
- Follow PEP8 style guide.
- Recommend Conda environment management.
- **Enhancement**:
  - Every module must define reproducibility context (conda env YAML, RNG seeds).
  - Mandatory version pinning for core dependencies (NumPy, Matplotlib, etc.).
  - Suggested: `poetry` or `conda-lock` for environment reproducibility.

## 10. Error Handling and Fault Tolerance (New)
- All functions must define behavior for invalid inputs and edge cases.
- Explicit decision per module: fail fast (raise exceptions) or degrade gracefully (warn + fallback).
- Document error handling strategy in module README.

## 11. CI/CD and Code Review Discipline (New)
- Every code change requires peer review before merging.
- Automated linting, formatting, and basic tests must pass before review.
- Experimental branches must be labeled with `[EXPERIMENT]` in PR titles.

## 12. Prompt Feedback Loop (New)
- For each Windsurf task, log the following:
  - Initial Prompt.
  - Agent Response.
  - Human Feedback & Adjustments.
  - Final Output Summary.
- Maintain a lightweight “Prompt Learning Log” to improve prompting strategies over time.

---
**Core Principles Reaffirmed**:
- Modularity is sacred.
- Traceability is non-negotiable.
- Validation is continuous, not afterthought.
- No change without context.
- Every decision leaves breadcrumbs.