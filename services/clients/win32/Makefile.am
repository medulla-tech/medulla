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

installernsi = pulse2-win32-agents-installer.nsi.in
installerdata = \
	artwork/header.bmp \
	artwork/uninstall.ico \
	artwork/wizard.bmp \
	artwork/install.ico \
	libs/StrRep.nsh \
	libs/ServiceLib.nsh \
	libs/InstallOptionsMacro.nsh \
	inventoryoptions.ini

dist_clients_SCRIPTS = generate-agent-pack.sh.in
dist_doc_DATA = README.win32

clients_SCRIPTS = generate-agent-pack.sh
clients_DATA = \
	sfx.conf.in \
	sfx.noprompt.conf.in \
	sfx.silent.conf.in \
	$(installernsi)
nobase_clients_DATA =  $(installerdata)

CLEANFILES = generate-agent-pack.sh

EXTRA_DIST = \
	sfx.conf.in \
	sfx.noprompt.conf.in \
	sfx.silent.conf.in \
	$(installernsi) \
	$(installerdata)

edit = sed -e 's|@sysconfdir[@]|$(sysconfdir)|g'

generate-agent-pack.sh: generate-agent-pack.sh.in
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	srcdir=''; \
	test -f ./$@.in || srcdir=$(srcdir)/; \
		$(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@
