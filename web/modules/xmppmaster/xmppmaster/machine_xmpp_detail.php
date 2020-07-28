<?php
/*
 * (c) 2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 *
 * File xmppmaster/machine_xmpp_detail.php
 */
 // recupere information machine
 //print_r($_GET);
extract($_GET);
?>
<?php

//print_r($_GET);

$cn =   explode ( "/", $machine)[1];
$machinexmpp = xmlrpc_getMachinefromjid($machine);
  header('Location: main.php?module=base&submod=computers&action=glpitabs&cn='.urlencode($cn).'&objectUUID='.urlencode($machinexmpp['uuid_inventorymachine']));
  exit();

/*
echo "<pre>";
print_r($machinexmpp);
echo "</pre>";*/

?>
