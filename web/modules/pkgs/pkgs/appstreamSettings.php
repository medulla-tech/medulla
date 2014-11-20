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


require("graph/navbar.inc.php");
require("localSidebar.php");

require_once("modules/backuppc/includes/html.inc.php");

$p = new PageGenerator(_T("Appstream settings", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

print '<br/>';
print sprintf(_T('Please access the %s to manage your Appstream subscriptions.', 'pkgs'), '<a target="_blank" href="http://serviceplace.mandriva.com/">Mandriva ServicePlace</a>');
print '<br/>';
print '<br/>';

require_once("modules/pkgs/includes/xmlrpc.php");

// Activated package list

$json = getAppstreamJSON();
if (isset($_POST['bconfirm'])){
    $json['my_username'] = $_POST['my_username'];
    $json['my_password'] = $_POST['my_password'];
    if (setAppstreamJSON($json)){
        $available = getAvailableAppstreamPackages();
        if ($available['detail'] == 'Invalid username/password')
            new NotifyWidgetFailure(_T('Invalid My Credentials, please verify your username/password.', 'pkgs'));
        else
            new NotifyWidgetSuccess(_T('Your My credentials have been set successfuly.', 'pkgs'));
    }
    else{
        new NotifyWidgetFailure(_T('Cannot set My Credentials.', 'pkgs'));
    }
}

//  Check if credentials are active
$credentials_active=false;
if (setAppstreamJSON($json)){
    $available = getAvailableAppstreamPackages();
    if ($available['detail'] != 'Invalid username/password')
        $credential_active=true;
}
// =============================================================
// My Credentials form
// =============================================================

if ($credential_active) {
    print '<h2><br/>' . _T('Your Account credentials are active', 'pkgs') . '</h2>';
    $edit_credentialBtn = new buttonTpl('edit_account',_T('Modify Account credentials', 'pkgs'));
    $edit_credentialBtn->display();
    $show_credentials = "0";
    print '<br/>';
}
else {
    $show_credentials = "1";
    print '<h2><br/>' . _T('My Account credentials:', 'pkgs') . '</h2>';
}

print '<div id=\'credentials_form\'>';
$f = new ValidatingForm();
$f->push(new Table());

$f->add(
    new TrFormElement(_T('Username','pkgs'), new InputTpl('my_username')),
    array("value" => $json['my_username'],"required" => True)
);

$f->add(
    new TrFormElement(_T('Password','pkgs'), new PasswordTpl('my_password')),
    array("value" => $json['my_password'],"required" => True)
);
print "<input type = 'hidden' id = 'show_credentials' value = '$show_credentials'/>";
$f->addValidateButton("bconfirm");

$f->display();
print '</div>';

// =============================================================
// Package list
// =============================================================

if ($credential_active) {

// Activated package list
include("modules/pkgs/pkgs/ajaxAppstreamActivatedPackageList.php");

// Available package list
include("modules/pkgs/pkgs/ajaxAppstreamAvailablePackageList.php");

}
?>

<style>
    .noborder { border:0px solid blue; }
</style>

<script type="text/javascript">
    if (jQuery('#show_credentials').val() == "0")
    {
        jQuery('#credentials_form').css("display","none");
    }

    jQuery('#edit_account').click(function(){
        jQuery('#credentials_form').css("display","inline");
        jQuery('#edit_account').css("display","none");
    });
</script>
