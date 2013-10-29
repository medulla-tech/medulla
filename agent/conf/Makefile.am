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
nobase_dist_mmcconf_DATA = plugins/ppolicy.ini plugins/dashboard.ini plugins/report.ini \
	agent/keys/cacert.pem agent/keys/localcert.pem
nobase_nodist_mmcconf_DATA = agent/config.ini plugins/base.ini plugins/services.ini

EXTRA_DIST = agent/config.ini.in plugins/base.ini.in plugins/services.ini.in
CLEANFILES = agent/config.ini plugins/base.ini plugins/services.ini

if ENABLE_CONF_BACKUP
INSTALL += --backup=numbered
endif

edit = sed \
        -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
        -e 's|@localstatedir[@]|$(localstatedir)|g' \
        -e 's|@libdir[@]|$(libdir)|g'

plugins/base.ini plugins/services.ini agent/config.ini: Makefile
	rm -f $@ $@.tmp
	$(MKDIR_P) $(@D)
	$(edit) $@.in > $@.tmp
	test "$@ = plugins/base.ini" && test -f /etc/mandriva-release && sed -i 's!log/ldap.log!log/ldap/ldap.log!;s!ou=Groups\b!ou=Group!g;s!ou=Users\b!ou=People!g' $@.tmp || echo Continue
	test "$@ = plugins/services.ini" && test -f /etc/mandriva-release && sed -i 's!systemd-journalctl!journalctl!' $@.tmp || echo Continue
	mv $@.tmp $@
