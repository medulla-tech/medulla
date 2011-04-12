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
# Author(s)
#   Jean Parpaillon <jparpaillon@mandriva.com>
#
mmcconfdir = $(sysconfdir)/mmc
mmcconffiles = \
	agent/config.ini plugins/base.ini plugins/ppolicy.ini \
	agent/keys/cacert.pem agent/keys/localcert.pem

EXTRA_DIST = $(mmcconffiles)

if ENABLE_CONF_BACKUP
# Extension for beckup'd configuration files
confbackup = yes
backupext = .$(shell date +%Y-%m-%d+%H:%M:%S)
endif

# exec'ed after install-data

# If ENABLE_CONF_BACKUP, backup configuration files
# and install conf files
install-data-local:
	if [ "x$(confbackup)" = "xyes" -a -d "$(DESTDIR)$(mmcconfdir)" ]; then \
	  mv -f "$(DESTDIR)$(mmcconfdir)" "$(DESTDIR)$(mmcconfdir)$(backupext)"; \
	fi
	for path in $(mmcconffiles); do \
	  dirname=`dirname $$path`; \
	  $(MKDIR_P) $(DESTDIR)$(mmcconfdir)/$$dirname; \
	  $(install_sh) -m 600 $(srcdir)/$$path $(DESTDIR)$(mmcconfdir)/$$dirname/; \
	done

uninstall-local:
	for path in $(mmcconffiles); do \
	  rm -f $(DESTDIR)$(mmcconfdir)/$$path; \
	done
