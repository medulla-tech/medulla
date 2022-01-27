<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse
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

$p = new PageGenerator(_T("Group creation", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$users_group_array = xmlrpc_get_clients();

$groupname = $_POST['groupname'];

$group_array = $users_group_array['navitems']['groups'];

$group_already_exist = "False";

$need_name = "False";

foreach ($group_array as $group) {
    if ($group['name'] == $groupname) {
        $group_already_exist = "True";
    }
}

if ($group_already_exist == "False") 
{
    if(strlen(trim($_POST['groupname']))<=0){
        $need_name = "True";
    }
    else
    {
        $create_group = xmlrpc_add_group($groupname);
    }
}

?>
<br>
<br>
<?php
$url = 'main.php?module=urbackup&submod=urbackup&action=usersgroups&groupname='.$groupname.'&needname='.$need_name.'&groupalreadyexist='.$group_already_exist;

header("Location: ".$url);
?>