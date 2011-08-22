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
clientsdir = $(localstatedir)/lib/pulse2/clients/win32
dist_clients_SCRIPTS = build.sh
clients_DATA = sfx.conf.in win32.mk 7zsd.sfx \
	remote-desktop-agent.reg remote-desktop-agent-vnc2.reg

EXTRA_DIST = \
	build.sh \
	win32.mk.in \
	sfx.conf.in \
	7zsd.sfx \
	remote-desktop-agent.reg \
	remote-desktop-agent-vnc2.reg

CLEANFILES = win32.mk

edit = sed \
	-e 's|@VERSION[@]|$(VERSION)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g'

win32.mk: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	  test -f ./$@.in || srcdir=$(srcdir)/; \
	  $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

win32.mk: win32.mk.in
