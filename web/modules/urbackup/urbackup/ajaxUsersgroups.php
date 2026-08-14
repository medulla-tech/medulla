<?php
/*
 * (c) 2026 Medulla, http://medulla-tech.io
 *
 * $Id$
 *
 * This file is part of Pulse.
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
require_once("modules/urbackup/includes/xmlrpc.php");


$entity_id = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$group = xmlrpc_get_group_info($entity_id);


$groupid=(isset($group["id"])) ? $group["id"] : 0;
$groupname = isset($group["profile_name"]) ? htmlspecialchars($group["profile_name"]) : "";
$groupuuid=(isset($group["profile_uuid"])) ? htmlentities($group["profile_uuid"]) : "";
$groupapiid=(isset($group["api_id"])) ? htmlentities($group["api_id"]) : 0;
?>

<h1> <?php echo _T("Profile list :", 'urbackup'); ?> </h1>
<br>
<table class="listinfos" border="1px" cellspacing="0" cellpadding="5" >
    <thead>
        <tr>
            <th style='text-align: left;'> <?php echo _T("Name", 'urbackup'); ?> </th>
            <th style='text-align: right;'> <?php echo _T("Actions", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>

        <tr>
            <td style='padding-left: 5px;'>
                <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=edit_group_settings&amp;groupid=<?php echo $groupapiid; ?>&amp;groupname=<?php echo $groupname; ?>"><?php echo $groupname; ?></a>
            </td>
            <td>
            <ul class="action">
                <li class="edit">
                    <a title=<?php echo _T("Edit", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=edit_group_settings&amp;groupid=<?php echo $groupapiid; ?>&amp;groupname=<?php echo $groupname; ?>">&nbsp;</a>
                </li>
                <li class="delete">
                    <a title=<?php echo _T("Delete", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_group&amp;groupuuid=<?php echo $groupuuid;?>&amp;groupid=<?php echo $groupapiid; ?>">&nbsp;</a>
                </li>
            </ul>
            </td>
        </tr>
    </tbody>
</table>
