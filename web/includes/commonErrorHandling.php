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

$errObj = new ErrorHandlingControler();

$errItem = new ErrorHandlingItem('(ldap.ALREADY_EXISTS|Already exist)');
$errItem->setMsg(_("This item already exists in your LDAP directory"));
$errItem->setAdvice(_("Solve the problem by:
                        <ul>
                            <li>change this entry name</li>
                            <li>delete this entry before recreate it</li>
                        </ul>"));
$errItem->setTraceBackDisplay(false);
$errItem->setSize(300);
$errItem->setLevel(0);
$errObj->add($errItem);


$errItem = new ErrorHandlingItem('Can\'t contact LDAP server');
$errItem->setMsg(_("MMC Agent can't contact your LDAP server"));
$errItem->setAdvice(_("Solve the problem by:
                        <ul>
                            <li>Verify your LDAP server is correctly configured in /etc/mmc/plugins/base/ini </li>
                            <li>Verify you LDAP server is up</li>
                        </ul>"));

$errObj->add($errItem);

$errItem = new ErrorHandlingItem("AuthenticationError");
$errItem->setMsg(_("Error during authentication process"));
$errItem->setAdvice(_("Please contact your administrator."));
$errObj->add($errItem);

$errItem = new ErrorHandlingItem("ProvisioningError");
$errItem->setMsg(_("Error while provisioning your account"));
$errItem->setAdvice(_("Please contact your administrator."));
$errObj->add($errItem);


$errItem = new ErrorHandlingItem('(exceptions.IndexError: list index out of range|ldap.NO_SUCH_OBJECT)'); // FIXME : isn't the regex too wide ? 
$errItem->setMsg(_("This item do not seems to be in the index"));
$errItem->setAdvice(_("This problem can appear if:
                        <ul>
                            <li>This item no longer exists.</li>
                            <li>You misspelled it.</li>
                        </ul>"));
//$errItem->setTraceBackDisplay(false);
$errItem->setSize(800);
$errItem->setLevel(0);
$errObj->add($errItem);


$errItem = new ErrorHandlingItem('Failed to modify password entry');
$errItem->setMsg(_("smbpasswd failed to change your password entry"));
$errItem->setAdvice(_("Verify that your smbpasswd is correctly configured:
                        <ul>
                            <li> Your Ldap server can be down</li>
                            <li> Your Samba server is not properly configured</li>
                        </ul>"));

$errObj->add($errItem);

?>
