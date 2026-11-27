# Medulla: Copilot general instructions

This is the base file of the general context for Copilot. It applies to Medulla repositories. A repository may refine it with its own files when needed.

## How the context is organized

- This file is the base. It does not hold detailed rules.
- Rules are added one small file per topic in `.github/instructions/`.
- Files for Copilot are prefixed `copilot_` and end with `.instructions.md` (example: `copilot_security.instructions.md`). Every such file present is part of these instructions.
- Adding a topic means adding a file. This base file does not need to change.
- Files without the `copilot_` prefix are not Copilot instructions.

## General rules

- Do nothing without an explicit request; propose a plan before coding.
- Keep changes minimal and local. Preserve public APIs, file headers and docstrings.
- Never expose secrets (passwords, keys, tokens) in code, commands or logs.
