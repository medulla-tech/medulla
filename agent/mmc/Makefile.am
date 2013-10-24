# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
pythonmodules = support plugins plugins.base plugins.ppolicy \
	core core.audit client plugins.dashboard plugins.dashboard.panels \
	plugins.services core.signals

all-local: site.py

# Expands Python modules list with found *.py files in each module given in pythonmodules
mmcpythondir = $(pythondir)/$(notdir $(realpath $(srcdir)))
nobase_mmcpython_PYTHON = $(wildcard *.py $(patsubst %,$(srcdir)/%/*.py ,$(subst .,/,$(pythonmodules))))
nodist_mmcpython_PYTHON = site.py

EXTRA_DIST = site.py.in
CLEANFILES = site.py

edit = sed \
        -e 's|@bindir[@]|$(bindir)|g' \
        -e 's|@sbindir[@]|$(sbindir)|g' \
        -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' \
        -e 's|@prefix[@]|$(prefix)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g' \
        -e 's|@mmcconfdir[@]|$(mmcconfdir)|g' \
        -e 's|@sysconfdir[@]|$(sysconfdir)|g'

site.py: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@
