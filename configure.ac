dnl configure.in for Pulse2 project.
dnl (c) 2011 mandriva, http://www.mandriva.com
dnl
dnl This file is part of Mandriva Management Console (MMC).
dnl
dnl MMC is free software; you can redistribute it and/or modify
dnl it under the terms of the GNU General Public License as published by
dnl the Free Software Foundation; either version 2 of the License, or
dnl (at your option) any later version.
dnl
dnl MMC is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl GNU General Public License for more details.
dnl
dnl You should have received a copy of the GNU General Public License
dnl along with MMC.  If not, see <http://www.gnu.org/licenses/>.
dnl Process this file with autoconf to produce a configure script.

dnl autoconf version
AC_PREREQ(2.59)

dnl autoconf initialization
AC_INIT([pulse2], [1.3.1], [http://www.mandriva.com])

AC_CANONICAL_BUILD
AC_CANONICAL_HOST
AC_CANONICAL_TARGET

AM_INIT_AUTOMAKE([-Wno-portability])
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES(yes)])
AC_CONFIG_MACRO_DIR([m4])

dnl check for programs
AC_PROG_CC
AC_PROG_MAKE_SET
AC_PROG_LN_S
AC_PROG_LIBTOOL
AC_PROG_INSTALL
dnl Check for Python
AM_PATH_PYTHON([2.5])

# gettext: prepare the translation directories.
AM_PO_SUBDIRS
if test "x$USE_NLS" = "xyes"; then
   AC_CHECK_PROG(HAVE_MSGFMT, msgfmt,yes,no)

   if test "x$HAVE_MSGFMT" = "xno"; then
          AC_MSG_ERROR([msgfmt not found. You need to install the 'gettext' package, or pass --enable-nls=no to configure.])
   fi
fi

dnl check for libraries

dnl Check for Python modules
AX_PYTHON_MODULE([sqlalchemy], [1])
AX_PYTHON_MODULE([MySQLdb], [1])
AX_PYTHON_MODULE([twisted.web], [1])

dnl check for headers
AC_HEADER_STDC

dnl Add strictness options to the compiler
CFLAGS="$CFLAGS -Wall -Werror"
AC_SUBST(CFLAGS)
AC_SUBST(CPPFLAGS)
AC_SUBST(LDFLAGS)

dnl
dnl --disable-conf-backup
dnl   Disable backup configuration file
dnl
AC_ARG_ENABLE([conf-backup],
              [AS_HELP_STRING([--disable-backup-conf],
                              [Disable configuration files backup, if any @<:@default=enable@:>@])],
              [],
              [enable_conf_backup="yes"])
AM_CONDITIONAL([ENABLE_CONF_BACKUP], [test "$enable_conf_backup" = "yes"])

dnl
dnl --disable-wol
dnl   Fetch and compile wake-on-lan tool (3rd party)
dnl
AC_ARG_ENABLE([wol],
              [AS_HELP_STRING([--disable-wol],
                              [Disable wake-on-lan tool (3rd party) @<:@default=enable@:>@])],
              [],
              [enable_wol="yes"])
AM_CONDITIONAL([ENABLE_WOL], [test "$enable_wol" = "yes"])

dnl files to generate with automake
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([services/Makefile])
AC_CONFIG_FILES([services/conf/Makefile])
AC_CONFIG_FILES([services/init.d/Makefile])
AC_CONFIG_FILES([services/src/Makefile])
AC_CONFIG_FILES([services/3rd_party/Makefile])
AC_CONFIG_FILES([web/Makefile])

dnl write all stuff
AC_OUTPUT

dnl Fetch 3rd-party sources
dnl Look for sources in /usr/src first
make -C services/3rd_party configure

dnl Warn user sysconfdir is not /etc, if necessary.
make sysconfdirwarning

echo "###"
echo "### End of pulse2 configuration"
echo "###"
