---
applyTo: "**/*.php"
---
# PHP file header (Medulla)

Every new or significantly modified PHP file starts with a header that ends with a `file :` line giving its path relative to the repository (separator `/`, never an absolute path).

## Order

1. PHP opening tag, `<?php`.
2. SPDX lines, using `//` comments.
3. `// file : <relative/path.php>`
4. The rest of the file.

## New file

```php
<?php
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/example/example.php
```

Use the current year in the copyright line.

## Existing file

- Keep the SPDX lines already present, in the same order, even if the copyright holder differs (Medulla, Siveo, Linbox, Mandriva).
- Add the `file :` line right after them if it is missing. Do not reorder anything else.
- Do not add other information to the header.
