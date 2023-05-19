<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2017 Siveo, http://http://www.siveo.net
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

/*
 * Delete post-imaging script popup)
 */

include('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once("modules/xmppmaster/includes/xmlrpc.php");
//$params = getParams();
$script_id = $_GET['itemid'];
$location = getCurrentLocation();
$label = urldecode($_GET['itemlabel']);

if ($_POST) {
    $script_id = $_POST['itemid'];
    // delete image
    $ret = xmlrpc_delPostInstallScript($script_id);

    // check result
    if ((is_array($ret) && $ret[0]) || $ret) {
        $str = sprintf(_T("<strong>%s</strong> script deleted", "imaging"), $script_name);
        xmlrpc_setfromxmppmasterlogxmpp(_T("Notify Success : script deleted", 'Imaging').' '."Script : "."( ".$script_name." ) "."on location : ".$location."[".$label."]",
                                                "IMG",
                                                '',
                                                0,
                                                $script_name ,
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Imaging | Postinstall | Menu | Start | Manual');
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/postinstall"));
        exit;
    } elseif (safeCount($ret) > 1) {
        xmlrpc_setfromxmppmasterlogxmpp(_T("Notify Error : script deleted", 'Imaging').' '."Script : "."( ".$script_name." ) "."on location : ".$location."[".$label."]",
                                                "IMG",
                                                '',
                                                0,
                                                $script_name ,
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Imaging | Postinstall | Menu | Start | Manual');
        new NotifyWidgetFailure($ret[1]);
    } else {
        $str = sprintf(_T("<strong>%s</strong> script wasn't deleted", "imaging"), $script_name);
        xmlrpc_setfromxmppmasterlogxmpp(_T("Notify Warning : script wasn't deleted", 'Imaging').' '."Script : "."( ".$script_name." ) "."on location : ".$location."[".$label."]",
                                                "IMG",
                                                '',
                                                0,
                                                $script_name ,
                                                'Manuel',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Imaging | Postinstall | Menu | Start | Manual');
        new NotifyWidgetFailure($str);
    }
} else {
    $script = xmlrpc_getPostInstallScript($script_id, $location);

    if (!$script['is_local']) {
        ?>
        <h2><?php echo _T("Can't delete this post-imaging script, it's a global script.", "imaging") ?></h2>
        <?php
    } else {
        ?>
        <h2><?php echo _T("Delete post-imaging script", "imaging") ?></h2>
        <form action="<?php echo urlStr("imaging/manage/postinstall_delete") ?>" method="post">
            <p><?php printf(_T("Are you sure you want to delete the <b>%s</b> script ?", "imaging"), $label); ?></p>
            <input name='itemid' type='hidden' value="<?php echo $script_id ?>" />
            <input name='valid' type="submit" class="btnPrimary" value="<?php echo _T("Delete", "imaging"); ?>" />
            <input name="bback" type="submit" class="btnSecondary" value="<?php echo _T("Cancel", "imaging"); ?>" onClick="closePopup();
                    return false;"/>
        </form>
        <?php
    }
}
?>
