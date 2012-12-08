#!/bin/sh

log=`mktemp`
error=0
pyflakes . >"${log}" 2>&1

# Print log without manual ignores
while read line; do
  file=`echo "${line}" | cut -d':' -f1`
  linenb=`echo "${line}" | cut -d':' -f2`
  # Check if the line found by flkages contains the excluding pattern
  cat "${file}" | head -n ${linenb} | tail -n 1 | grep -q "# pyflakes.ignore"
  # If not, print the error line and increment error nb
  if [ ! $? -eq 0 ]; then
    echo "${line}"
    error=`expr ${error} + 1`
  fi
done < "${log}"

test -f "${log}" && rm -f "${log}"

exit ${error}
