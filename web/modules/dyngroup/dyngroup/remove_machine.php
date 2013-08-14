<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

require_once("modules/dyngroup/includes/includes.php");

$gid = quickGet('gid');
$group = new Group($gid, true);
$machine = quickGet('hostname');
$uuid = quickGet('objectUUID');

if (quickGet('valid')) {
    if (in_array("imaging", $_SESSION["modulesList"])) {
        include('modules/imaging/includes/xmlrpc.inc.php');
        if (xmlrpc_isProfileRegistered($gid)) {
            // Get Current Location
            $location = xmlrpc_getProfileLocation($gid);
        }
    }
    $group->delMember(array("$uuid" => array("uuid" => $uuid)));
    if (in_array("imaging", $_SESSION["modulesList"])) {
        if (xmlrpc_isProfileRegistered($gid)) {
            // Synchro Location
            xmlrpc_synchroLocation($location);
        }
    }
    header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$gid)));
    exit;
}

?> <h2><?php echo  _T("Remove a computer", "dyngroup") ?></h2> <?php

?>

<form action="<?php echo  urlStr("base/computers/remove_machine", array('gid'=>$gid, 'hostname'=>$machine, 'objectUUID'=>$uuid)) ?>" method="post">
<p>
<?php
    printf(_T("You will remove computer <b>%s</b> from group <b>%s</b>.", "dyngroup"), $machine, $group->getName());
?>
</p>
<input name='valid' type="submit" class="btnPrimary" value="<?php echo  _T("Remove Computer", "dyngroup"); ?>" />
<input name="bback" type="submit" class="btnSecondary" value="<?php echo  _T("Cancel", "dyngroup"); ?>" onClick="jQuery('#popup').fadeOut(); return false;"/>
</form>





