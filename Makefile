# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA



# General Makefile variables
DESTDIR =
PREFIX = /usr/local
DATADIR = $(PREFIX)/share/mmc
MODULESWEBSUBDIR = /modules/
SBINDIR = $(PREFIX)/sbin
LIBDIR = $(PREFIX)/lib/mmc
ETCDIR = /etc/mmc
INITDIR = /etc/init.d
INSTALL = $(shell which install)
SED = $(shell which sed)
CP = $(shell which cp)
CHOWN = $(shell which chown)
CHGRP = $(shell which chgrp)

# Python specific variables
PYTHON = $(shell which python)
PYTHON_PREFIX = $(shell $(PYTHON) -c "import sys; print sys.prefix")

# List of files to install
SBINFILES = bin/pulse2-package-server contrib/msc/pulse2-msc-clean-database contrib/inventory/pulse2-inventory-clean-database bin/pulse2-inventory-server bin/pulse2-scheduler bin/pulse2-scheduler-manager bin/pulse2-launcher bin/pulse2-launchers-manager bin/pulse2-output-wrapper bin/pulse2-ping bin/pulse2-wol bin/pulse2-tcp-sproxy

FILESTOINSTALL = modules/dyngroup modules/msc modules/inventory modules/glpi modules/pkgs modules/pulse2

# Extension for backuped configuration files
BACKUP = .$(shell date +%Y-%m-%d+%H:%M:%S)

all:

# Cleaning target
clean: clean_mo
	@echo ""
	@echo "Cleaning sources..."
	@echo "Nothing to do"

clean_mo:
	sh scripts/clean_mo.sh

build_mo:
	sh scripts/build_mo.sh

build_pot:
	sh scripts/build_pot.sh

# Install everything
install: build_mo
	@# Install directories
	@echo ""
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -f $(DESTDIR)$(ETCDIR)/package-server.ini ] && mv -f $(DESTDIR)$(ETCDIR)/package-server.ini $(DESTDIR)$(ETCDIR)/package-server.ini$(BACKUP)
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -f $(DESTDIR)$(ETCDIR)/inventory-server.ini ] && mv -f $(DESTDIR)$(ETCDIR)/inventory-server.ini $(DESTDIR)$(ETCDIR)/inventory-server.ini$(BACKUP)
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -f $(DESTDIR)$(ETCDIR)/scheduler.ini ] && mv -f $(DESTDIR)$(ETCDIR)/scheduler.ini $(DESTDIR)$(ETCDIR)/scheduler.ini$(BACKUP)
	@echo "Move old configuration files to $(DESTDIR)$(ETCDIR)$(BACKUP)"
	-[ -f $(DESTDIR)$(ETCDIR)/launchers.ini ] && mv -f $(DESTDIR)$(ETCDIR)/launchers.ini $(DESTDIR)$(ETCDIR)/launchers.ini$(BACKUP)
	@echo ""
	@echo "Creating directories..."
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(PYTHON_PREFIX)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Installing mmc-web-dyngroup in $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)
	$(CP) -R $(FILESTOINSTALL) $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)
	$(CHOWN) -R root $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)
	$(CHGRP) -R root $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)
	find $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)/*/locale -type f -name \*.po -exec rm -f {} \;
	find $(DESTDIR)$(DATADIR)$(MODULESWEBSUBDIR)/ -depth -type d -name .svn -exec rm -fr {} \;

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install SBINFILES in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) $(SBINFILES) -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Install CONFILES in $(DESTDIR)$(ETCDIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) conf/plugins/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server
	$(INSTALL) conf/pulse2/package-server/package-server.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server
	$(INSTALL) conf/pulse2/package-server/keys -d -m 700 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server/keys
	$(INSTALL) conf/pulse2/package-server/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server/keys/
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server
	$(INSTALL) conf/pulse2/inventory-server/inventory-server.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server
	$(INSTALL) conf/pulse2/inventory-server/keys -d -m 700 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server/keys
	$(INSTALL) conf/pulse2/inventory-server/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server/keys/
	$(INSTALL) contrib/OcsNGMap.xml -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server/
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler
	$(INSTALL) conf/pulse2/scheduler/scheduler.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler
	$(INSTALL) conf/pulse2/scheduler/keys -d -m 700 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler/keys
	$(INSTALL) conf/pulse2/scheduler/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler/keys/
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers
	$(INSTALL) conf/pulse2/launchers/launchers.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers
	$(INSTALL) conf/pulse2/launchers/keys -d -m 700 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers/keys
	$(INSTALL) conf/pulse2/launchers/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers/keys/

	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(INITDIR)
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-package-server $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/pulse2-package-server
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-inventory-server $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/pulse2-inventory-server
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-scheduler $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/pulse2-scheduler
	$(INSTALL) -m 755 -o root -g root init.d/pulse2-launchers $(DESTDIR)$(INITDIR)
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/pulse2-launchers

	@echo ""
	@echo "Install additionnal tools in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) $(SBINFILES) -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

include common.mk

$(RELEASES_DIR)/$(TARBALL_GZ):
	mkdir -p $(RELEASES_DIR)/$(TARBALL)
	$(CPA) web/modules web/scripts services/bin services/pulse2 services/init.d common.mk services/conf services/contrib Makefile services/mmc services/setup.py services/COPYING services/Changelog $(RELEASES_DIR)/$(TARBALL)
	cd $(RELEASES_DIR) && tar -czf $(TARBALL_GZ) $(EXCLUDE_FILES) $(TARBALL); rm -rf $(TARBALL);

