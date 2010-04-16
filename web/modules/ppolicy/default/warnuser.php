<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 Included by MMC main.php to display a warning when the user logs in using
 grace login.
 */

require_once("modules/ppolicy/includes/ppolicy-xmlrpc.php");

if ($_SESSION["login"] != "root") {
    if ((empty($_SESSION["gracelogin"]))
        && (isAccountInGraceLogin($_SESSION["login"]) != -1)) {
        new NotifyWidgetSuccess(_T("Warning you have been logged using grace login mode. Please change your password as soon as possible using the password change page, else your account will be locked.", "ppolicy"));
    }
    $_SESSION["gracelogin"] = 1;
    if ((empty($_SESSION["userMustChangePassword"]))
        && (userMustChangePassword($_SESSION["login"]))) {
        new NotifyWidgetSuccess(_T("Warning your password has been reset by an administrator. Your LDAP account is restricted. Please change your password as soon as possible using the password change page.", "ppolicy"));
    }
    $_SESSION["userMustChangePassword"] = 1;
}

?>