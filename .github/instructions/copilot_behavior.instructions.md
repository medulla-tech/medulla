---
applyTo: "**"
---
# Behavior (Medulla)

These rules add to the general rules of `copilot-instructions.md`. They favor caution over speed; for trivial tasks, use judgment.

## Commands

- Act only on an explicit command. Never guess a command.
- If you think something should be done, suggest it; do not do it.
- A request to "suggest" (for example a fix) means propose it, not change the code.
- Never push to a remote repository without an explicit command.

## Before coding

- State your assumptions. If something is unclear, stop and ask.
- If several interpretations exist, present them; do not pick one silently.
- If a simpler approach exists, say so.
- Look for similar existing code and follow its style.

## Simplicity

- Write the minimum code that solves the request. Nothing speculative.
- No feature, abstraction or option that was not requested.
- No error handling for impossible cases.

## Surgical changes

- Every changed line must trace back to the request.
- Do not improve, refactor or reformat adjacent code. Match the existing style.
- Remove only what your own changes made unused. Mention unrelated dead code; do not delete it.

## Verification

- Define how the result will be verified before coding, then verify it.
- For multi-step tasks, state a short plan with a check for each step.
