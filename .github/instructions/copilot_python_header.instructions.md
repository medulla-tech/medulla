---
applyTo: "**/*.py"
---
# Python file header (Medulla)

Every new or significantly modified Python file starts with a header that ends with a `file :` line giving its path relative to the repository (separator `/`, never an absolute path).

## Order

1. Shebang, only for executable scripts (never for pure modules).
2. Encoding declaration, only if needed.
3. SPDX lines.
4. `# file : <relative/path.py>`
5. The rest of the file.

## New file

```python
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/mmc/plugins/example/__init__.py
```

Use the current year in the copyright line.

## Existing file

- Keep the SPDX lines already present, in the same order, even if the copyright holder differs (Medulla, Siveo, Linbox, Mandriva).
- Add the `file :` line right after them if it is missing. Do not reorder anything else.
- Do not add other information to the header.
