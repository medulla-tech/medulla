<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

$errItem = new ErrorHandlingItem("No such file or directory: '/var/log/ldap.log'");
$errItem->setMsg(_("LDAP log file does not exist."));
$errItem->setAdvice(_("Please be sure you have:
                        <p>This line in your /etc/ldap/slapd.conf or /etc/openldap/slapd.conf:
                        <pre>loglevel        256</pre></p>
                        <p>and this line in your /etc/syslog.conf:
                        <pre>local4.*       /var/log/ldap.log</pre>
                        </p>
                        "));
$errObj->add($errItem);

$errItem = new ErrorHandlingItem("No such file or directory: '/home/");
$errItem->setMsg(_("The user directory does not exist and cannot be removed."));
$errItem->setAdvice(_("Please do not remove user's files when deleting the user."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

$errItem = new ErrorHandlingItem("/home/.* already exists.");
$errItem->setMsg(_("The user home directory already exists."));
$errItem->setAdvice(_("Set the home directory in a different location (in expert mode) or delete the directory before creating the user."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

$errItem = new ErrorHandlingItem(": {'info': 'Password fails quality checking policy', 'desc': 'Constraint violation'}");
$errItem->setMsg(_("Password fails quality checking policy."));
$errItem->setAdvice(_("The password policy of your account doesn't allow you to modify your password, because your password doesn't met the passwords policies."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

$errItem = new ErrorHandlingItem(": {'info': 'Password is too young to change', 'desc': 'Constraint violation'}");
$errItem->setMsg(_("Your password is too young to change."));
$errItem->setAdvice(_("The password policy of your account doesn't allow you to modify your password, because your password is too young to change."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

$errItem = new ErrorHandlingItem(": {'info': 'Password is in history of old passwords', 'desc': 'Constraint violation'}");
$errItem->setMsg(_("Password is in history of old passwords"));
$errItem->setAdvice(_("The password policy of your account doesn't allow you to modify your password, because you already had this password previously."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

$errItem = new ErrorHandlingItem(": {'info': 'Password is not being changed from existing value', 'desc': 'Constraint violation'}");
$errItem->setMsg(_("Password is not being changed from existing value"));
$errItem->setAdvice(_("The password policy of your account doesn't allow you to modify your password, because you already had this password previously."));
$errItem->setTraceBackDisplay(False);
$errObj->add($errItem);

?>
