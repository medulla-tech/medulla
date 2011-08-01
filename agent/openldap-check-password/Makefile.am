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
ldapconfdir = @ldapconfdir@
ldaplibdir = @ldaplibdir@

dist_ldapconf_DATA = mmc-check-password.conf
dist_bin_SCRIPTS = mmc-password-helper

ldaplib_LTLIBRARIES = mmc-check-password.la

mmc_check_password_la_CFLAGS = -I/usr/include/openldap/slapd/ -I/usr/include/openldap/include -DCONFIG_FILE=\"$(ldapconfdir)/mmc-check-password.conf\"
mmc_check_password_la_SOURCES = mmc-check-password.c
mmc_check_password_la_LDFLAGS = -module

