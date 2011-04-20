# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Pulse2 project.
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s):
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
mmcconfdir = $(sysconfdir)/mmc
mmcconffiles = \
	pulse2/package-server/package-server.ini pulse2/inventory-server/inventory-server.ini \
	pulse2/scheduler/scheduler.ini pulse2/launchers/launchers.ini 

certpaths = \
	pulse2/package-server/keys/ pulse2/inventory-server/keys/ pulse2/scheduler/keys/ \
	pulse2/launchers/keys/
certca = $(patsubst %,%/cacert.pem,$(certpaths))
certpriv = $(patsubst %,%/privkey.pem,$(certpaths))
certfiles = $(certca) $(certpriv)

EXTRA_DIST = $(patsubst %,$(srcdir)/%,$(mmcconffiles)) $(patsubst %,$(srcdir)/%,$(certfiles))

if ENABLE_CONF_BACKUP
# Extension for beckup'd configuration files
confbackup = yes
backupext = .$(shell date +%Y-%m-%d+%H:%M:%S)
endif

# exec'ed after install-data

# If ENABLE_CONF_BACKUP, backup configuration files
# and install conf files
install-data-local:
	if [ "x$(confbackup)" = "xyes" ]; then \
	  for file in $(mmcconffiles) $(certfiles); do \
	    if [ -f "$(DESTDIR)$(mmcconfdir)/$$file" ]; then \
	      cp -f "$(DESTDIR)$(mmcconfdir)/$$file" "$(DESTDIR)$(mmcconfdir)/$$file$(backupext)"; \
	    fi; \
	  done; \
	fi
	for file in $(mccconffiles) $(certfiles); do \
	  dirname=`dirname $$file`; \
	  $(MKDIR_P) $(DESTDIR)$(mmcconfdir)/$$dirname; \
	  $(install_sh) -m 600 $(srcdir)/$$file $(DESTDIR)$(mmcconfdir)/$$dirname/; \
	done

uninstall-local:
	for file in $(mccconffiles) $(certfiles); do \
	   rm -f $(DESTDIR)$(mmcconfdir)/$$file; \
	done
