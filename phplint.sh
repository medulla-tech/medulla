#!/bin/sh

error=0

# Lint all PHP files, reporting only failures
for file in $(find . \( -name '*.inc' -o -name '*.php' \) -print); do
  php -l "${file}" >/dev/null || error=1
done

exit ${error}
