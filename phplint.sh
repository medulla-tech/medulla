#!/bin/sh

log=`mktemp`
error=0

# Find all PHP files
for file in `find . -name '*.inc' -o -name '*.php' -print`; do
  php -l ${file} 2>>"${log}" >/dev/null
done

# Print log of failures only
while read line; do
  echo "${line}" | grep -q '^No syntax errors detected in '
  if [ ! $? -eq 0 ]; then
    echo "${line}"
    error=`expr ${error} + 1`
  fi
done < "${log}"

test -f "${log}" && rm -f "${log}"

exit ${error}
