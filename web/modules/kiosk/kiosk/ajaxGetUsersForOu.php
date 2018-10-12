<?php
/**
 * (c) 2018 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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

require_once("../includes/xmlrpc.php");
require_once("../includes/functions.php");
require_once("../../../includes/config.inc.php");
require_once("../../../includes/session.inc.php");
require_once("../../../includes/PageGenerator.php");
require_once("../../../includes/acl.inc.php");

$roots = $_POST['roots'];
$tmp = [];
foreach($roots as $root)
{
    $tmp = array_merge(xmlrpc_get_users_from_ou($root),$tmp);
}
$users = [];

foreach($tmp as $user)
{
    if(!in_array($user,$users))
        $users[] = $user;
}
unset($tmp);
unset($roots);

echo '<ul>';
foreach($users as $user)
{
    echo '<li>'.$user.'</li>';
}
echo '</ul>';

?>
