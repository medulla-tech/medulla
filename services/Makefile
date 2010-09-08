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
3RDPARTY_FOLDER	:= 3rd_party
BUILD_FOLDER	:= build

# WOL stuff
WOL_VERSION	:= 0.7.1
WOL_URI		:= http://downloads.sourceforge.net/project/wake-on-lan/wol/$(WOL_VERSION)
WOL_FOLDER	:= wol-$(WOL_VERSION)
WOL_TARBALL	:= $(WOL_FOLDER).tar.gz

# main target

BUILD_FOLDER = build
SUBDIRS = src

.PHONY: subdirs $(SUBDIRS)

all: subdirs wol

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean: $(SUBDIRS)
	for i in $^; do $(MAKE) -C $$i clean; done
 
wol-clean:
	-$(MAKE) clean -C $(BUILD_FOLDER)/$(WOL_FOLDER)

install: subdirs install-imaging-server

wol:
	[ -e $(3RDPARTY_FOLDER)/$(WOL_TARBALL) ] || wget $(WOL_URI)/$(WOL_TARBALL) -P $(3RDPARTY_FOLDER)
	[ -d $(BUILD_FOLDER)/$(WOL_FOLDER) ] || tar zxf $(3RDPARTY_FOLDER)/$(WOL_TARBALL) -C $(BUILD_FOLDER)
	[ -f $(BUILD_FOLDER)/$(WOL_FOLDER)/Makefile ] || (cd $(BUILD_FOLDER)/$(WOL_FOLDER) && CC="$(CC)" ./configure)
	$(MAKE) -C $(BUILD_FOLDER)/$(WOL_FOLDER) CC=$(CC)
	cp -a $(BUILD_FOLDER)/$(WOL_FOLDER)/src/wol bin/pulse2-wol

install-imaging-server:
	@echo ""
	@echo "Creating directories ..."
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/bootmenus
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/computers
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/custom
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/inventories
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/masters
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/isos
	$(INSTALL) -m 750 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(VARDIR)/archives

	@echo "Installing binaries ..."
	$(INSTALL) -m 755 -o root -g root src/pulse2-imaging-server $(DESTDIR)/$(SBINDIR)/pulse2-imaging-server

	@echo "Installing hooks ..."
	$(INSTALL) -m 755 -o root -g root -d $(DESTDIR)/$(HOOKSDIR)
	$(INSTALL) -m 755 -o root -g root contrib/imaging-server/hooks/* $(DESTDIR)/$(HOOKSDIR)/

	@echo "Installing init files ..."
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-imaging-server $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!g' $(DESTDIR)$(INITDIR)/pulse2-imaging-server

	@echo "Installing config files ..."
	$(INSTALL) -m 755 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) -d $(DESTDIR)/$(ETCDIR)/pulse2/imaging-server
	$(INSTALL) -m 600 -o $(PULSE2_OWNER) -g $(PULSE2_GROUP) conf/pulse2/imaging-server/imaging-server.ini $(DESTDIR)/$(ETCDIR)/pulse2/imaging-server

.PHONY: src
