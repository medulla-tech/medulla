<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
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
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Profiles", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$groupname = htmlspecialchars($_GET["groupname"]);
$need_name = htmlspecialchars($_GET["needname"]);


$users_group_array = xmlrpc_get_clients();

$groupe_already_exist = htmlspecialchars($_GET["groupalreadyexist"]);

if ($need_name == "True")
{
    ?>
    <script>
        alert("Profile need name");
    </script>
    <?php
}

if ($groupe_already_exist == "True")
{
    ?>
    <script>
        alert("Profile already exist with this name");
    </script>
    <?php
}
?>

<br>
<br>
<form name="form" action="main.php?module=urbackup&amp;submod=urbackup&amp;action=create_group" method="post">
    <label><?php echo _T("Profile name :", 'urbackup'); ?></label><input type="text" name="groupname" id="groupname"/>
    <input type="submit" name="subcreate" id="subcreate" value="Create profile">
</form>

<br>
<br>

<?php
$group_array = $users_group_array['navitems']['groups'];
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
<?php
foreach ($group_array as $group) {
    if ($group['name'] != "") {
?>
        <tr>
            <td style='padding-left: 5px;'>
                <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_computers_onprofile&amp;groupid=<?php echo $group['id']; ?>&amp;groupname=<?php echo $group['name']; ?>"><?php echo $group['name']; ?></a>
            </td>
            <td>
            <ul class="action">
                <li class="display">
                    <a title=<?php echo _T("Browse", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=list_computers_onprofile&amp;groupid=<?php echo $group['id']; ?>&amp;groupname=<?php echo $group['name']; ?>">&nbsp;</a>
                </li>
                <li class="edit">
                    <a title=<?php echo _T("Edit", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=edit_profile_settings&amp;groupid=<?php echo $group['id']; ?>&amp;groupname=<?php echo $group['name']; ?>">&nbsp;</a>
                </li>
                <li class="delete">
                    <a title=<?php echo _T("Delete", 'urbackup'); ?> href="main.php?module=urbackup&amp;submod=urbackup&amp;action=deleting_group&amp;groupid=<?php echo $group['id']; ?>">&nbsp;</a>
                </li>
            </ul>
            </td>
        </tr>
<?php
    }
}
?>
    </tbody>
</table>
