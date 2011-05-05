dnl configure.in for mmc-core project.
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
AC_INIT([mmc], [3.0.1], [http://www.mandriva.com])

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

dnl Check for GNU install (for file backup)
AC_MSG_CHECKING([for GNU install])
if $INSTALL --version | grep -q 'GNU coreutils'; then
   AC_MSG_RESULT([yes])
else
   AC_MSG_ERROR([Could not find GNU install])
fi

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
AX_PYTHON_MODULE([ldap], [1])
AX_PYTHON_MODULE([OpenSSL], [1])

dnl check for headers
AC_HEADER_STDC
# TODO: check for slap.h header

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
              [AS_HELP_STRING([--disable-conf-backup],
                              [Disable configuration files backup, if any @<:@default=enable@:>@])],
              [],
              [enable_conf_backup="yes"])
AM_CONDITIONAL([ENABLE_CONF_BACKUP], [test "$enable_conf_backup" = "yes"])

dnl
dnl --enable-check-password
dnl   Enable ldap mmc-check-password module.
dnl   WARNING: as of today, we don't know how to compile it
dnl
AC_ARG_ENABLE([check-password],
              [AS_HELP_STRING([--enable-check-password],
                              [Enable ldap mmc-check-password module @<:@default=disable@:>@])],
              [],
              [enable_check_password="no"])
AM_CONDITIONAL([ENABLE_CHECK_PASSWORD], [test "$enable_check_password" = "yes"])

dnl
dnl --with-ldap-confdir
dnl   Set path to ldap configuration directory
dnl   Default to SYSCONFDIR/ldap
dnl
AC_ARG_WITH([ldap-confdir],
            [AS_HELP_STRING([--with-ldap-confdir],
                            [path to ldap configuration direcory @<:@default=SYSCONFDIR/ldap@:>@])],
            [ldapconfdir="$withval"],
	    [ldapconfdir="${sysconfdir}/ldap"])
AC_SUBST([ldapconfdir])

dnl
dnl --with-ldap-libdir
dnl   Set path to ldap plugins directory
dnl   Default to LIBDIR/ldap
dnl
AC_ARG_WITH([ldap-libdir],
            [AS_HELP_STRING([--with-ldap-libdir],
                            [path to ldap plugins direcory @<:@default=LIBDIR/ldap@:>@])],
            [ldapconfdir="$withval"],
	    [ldapconfdir="${libdir}/ldap"])
AC_SUBST([ldaplibdir])

dnl files to generate with automake
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([agent/Makefile])
AC_CONFIG_FILES([agent/bin/Makefile])
AC_CONFIG_FILES([agent/backup-tools/Makefile])
AC_CONFIG_FILES([agent/init.d/Makefile])
AC_CONFIG_FILES([agent/conf/Makefile])
AC_CONFIG_FILES([agent/contrib/Makefile])
AC_CONFIG_FILES([agent/contrib/ldap/Makefile])
AC_CONFIG_FILES([agent/openldap-check-password/Makefile])
AC_CONFIG_FILES([web/Makefile])
AC_CONFIG_FILES([web/confs/Makefile])

dnl write all stuff
AC_OUTPUT

dnl Warn user sysconfdir is not /etc, if necessary.
make sysconfdirwarning
