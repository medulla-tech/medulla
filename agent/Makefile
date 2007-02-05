# Copyright (C) 2006, Adam Cecile for Linbox FAS
# Copyright (C) 2006, Jerome Wax for Linbox FAS
# Copyright (C) 2006, Cedric Delfosse for Linbox FAS
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
LIBDIR = $(PREFIX)/lib/lmc
ETCDIR = /etc/lmc
INITDIR = /etc/init.d
INSTALL = $(shell which install)
SED = $(shell which sed)

# Python specific variables
PYTHON = $(shell which python)
PYTHON_PREFIX = $(shell $(PYTHON) -c "import sys; print sys.prefix")

# List of files to install
LIBFILES = bin/add_machine_script
LIBFILESBACKUP = backup-tools/cdlist backup-tools/backup.sh
LIBDIRBACKUP = $(LIBDIR)/backup-tools
SBINFILES = bin/lmc-agent

all:

# Cleaning target
clean:
	@echo ""
	@echo "Cleaning sources..."
	@echo "Nothing to do"

# Install everything
install: 
	@# Install directories
	@echo ""
	@echo "Creating directories..."
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(SBINDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(LIBDIRBACKUP)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install python code in $(DESTDIR)$(PYTHON_PREFIX)"
	$(PYTHON) setup.py install --no-compile --prefix $(DESTDIR)$(PYTHON_PREFIX)

	@echo ""
	@echo "Install LIBFILES in $(DESTDIR)$(LIBDIR)"
	$(INSTALL) $(LIBFILES) -m 755 -o root -g root $(DESTDIR)$(LIBDIR)

	@echo ""
	@echo "Install LIBDIRBACKUP in $(DESTDIR)$(LIBDIRBACKUP)"

	$(INSTALL) $(LIBFILESBACKUP) -m 755 -o root -g root $(DESTDIR)$(LIBDIRBACKUP)

	@echo ""
	@echo "Install SBINFILES in $(DESTDIR)$(SBINDIR)"
	$(INSTALL) $(SBINFILES) -m 755 -o root -g root $(DESTDIR)$(SBINDIR)

	@echo ""
	@echo "Install CONFILES in $(DESTDIR)$(ETCDIR)"
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) conf/agent/config.ini -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/agent
	$(INSTALL) conf/agent/keys/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/agent/keys
	$(INSTALL) conf/plugins/* -m 600 -o root -g root $(DESTDIR)$(ETCDIR)/plugins
	$(INSTALL) -d -m 755 -o root -g root $(DESTDIR)$(INITDIR)
	$(INSTALL) -m 755 -o root -g root init.d/lmc-agent $(DESTDIR)$(INITDIR)
	$(SED) -i 's!^path[ \t].*$$!path = $(LIBDIR)/backup-tools!' $(DESTDIR)$(ETCDIR)/plugins/base.ini
	$(SED) -i 's!##SBINDIR##!$(SBINDIR)!' $(DESTDIR)$(INITDIR)/lmc-agent

# Linbox internal target. Will be updated soon.

debian-package: revision
	sed -i "s/##VERSION##/`cat revision`/" debian/changelog
	sed -i "s/###SVN_VERSION###/`cat revision`/" lmc/agent.py
	dpkg-buildpackage -b -uc -rfakeroot
	sed -i "s/`cat revision`/##VERSION##/" debian/changelog
	sed -i "s/`cat revision`/###SVN_VERSION###/" lmc/agent.py

revision:
	# fake SVN revision number if there is none
	# else the revision number is found by BuildBot
	echo -n 100 > "revision"

move: debian-package docs
	mv ../*.deb /var/www/portail/lmc-packages/
	rm -fr /var/www/portail/lmc-docs/lmc-agent
	mv -f html /var/www/portail/lmc-docs/lmc-agent
	chmod -R 755 /var/www/portail/lmc-docs/lmc-agent

docs:
	epydoc lmc

test:
	PYTHONPATH=. python tests/testldap.py
	PYTHONPATH=. python tests/testsamba.py
	PYTHONPATH=. python tests/testproxy.py
	PYTHONPATH=. python tests/testmail.py

lint:
	pylint --disable-all --html=y --enable-variables=y lmc/*.py lmc/support/*.py lmc/plugins/*.py > /var/www/portail/lmc-lint.html
	chmod 755 /var/www/portail/lmc-lint.html

fixmetodo:
	grep -nir -e FIXME -e TODO * > /var/www/portail/lmc-fixmetodo.txt
	chmod 755 /var/www/portail/lmc-fixmetodo.txt
