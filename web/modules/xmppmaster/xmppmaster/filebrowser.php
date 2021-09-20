<?php
/*
 * (c) 2016-2020 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoringview.php
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");

?>
<style>
body {
	font-family: Arial, Helvetica, sans-serif;
}

table {
	font-size: 1em;
}

.ui-draggable, .ui-droppable {
	background-position: top;
}</style>
<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter= isset($_GET["filter"]) ? $_GET["filter"] : "";
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
$jid  = isset($_GET['jid']) ? $_GET['jid'] : ( isset($_POST['jid']) ? $_POST['jid'] : "");
$machine  = isset($_POST['Machine']) ? $_POST['Machine'] : ($uuid != '' ?  xmlrpc_getjidMachinefromuuid( $uuid ) : $jid);
$presence = xmlrpc_getPresenceuuid($uuid);
if($presence){
	$hostname = (isset($_GET['cn'])) ? htmlentities($_GET['cn']) : "";

	$p = new PageGenerator(_T("File viewer", 'xmppmaster')." $hostname");

	$p->setSideMenu($sidemenu);
	$p->display();

	$remote=52044;

	$result = xmlrpc_create_reverse_ssh_from_am_to_ars($machine, $remote);

	$relay = (isset($result)) ? explode('/', $result['jidARS'])[0] : explode('/', $machine)[0];
	$proxy = (isset($result)) ? $result['portproxy'] : 0;

	$relay = explode('@', $relay)[1];

	$host = $_SERVER['HTTP_HOST'];
	echo '<iframe id="fb_frame" src="" width="99%" style="height:700px;"></iframe>';
	?>

	<script>
	function sleep(ms) {
	  return new Promise(resolve => setTimeout(resolve, ms));
	}

	jQuery().ready(function(){
	  uri = window.location.protocol+"//<?php echo $host.'/mmc/fb/'.$relay.'/'.$proxy.'/';?>"
	  jQuery('#fb_frame').attr('src', uri);

	});
	</script>
<?php }
else{
	header('location: '.urlStrRedirect('base/computers/machinesList'));
}
?>
