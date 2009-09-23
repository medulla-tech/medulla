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
SBINDIR = $(PREFIX)/sbin
LIBDIR = $(PREFIX)/lib/mmc
ETCDIR = /etc/mmc
INITDIR = /etc/init.d
INSTALL = $(shell which install)
SED = $(shell which sed)

# Python specific variables
PYTHON = $(shell which python)
PYTHON_PREFIX = $(shell $(PYTHON) -c "import sys; print sys.prefix")

# List of files to install
SBINFILES = contrib/msc/pulse2-msc-clean-database contrib/inventory/pulse2-inventory-clean-database

# Extension for backuped configuration files
BACKUP = .$(shell date +%Y-%m-%d+%H:%M:%S)

all:

# Cleaning target
clean:
	@echo ""
	@echo "Cleaning sources..."
	@echo "Nothing to do"

# Install everything
install:
	@# Install directories
	@echo "Creating directories..."
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(PYTHON_PREFIX)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install CONFILES in $(DESTDIR)$(ETCDIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers/keys
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server/keys
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler/keys
	$(INSTALL) conf/plugins/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) conf/pulse2/inventory-server/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/inventory-server
	$(INSTALL) conf/pulse2/launchers/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers/keys
	$(INSTALL) conf/pulse2/launchers/*.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/launchers
	$(INSTALL) conf/pulse2/package-server/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server/keys
	$(INSTALL) conf/pulse2/package-server/*.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/package-server
	$(INSTALL) conf/pulse2/scheduler/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler/keys
	$(INSTALL) conf/pulse2/scheduler/*.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2/scheduler
	$(INSTALL) conf/pulse2/*.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/pulse2

	@echo ""
	@echo "Install additionnal tools in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) $(SBINFILES) -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

include common.mk

$(RELEASES_DIR)/$(TARBALL_GZ):
	mkdir -p $(RELEASES_DIR)/$(TARBALL)
	$(CPA) services/pulse2 common.mk services/conf services/contrib Makefile services/mmc services/setup.py services/COPYING services/Changelog $(RELEASES_DIR)/$(TARBALL)
	cd $(RELEASES_DIR) && tar -czf $(TARBALL_GZ) $(EXCLUDE_FILES) $(TARBALL); rm -rf $(TARBALL);

