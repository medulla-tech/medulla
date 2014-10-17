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
define([project], [pulse2])
AC_INIT(project, [2.1], [http://www.mandriva.com])

AC_CANONICAL_BUILD
AC_CANONICAL_HOST
AC_CANONICAL_TARGET

AM_INIT_AUTOMAKE([1.9 tar-ustar -Wno-portability])
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

dnl
dnl --enable-packager-mode
dnl   Packager mode: disable some features usually done by packagers
dnl   (eg: installing runlevel scripts)
dnl
AC_ARG_ENABLE([packager-mode],
              [AS_HELP_STRING([--enable-packager-mode],
                              [Disable features usually done in packaging @<:@default=disable@:>@])],
              [],
              [enable_packager_mode="no"])
AM_CONDITIONAL([ENABLE_PACKAGER_MODE], [test "$enable_packager_mode" = "yes"])

dnl
dnl --disable-python-check
dnl   Do not check python modules on configure
dnl
if test "x$enable_packager_mode" = "xno"; then
   AC_ARG_ENABLE([python-check],
                 [AS_HELP_STRING([--disable-python-check],
		                 [Do not check python modules on configure @<:@default=enable@:>@])],
				 [],
				 [enable_python_check="yes"])
else
   enable_python_check=no
fi
AM_CONDITIONAL([ENABLE_PYTHON_CHECK], [test "$enable_python_check" = "yes"])

dnl Check for Python modules
if test "x$enable_python_check" = "xyes"; then
   AX_PYTHON_MODULE([sqlalchemy], [1])
   AX_PYTHON_MODULE([MySQLdb], [1])
   AX_PYTHON_MODULE([twisted.web], [1])
   AX_PYTHON_MODULE([mmc], [1])
fi

dnl check for headers
AC_HEADER_STDC

dnl Add strictness options to the compiler
CFLAGS="$CFLAGS -Wall -Werror"
AC_SUBST(CFLAGS)
AC_SUBST(CPPFLAGS)
AC_SUBST(LDFLAGS)

dnl
dnl --disable-conf
dnl   Disable configuration files installation
dnl
AC_ARG_ENABLE([conf],
              [AS_HELP_STRING([--disable-conf],
                              [Disable configuration files installation @<:@default=enable@:>@])],
              [],
              [enable_conf="yes"])
AM_CONDITIONAL([ENABLE_CONF], [test "$enable_conf" = "yes"])

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
dnl --disable-wol
dnl   Fetch and compile wake-on-lan tool (3rd party)
dnl
if test "x$enable_packager_mode" = "xno"; then
    AC_ARG_ENABLE([wol],
                  [AS_HELP_STRING([--disable-wol],
                                  [Disable wake-on-lan tool (3rd party) @<:@default=enable@:>@])],
                  [],
                  [enable_wol="yes"])
else
    enable_wol=no
fi
AM_CONDITIONAL([ENABLE_WOL], [test "$enable_wol" = "yes"])

dnl
dnl --with-examples-dir
dnl   Set path to configuration files examples dir
dnl   Default to DOCDIR/examples
dnl
AC_ARG_WITH([examples-dir],
            [AS_HELP_STRING([--with-examples-dir],
                            [path to configuration files examples dir @<:@default=DOCDIR/examples@:>@])],
            [examplesdir="$withval"],
	    [examplesdir="${docdir}/examples"])
AC_SUBST([examplesdir])

dnl files to generate with automake
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([services/Makefile])
AC_CONFIG_FILES([services/bin/Makefile])
AC_CONFIG_FILES([services/mmc/Makefile])
AC_CONFIG_FILES([services/pulse2/Makefile])
AC_CONFIG_FILES([services/pulse2/version.py])
AC_CONFIG_FILES([services/contrib/Makefile])
AC_CONFIG_FILES([services/conf/Makefile])
AC_CONFIG_FILES([services/conf/plugins/Makefile])
AC_CONFIG_FILES([services/conf/pulse2/Makefile])
AC_CONFIG_FILES([services/init.d/Makefile])
AC_CONFIG_FILES([services/3rd_party/Makefile])
AC_CONFIG_FILES([services/clients/Makefile])
AC_CONFIG_FILES([services/clients/win32/Makefile])
AC_CONFIG_FILES([web/Makefile])
AC_CONFIG_FILES([web/modules/pulse2/version.php])
AC_CONFIG_FILES([doc/Makefile])
AC_CONFIG_FILES([doc/man/Makefile])
AC_CONFIG_FILES([doc/user/Makefile])

dnl write all stuff
AC_OUTPUT

dnl Fetch 3rd-party sources
make -C services/3rd_party configure
make -C doc DocumentConverter.py

dnl Warn user sysconfdir is not /etc, if necessary.
make confwarning

echo "###"
echo "### End of pulse2 configuration"
echo "###"
