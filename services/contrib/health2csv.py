#!/usr/bin/python
#
# (c) 2009 Mandriva, http://www.mandriva.com/
#
# $Id: command_evolution_from_coh_table.py 833 2009-12-08 10:22:41Z nrueff $
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import sys
import re

HEALTH_STR = r"""^(\S+ \S+),[0-9]+ INFO scheduler \S+: HEALTH: (.*)$"""
HEALTH_RE = re.compile(HEALTH_STR)

if len(sys.argv) != 2:
    print "usage : %s <log-file>" % sys.argv[0]
    sys.exit(1)

log_file = sys.argv[1]


try:
    log_fd = open(log_file)
except Exception, e:
    print "Error opening %s : %s" % (log_file, e)
    sys.exit(1)

data = dict()
for line in log_fd:
    match_obj = HEALTH_RE.search(line)
    if match_obj :
        ts = match_obj.group(1)
        val = match_obj.group(2)
        if ts in data:
            print "Double data found : %s" % (ts)
            sys.exit(1)
        data[ts] = eval(val)

# recover header, using first record
headers = list()
for k1 in data[data.keys()[0]].keys():
    for k2 in data[data.keys()[0]][k1].keys():
        headers.append("%s:%s" % (k1, k2))
headers.sort()
print ';'.join(['time'] + headers)

stamps = data.keys()
stamps.sort()

for t in stamps:
    d = data[t]
    v = list()
    for h in headers:
        (h1, h2) = h.split(':')
        v.append(str(d[h1][h2]))
    print ';'.join([t] + v)

#MDV/NR print data

