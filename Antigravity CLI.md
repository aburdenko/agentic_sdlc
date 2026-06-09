## Antigravity CLI Developer Guide

This developer guide is optimized for the **Antigravity CLI** (`agy` / `antigravity`) operating in the `agent-skills` workspace.

The three-tier framework (Skills, Personas, Commands) described here maps natively to the capabilities of the **Antigravity Platform** and the **Agent Development Kit (ADK)** (such as using remote Managed Agents via the Agent2Agent/A2A protocol and local Subagent parallel fan-out orchestration). For full details, see the [Antigravity ADK Integration Guide](file:///home/user/agentic_sdlc/docs/antigravity-adk-integration.md).

## Project Structure

```plaintext
skills/          → Core skills (each with its own `SKILL.md` and optional `scripts/`)
agents/          → Reusable agent personas (code-reviewer, test-engineer, security-auditor)
hooks/           → Session lifecycle hooks
.gemini/         → Workspace-scoped Antigravity config and skills
  skills/        → Installed workspace-scoped skills
references/      → Supplementary checklists (testing, performance, security, accessibility)
docs/            → Setup and anatomy guides (including [Antigravity ADK Integration Guide](file:///home/user/agentic_sdlc/docs/antigravity-adk-integration.md))
scripts/         → Developer utilities and validator scripts
```

## Skills by Phase

*   **Define:** `interview-me`, `idea-refine`, `spec-driven-development`
*   **Plan:** `planning-and-task-breakdown`
*   **Build:** `incremental-implementation`, `test-driven-development`, `context-engineering`, `source-driven-development`, `doubt-driven-development`, `frontend-ui-engineering`, `api-and-interface-design`
*   **Verify:** `browser-testing-with-devtools`, `debugging-and-error-recovery`
*   **Review:** `code-review-and-quality`, `code-simplification`, `security-and-hardening`, `performance-optimization`
*   **Ship:** `git-workflow-and-versioning`, `ci-cd-and-automation`, `deprecation-and-migration`, `documentation-and-adrs`, `shipping-and-launch`

## Key Environment Configuration

*   **Vertex AI Agent Engine Location:** Resources must default to `us-central1` (requires regional API endpoints like `us-central1-discoveryengine.googleapis.com`).
*   **Discovery Engine (Agent Builder):** Use the `us` multiregion. Note that `us-central1` is not a valid location for Discovery Engine Engine creation, though they can integrate with `us-central1` Dialogflow Agents.
*   **Medium Publishing Workflow:** Uses a non-headless Playwright browser (`headless=False`) running inside a virtual display provided by `xvfb-run`. Playwright should always be configured to use its bundled browser rather than system chrome.

## Conventions & Style

*   **Skill Anatomy:** Every skill must reside in `skills/<name>/SKILL.md`.
*   **YAML Frontmatter:** Every `SKILL.md` must contain a `name` matching the directory exactly and a `description` \<= 1024 characters starting in third-person followed by "Use when...".
*   **Required Sections:** Standard skills must include `## Overview`, `## When to Use`, `## Common Rationalizations`, `## Red Flags`, and `## Verification`.
*   **Exemptions:** Only `using-agent-skills` and `idea-refine` are exempt from section validation (hardcoded in `scripts/validate-skills.js`).
*   **File Lengths:** Keep `SKILL.md` files under 500 lines to minimize context window usage. Put larger reference content into supporting markdown files.
*   **Cross-References:** Link between skills using canonical phrasing (e.g., `use the \`\[skill-name\]\` skill`,` see \`\[skill-name\]\`\`) to satisfy the validator.

## Essential Commands

### Validation

*   **Validate Skill Files:** Validate all skills in the project against frontmatter, required headings, and cross-reference constraints:

### Local Development & Integration

*   **Run ADK Web with Logging:** Start the ADK local logging proxy server:
*   **Interact with Web UI:** Ensure you run/interact with the Web UI to generate local logs before executing any evaluation scripts (e.g. `eval_agent.py` or ADK eval).
*   **Run configure.sh:** Run `./.scripts/configure.sh` to install system packages (`xvfb`, etc.) and set up python virtual environments.

## Boundaries

*   **Always**: Run `node scripts/validate-skills.js` before submitting any skill modifications or additions.
*   **Always**: Build incremental changes as thin vertical slices, verifying step-by-step.
*   **Never**: Add vague advice skills. All skills must describe structured, actionable processes with explicit exit criteria.
*   **Never**: Duplicate content between skills — link/reference other skills instead.

```plaintext
python3 .scripts/run_adk_web_with_logging.py
```

```plaintext
node scripts/validate-skills.js
```