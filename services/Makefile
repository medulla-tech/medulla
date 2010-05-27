#
# (c) 2009-2010 Mandriva, http://www.mandriva.com
#
# $Id$
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
# along with Pulse 2. If not, see <http://www.gnu.org/licenses/>.
#

# General Makefile variables
PULSE2_OWNER	:= root
PULSE2_GROUP	:= root
PREFIX 		:= /usr/local
VARDIR 		:= /var/lib/pulse2/imaging
VARIMAGINGDIR	:= $(VARDIR)/imaging-server
HOOKSDIR	:= $(PREFIX)/lib/pulse2/imaging-server/hooks
SBINDIR 	:= $(PREFIX)/sbin
INITDIR 	:= /etc/init.d
ETCDIR 		:= /etc/mmc
INSTALL		:= $(shell which install)
SED		:= $(shell which sed)

# main target

BUILD_FOLDER = build/
SUBDIRS = src

.PHONY: subdirs $(SUBDIRS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean: $(SUBDIRS)
	for i in $^; do $(MAKE) -C $$i clean; done

install: subdirs install-imaging-server

install-imaging-server:
	@echo ""
	@echo "Creating directories ..."
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/bootmenus
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/computers
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/custom
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/inventories
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/masters
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/isos
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(VARDIR)/archives

	@echo "Installing binaries ..."
	$(INSTALL) -m 755 -o root -g root src/pulse2-imaging-server $(SBINDIR)/pulse2-imaging-server

	@echo "Installing hooks ..."
	$(INSTALL) -m 755 -o root -g root -d $(HOOKSDIR)
	$(INSTALL) -m 755 -o root -g root contrib/imaging-server/hooks/* $(HOOKSDIR)/

	@echo "Installing init files ..."
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-imaging-server $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!g' $(DESTDIR)$(INITDIR)/pulse2-imaging-server

	@echo "Installing config files ..."
	$(INSTALL) -m 755 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(ETCDIR)/pulse2/imaging-server
	$(INSTALL) -m 755 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) conf/pulse2/imaging-server/imaging-server.ini $(ETCDIR)/pulse2/imaging-server

.PHONY: src
