<?php
/*
 * (c) 2017-2021 Siveo, http://http://www.siveo.net
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
 *
 * file xmppmaster/logs/ajaxviewgrpdeploy.php
 */

require("modules/xmppmaster/xmppmaster/localSidebarxmpp.php");
require_once("modules/dyngroup/includes/dyngroup.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
?>
<script src="jsframework/d3/d3.js"></script>
<style>
.log_err{
  color : red;
}

.log_warn{
  color : orange;
}

.log_ok{
  color : green;
}
.status, .machine-inventory{
    cursor: pointer;
}

progress{
    border-color: #ffffff;
    background-color: #009ea9;
}
progress.mscdeloy{
    width: 390px;
    background-color: #00f3f3;
}

progress::-webkit-progress-bar {
    background: #00f3f3 ;
}

progress::-webkit-progress-value {
    background: #009ea9;
}
progress::-moz-progress-bar {
  background-color:blue;
}


.bars{
    width: 400px;
    float:left;
}
.bars1{
    width:650px;
    float:left;
}

#holder ul li a{
    font-weight : normal;
}

.deployment td{
  vertical-align: top;
}
</style>

<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
extract($_GET);

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$criterion = isset($_GET['criterion']) ? $_GET['criterion'] : "";
$filter = ["filter" => $filter, "criterion" => $criterion];
$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['end'] + $maxperpage : $maxperpage);

function urlredirect_group_for_deploy($typegroup, $g_id, $login_deploy, $cmddeploy_id)
{
    $urlRedirect1 = urlStrRedirect("base/computers/createMachinesStaticGroupdeploy&gid=".$g_id."&login=".$login_deploy."&cmd_id=".$cmddeploy_id."&type=".$typegroup);
    return $urlRedirect1;
}

function datecmd($tabbleaudatetime)
{
    return date(
        "Y-m-d H:i:s",
        mktime(
            $tabbleaudatetime[3],
            $tabbleaudatetime[4],
            $tabbleaudatetime[5],
            $tabbleaudatetime[1],
            $tabbleaudatetime[2],
            $tabbleaudatetime[0]
        )
    );
}

function installrefresh()
{
    echo '<script type="text/javascript">
    setTimeout(function(){document.location.reload(); }, 20000);
</script>';
}

//FROM MSC BASE
// The deployment is a convergence
$isconvergence = is_commands_convergence_type($cmd_id);


// Get syncthing stats for this deployment
$statsyncthing  = xmlrpc_stat_syncthing_transfert($_GET['gid'], $_GET['cmd_id']);

// get contrainte group
$tab = xmlrpc_get_conrainte_slot_deployment_commands([$cmd_id]);
$contrainte  = safeCount($tab) ? $tab[$cmd_id] : "";

// search from msc table CommandsOnHost
$lastcommandid = get_last_commands_on_cmd_id_start_end($cmd_id, $filter, $start, $end);



$infocmd = command_detail($cmd_id);

$title = (!empty($_GET['title'])) ? htmlentities($_GET['title']) : $infocmd['title'];
$creator_user = $infocmd['creator'] ;
$creation_date = datecmd($infocmd['creation_date']);
$end_date =  datecmd($infocmd['end_date']);
$start_date = datecmd($infocmd['start_date']);

$group = getPGobject($gid, true);
$p = new PageGenerator(_T("Deployment [ group", 'xmppmaster')." ". $group->getName()."]");
$p->display();

if($isconvergence != 0) {
    echo "<h2>";
    echo $title;
    echo "</h2>";
}


// Get uuid, hostname and status of the deployed machines from xmppmaster.deploy
$getdeployment = xmlrpc_getdeployment_cmd_and_title(
    $cmd_id,
    $title,
    $filter,
    $start,
    $maxperpage
);
$status = array_combine($getdeployment["datas"]["uuid"], $getdeployment["datas"]["status"]);

// Get the same machines from glpi
$re = xmlrpc_get_machine_for_id(
    $getdeployment['datas']['id'],
    $filter,
    $start,
    $maxperpage
);

if($getdeployment['total'] != 0) {
    $count = $getdeployment['total'];
} else {
    $count = $re['total'];
}

// STATS FROM XMPPMASTER DEPLOY
$statsfromdeploy = xmlrpc_getstatdeploy_from_command_id_and_title($cmd_id, $title);
// get some info from msc for this deployment
$info = xmlrpc_getdeployfromcommandid($cmd_id, "UUID_NONE");


if ($count == 0) {
    // Refresh if no deployment is started.
    installrefresh();
}
$timestampnow = time();
$info_from_machines = $re["listelet"];
$statuslist = xmlrpc_get_log_status();

$dynamicstatus = [];

foreach($statuslist as $element) {
    $dynamicstatus[$element['label']] = $element['status'];
}

extract($statsfromdeploy);
$done = 0;
$aborted = 0;
$inprogress = 0;
$terminate = false;
$errors = 0;

//Calculate globals stats
foreach($statsfromdeploy as $key => $value) {
    if($key != 'totalmachinedeploy') {
        if(preg_match('#abort|success|error|status#i', $key)) {
            $done += $value;
            $terminate = ($done >= $totalmachinedeploy) ? true : false;
        } else {
            $inprogress += $value;
        }

        if(preg_match('#^abort#i', $key)) {
            $aborted += $value;
        }
        if(preg_match('#^error#i', $key)) {
            $errors += $value;
        }
    }
}
if($totalmachinedeploy) {
    $evolution  = round(($done / $totalmachinedeploy) * 100, 2);
    $evolution = ($evolution > 100) ? 100 : $evolution;
} else {
    $evolution = 0;
}

/* Deployment status
    Deployment terminated : $done == $total => $terminate = true
    Deployment still running : $inprogress > 0
    Deployment started at current time : $start_deploy = true
    Deployment finish at current time : $end_deploy = true
    Deployment evolution (%) : ($done / $total) * 100
*/
$start_deploy = false;
$end_deploy   = false;

if ($timestampnow > strtotime($start_date)) {
    $start_deploy = true;
}


if (gettype($end_date) == "integer" && $timestampnow > $end_date) {
    $end_deploy = true;
} elseif (gettype($end_date) == "string" && $timestampnow > strtotime($end_date)) {
    $end_deploy = true;
}

// This command gets associated group of cmd_id
$syncthing_enabled = ($statsyncthing['package'] == "") ? false : true;

echo "<table class='listinfos' cellspacing='0' cellpadding='5' border='1'>";
echo "<thead>";
echo "<tr>";
echo '<td>'._T("Creation Date", "xmppmaster").'</td>';
echo '<td>'._T("Start Date", "xmppmaster").'</td>';
if ($contrainte != "") {
    echo '<td>'._T("contraint slot", "xmppmaster").'</td>';
}
echo '<td>'._T("End Date", "xmppmaster").'</td>';
echo '<td>'._T("Creator", "xmppmaster").'</td>';
if($isconvergence != 0) {
    echo '<td>'._T("Convergence", "xmppmaster").'</td>';
}
echo '<td>'._T("Syncthing enabled", "xmppmaster").'</td>';
echo '<td>'._T("Progress", "xmppmaster").'</td>';
echo "</tr>";
echo "</thead>";
echo "<tbody>";
echo "<tr>";
echo '<td>'.$creation_date.'</td>';
echo '<td>'. $start_date.'</td>';
if ($contrainte != "") {
    echo '<td>'.$contrainte.'</td>';
}
echo '<td>'.$end_date.'</td>';
echo '<td>'.$creator_user.'</td>';
if($isconvergence != 0) {
    echo "<td><img style='position:relative;top : 5px;' src='img/other/convergence.svg' width='25' height='25'/></td>";
}


echo ($syncthing_enabled) ? '<td>'._T("Yes", "xmppmaster").'</td>' : '<td>'._T("No", "xmppmaster").'</td>';
echo '<td>';
echo '<div class="bars">';
echo'<span style="margin-left:10px">Deployment '.$evolution.'%</span>';
echo '<span style="width: 200px;">';
echo'<progress class="mscdeloy" data-label="50% Complete" max="'.$totalmachinedeploy.'" value="'.$done .'" form="form-id"></progress>';
echo '</span>';
echo '</td>';
echo "</tr>";
echo "</tbody>";
echo '</table>';

if ($statsyncthing['package'] != "") {
    echo '<h2>'._T("Syncthing Detail", "xmppmaster").'</h2>';
    //NEW
    echo "<table class='listinfos' cellspacing='0' cellpadding='5' border='1'>";
    echo "<thead>";
    echo '<tr>';
    echo '<td>'. _T("Share name", "xmppmaster"). '</td>';
    echo '<td>'. _T("Number of participants", "xmppmaster"). '</td>';
    echo '<td>'. _T("Transfer progress", "xmppmaster"). '</td>';
    echo '<td>'. _T("Detail", "xmppmaster").'</td>';
    echo '</tr>';
    echo '</thead>';


    echo '<tbody>';
    echo '<tr>';
    echo '<td>'.$statsyncthing['package'].'</td>';
    echo '<td>'.$statsyncthing['nbmachine'].'</td>';
    echo '<td>'.$statsyncthing['progresstransfert'].' %</td>';
    echo '<td><input id="buttontogglesyncthing" class="btn btn-primary" type="button" value="'._T('Show Transfer', 'xmppmaster').'"> <input id="buttonrefreshsyncthing" class="btn btn-primary" type="button" value="'._T('refresh View', 'xmppmaster').'"></td>';
    echo '</tr>';

    foreach ($statsyncthing['distibution']['data_dist'] as $arrayval) {
        echo "<tr>";
        echo '<td></td>';
        echo '<td>'.$arrayval[1].'</td>';
        echo '<td>'.$arrayval[0].'%</td>';
        echo '<td></td>';
        echo "</tr>";
    }
    echo '</tbody>';
    echo '</table>';


    //OLD
    echo "<div style='width :100%;'>";
    echo "<div>";
    echo "<div id='tablesyncthing'>";
    ?>
    <table id="tablelog" width="100%" border="1" cellspacing="0" cellpadding="1" class="listinfos">
            <thead>
                <tr>
                    <th style="width: 12%;"><?php echo _('cluster list'); ?></th>
                    <th style="width: 7%;"><?php echo _('cluster nb ars'); ?></th>
                    <th style="width: 7%;"><?php echo _('machine'); ?></th>
                    <th style="width: 7%;"><?php echo _('progress'); ?></th>
                    <th style="width: 7%;"><?php echo _('start'); ?></th>
                    <th style="width: 7%;"><?php echo _('end'); ?></th>
                </tr>
            </thead>
        </table>
<?php
        echo "</div>";
    echo "</div>";
    echo '</div>';
}//End syncthing
?>

<script type="text/javascript">
function searchlogs(url){
  jQuery('#tablelog').DataTable({
    'retrieve': true,
    "iDisplayLength": 5,
    "dom": 'rt<"bottom"fp><"clear">',
    'order': [[ 0, "desc" ]]
  })
  .ajax.url(url)
  .load();
}

jQuery(function(){
    searchlogs("modules/xmppmaster/xmppmaster/ajaxsyncthingmachineless.php?grp=<?php echo $_GET['gid']; ?>&cmd=<?php echo $cmd_id ?>")
} );

jQuery( "#tablesyncthing" ).hide();

jQuery( "#buttonrefreshsyncthing" ).click(function() {
    document.location.reload();
});

jQuery( "#buttontogglesyncthing" ).click(function() {
    jQuery( "#tablesyncthing" ).toggle();

    if(jQuery('#tablesyncthing').is(':visible')){
      jQuery( "#buttontogglesyncthing" ).val("Hide Transfer");
    }
    else{
      jQuery( "#buttontogglesyncthing" ).val("Show Transfer");
    }
});
</script>

<?php


$_GET['id'] = isset($_GET['id']) ? $_GET['id'] : "";
$_GET['ses'] = isset($_GET['ses']) ? $_GET['ses'] : "";
$_GET['hos'] = isset($_GET['hos']) ? $_GET['hos'] : "";
$_GET['sta'] = isset($_GET['sta']) ? $_GET['sta'] : "";

//start deployement status
echo "<div>";
if ($start_deploy) {

    if ($end_deploy || $terminate) {
        echo "<h2>"._T("Deployment complete", "xmppmaster")."</h2>";
        $terminate = true;
    } else {
        echo "<h2>"._T("Deployment in progress", "xmppmaster")."</h2>";
        echo _T("Started since", "xmppmaster")." <span>".($timestampnow - strtotime($start_date))."</span> s";
        $terminate = false;
    }
} else {
    echo _T("WAITING FOR START ", "xmppmaster").date("Y-m-d H:i:s", strtotime($start_date));
}


if(!$terminate) {
    $f = new ValidatingForm();
    $f->add(new HiddenTpl("id"), array("value" => $_GET['cmd_id'], "hide" => true));
    $f->addButton("bStop", _T("Abort Deployment", 'xmppmaster'));
    $f->display();
}

if(!$terminate) {
    echo "<table class='listinfos deployment' cellspacing='0' cellpadding='5' border='1'><thead><tr>";
    echo '<td>'._T('Graph', 'xmppmaster').'</td>';
    echo (isset($deploymentsuccess) && $deploymentsuccess) ? "<td>"._T("Deployment Success", "xmppmaster")."</td>" : "";
    echo (isset($deploymenterror) && $deploymenterror) ? "<td>"._T("Deployment Error", "xmppmaster")."</td>" : "";
    echo (isset($abortmissingagent) && $abortmissingagent) ? "<td>"._T("Abort Missing Agent", "xmppmaster")."</td>" : "";
    echo (isset($abortinconsistentglpiinformation) && $abortinconsistentglpiinformation) ? "<td>"._T("Abort inconsistent GLPI Information", "xmppmaster")."</td>" : "";
    echo (isset($abortrelaydown) && $abortrelaydown) ? "<td>"._T("Abort Relay Down", "xmppmaster")."</td>" : "";
    echo (isset($abortalternativerelaysdow) && $abortalternativerelaysdown) ? "<td>"._T("Abort Alternative relay down", "xmppmaster")."</td>" : "";
    echo (isset($abortinforelaymissing) && $abortinforelaymissing) ? "<td>"._T("Abort Info Relay Missing", "xmppmaster")."</td>" : "";
    echo (isset($errorunknownerror) && $errorunknownerror) ? "<td>"._T("Error Unknown Error", "xmppmaster")."</td>" : "";
    echo (isset($abortpackageidentifiermissing) && $abortpackageidentifiermissing) ? "<td>"._T("Abort Package Identifier Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortpackagenamemissing) && $abortpackagenamemissing) ? "<td>"._T("Abort Package Name Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortpackageversionmissing) && $abortpackageversionmissing) ? "<td>"._T("Abort Package Version Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortdescriptormissing) && $abortdescriptormissing) ? "<td>"._T("Abort Descriptor Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortmachinedisappeared) && $abortmachinedisappeared) ? "<td>"._T("Abort Machine Disappeared", "xmppmaster")."</td>" : "";
    echo (isset($abortdeploymentcancelledbyuser) && $abortdeploymentcancelledbyuser) ? "<td>"._T("Abort Deployment Cancelled By User", "xmppmaster")."</td>" : "";
    echo (isset($abortduplicatemachines) && $abortduplicatemachines) ? "<td>"._T("Abort Duplicate Machines", "xmppmaster")."</td>" : "";
    echo (isset($deploymentdelayed) && $deploymentdelayed) ? "<td>"._T("Deployment Delayed", "xmppmaster")."</td>" : "";
    echo (isset($deploymentstart) && $deploymentstart) ? "<td>"._T("Deployment start", "xmppmaster")."</td>" : "";
    echo (isset($deploymentpending) && $deploymentpending) ? "<td>"._T("Deployment Pending", "xmppmaster")."</td>" : "";
    echo (isset($wol1) && $wol1) ? "<td>"._T("WOL 1", "xmppmaster")."</td>" : "";
    echo (isset($wol2) && $wol2) ? "<td>"._T("WOL 2", "xmppmaster")."</td>" : "";
    echo (isset($wol3) && $wol3) ? "<td>"._T("WOL 3", "xmppmaster")."</td>" : "";
    echo (isset($waitingmachineonline) && $waitingmachineonline) ? "<td>"._T("Waiting Machine Online", "xmppmaster")."</td>" : "";
    echo (isset($errorhashmissing) && $errorhashmissing) ? "<td>"._T("Error Hash Missing", "xmppmaster")."</td>" : "";
    echo (isset($aborthashinvalid) && $aborthashinvalid) ? "<td>"._T("Abort Hash Invalid", "xmppmaster")."</td>" : "";
    echo (isset($otherstatus) && $otherstatus) ? "<td>"._T("Other Status", "xmppmaster")."</td>" : "";
    foreach($dynamicstatus as $label => $_status) {
        echo (isset($$label) && $$label) ? "<td>".ucfirst(strtolower(_T($_status, "xmppmaster")))."</td>" : "";
    }
    echo "</tr></thead>";

    echo "<tbody><tr>";
    echo '<td style="width:500px"><div id="holder"></div>';
    echo (isset($deploymentsuccess) && $deploymentsuccess) ? "<td>".$deploymentsuccess."</td>" : "";
    echo (isset($deploymenterror) && $deploymenterror) ? "<td>".$deploymenterror."</td>" : "";
    echo (isset($abortmissingagent) && $abortmissingagent) ? "<td>".$abortmissingagent."</td>" : "";
    echo (isset($abortinconsistentglpiinformation) && $abortinconsistentglpiinformation) ? "<td>".$abortinconsistentglpiinformation."</td>" : "";
    echo (isset($abortrelaydown) && $abortrelaydown) ? "<td>".$abortrelaydown."</td>" : "";
    echo (isset($abortalternativerelaysdow) && $abortalternativerelaysdown) ? "<td>".$abortalternativerelaysdown."</td>" : "";
    echo (isset($abortinforelaymissing) && $abortinforelaymissing) ? "<td>".$abortinforelaymissing."</td>" : "";
    echo (isset($errorunknownerror) && $errorunknownerror) ? "<td>".$errorunknownerror."</td>" : "";
    echo(isset($abortpackageidentifiermissing) && $abortpackageidentifiermissing) > 0 ? "<td>".$abortpackageidentifiermissing."</td>" : "";
    echo (isset($abortpackagenamemissing) && $abortpackagenamemissing) ? "<td>".$abortpackagenamemissing."</td>" : "";
    echo (isset($abortpackageversionmissing) && $abortpackageversionmissing) ? "<td>".$abortpackageversionmissing."</td>" : "";
    echo (isset($abortdescriptormissing) && $abortdescriptormissing) ? "<td>".$abortdescriptormissing."</td>" : "";
    echo (isset($abortmachinedisappeared) && $abortmachinedisappeared) ? "<td>".$abortmachinedisappeared."</td>" : "";
    echo (isset($abortdeploymentcancelledbyuser) && $abortdeploymentcancelledbyuser) ? "<td>".$abortdeploymentcancelledbyuser."</td>" : "";
    echo (isset($abortduplicatemachines) && $abortduplicatemachines) ? "<td>".$abortduplicatemachines."</td>" : "";
    echo (isset($deploymentdelayed) && $deploymentdelayed) ? "<td>".$deploymentdelayed."</td>" : "";
    echo (isset($deploymentstart) && $deploymentstart) ? "<td>".$deploymentstart."</td>" : "";
    echo (isset($deploymentpending) && $deploymentpending) ? "<td>".$deploymentpending."</td>" : "";
    echo (isset($wol1) && $wol1) ? "<td>".$wol1."</td>" : "";
    echo (isset($wol2) && $wol2) ? "<td>".$wol2."</td>" : "";
    echo (isset($wol3) && $wol3) ? "<td>".$wol3."</td>" : "";
    echo(isset($waitingmachineonline) && $waitingmachineonline) > 0 ? "<td>".$waitingmachineonline."</td>" : "";
    echo (isset($errorhashmissing) && $errorhashmissing) ? "<td>".$errorhashmissing."</td>" : "";
    echo (isset($aborthashinvalid) && $aborthashinvalid) ? "<td>".$aborthashinvalid."</td>" : "";
    echo (isset($otherstatus) && $otherstatus) ? "<td>".$otherstatus."</td>" : "";
    foreach($dynamicstatus as $label => $_status) {
        echo (isset($$label) && $$label) ? "<td>".$$label."</td>" : "";
    }
    echo "</tr>";
    echo "</tbody></table>";
} else {
    echo "<table class='listinfos deployment' cellspacing='0' cellpadding='5' border='1'><thead><tr>";
    echo '<td>'._T('Summary Graph', 'xmppmaster').'</td>';
    echo "<td>"._T("Success", "xmppmaster")."</td>
              <td>"._T("Error", "xmppmaster")."</td>
              <td>"._T("Aborted", "xmppmaster")."</td>";
    echo "</tr></thead>
          <tbody><tr>";
    echo '<td style="width:500px"><div id="holder"></div>';
    echo '</td>';
    echo "<td>".$deploymentsuccess."</td>
              <td>".$errors."</td>
              <td>".$aborted."</td>";
    echo "</tr>";
    echo "</tbody></table>";

    echo "<table class='listinfos deployment' cellspacing='0' cellpadding='5' border='1'><thead><tr>";
    echo '<td>'._T('Detailed Graph', 'xmppmaster').'</td>';
    echo (isset($deploymentsuccess) && $deploymentsuccess) ? "<td>"._T("Deployment Success", "xmppmaster")."</td>" : "";
    echo (isset($deploymenterror) && $deploymenterror) ? "<td>"._T("Deployment Error", "xmppmaster")."</td>" : "";
    echo (isset($abortmissingagent) && $abortmissingagent) ? "<td>"._T("Abort Missing Agent", "xmppmaster")."</td>" : "";
    echo (isset($abortinconsistentglpiinformation) && $abortinconsistentglpiinformation) ? "<td>"._T("Abort Inconsistent GLPI Information", "xmppmaster")."</td>" : "";
    echo (isset($abortrelaydown) && $abortrelaydown) ? "<td>"._T("Abort Relay Down", "xmppmaster")."</td>" : "";
    echo (isset($abortalternativerelaysdow) && $abortalternativerelaysdown) ? "<td>"._T("Abort Alternative relay down", "xmppmaster")."</td>" : "";
    echo (isset($abortinforelaymissing) && $abortinforelaymissing) ? "<td>"._T("Abort Info Relay Missing", "xmppmaster")."</td>" : "";
    echo (isset($errorunknownerror) && $errorunknownerror) ? "<td>"._T("Error Unknown Error", "xmppmaster")."</td>" : "";
    echo (isset($abortpackageidentifiermissing) && $abortpackageidentifiermissing) ? "<td>"._T("Abort Package Identifier Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortpackagenamemissing) && $abortpackagenamemissing) ? "<td>"._T("Abort Package Name Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortpackageversionmissing) && $abortpackageversionmissing) ? "<td>"._T("Abort Package Version Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortdescriptormissing) && $abortdescriptormissing) ? "<td>"._T("Abort Descriptor Missing", "xmppmaster")."</td>" : "";
    echo (isset($abortmachinedisappeared) && $abortmachinedisappeared) ? "<td>"._T("Abort Machine Disappeared", "xmppmaster")."</td>" : "";
    echo (isset($abortdeploymentcancelledbyuser) && $abortdeploymentcancelledbyuser) ? "<td>"._T("Abort Deployment Cancelled By User", "xmppmaster")."</td>" : "";
    echo (isset($abortduplicatemachines) && $abortduplicatemachines) ? "<td>"._T("Abort Duplicate Machines", "xmppmaster")."</td>" : "";
    echo (isset($deploymentdelayed) && $deploymentdelayed) ? "<td>"._T("Deployment Delayed", "xmppmaster")."</td>" : "";
    echo (isset($deploymentstart) && $deploymentstart) ? "<td>"._T("Deployment start", "xmppmaster")."</td>" : "";
    echo (isset($deploymentpending) && $deploymentpending) ? "<td>"._T("Deployment Pending", "xmppmaster")."</td>" : "";
    echo (isset($wol1) && $wol1) ? "<td>"._T("WOL 1", "xmppmaster")."</td>" : "";
    echo (isset($wol2) && $wol2) ? "<td>"._T("WOL 2", "xmppmaster")."</td>" : "";
    echo (isset($wol3) && $wol3) ? "<td>"._T("WOL 3", "xmppmaster")."</td>" : "";
    echo (isset($waitingmachineonline) && $waitingmachineonline) ? "<td>"._T("Waiting Machine Online", "xmppmaster")."</td>" : "";
    echo (isset($errorhashmissing) && $errorhashmissing) ? "<td>"._T("Error Hash Missing", "xmppmaster")."</td>" : "";
    echo (isset($aborthashinvalid) && $aborthashinvalid) ? "<td>"._T("Abort Hash Invalid", "xmppmaster")."</td>" : "";
    echo (isset($otherstatus) && $otherstatus) ? "<td>"._T("Other Status", "xmppmaster")."</td>" : "";
    foreach($dynamicstatus as $label => $_status) {
        echo (isset($$label) && $$label) ? "<td>".ucfirst(strtolower(_T($_status, "xmppmaster")))."</td>" : "";
    }
    echo "</tr></thead>";

    echo "<tbody><tr>";
    echo '<td style="width:500px"><div id="holder2"></div>';
    echo (isset($deploymentsuccess) && $deploymentsuccess) ? "<td>".$deploymentsuccess."</td>" : "";
    echo (isset($deploymenterror) && $deploymenterror) ? "<td>".$deploymenterror."</td>" : "";
    echo (isset($abortmissingagent) && $abortmissingagent) ? "<td>".$abortmissingagent."</td>" : "";
    echo (isset($abortinconsistentglpiinformation) && $abortinconsistentglpiinformation) ? "<td>".$abortinconsistentglpiinformation."</td>" : "";
    echo (isset($abortrelaydown) && $abortrelaydown) ? "<td>".$abortrelaydown."</td>" : "";
    echo (isset($abortalternativerelaysdow) && $abortalternativerelaysdown) ? "<td>".$abortalternativerelaysdown."</td>" : "";
    echo (isset($abortinforelaymissing) && $abortinforelaymissing) ? "<td>".$abortinforelaymissing."</td>" : "";
    echo (isset($errorunknownerror) && $errorunknownerror) ? "<td>".$errorunknownerror."</td>" : "";
    echo(isset($abortpackageidentifiermissing) && $abortpackageidentifiermissing) > 0 ? "<td>".$abortpackageidentifiermissing."</td>" : "";
    echo (isset($abortpackagenamemissing) && $abortpackagenamemissing) ? "<td>".$abortpackagenamemissing."</td>" : "";
    echo (isset($abortpackageversionmissing) && $abortpackageversionmissing) ? "<td>".$abortpackageversionmissing."</td>" : "";
    echo (isset($abortdescriptormissing) && $abortdescriptormissing) ? "<td>".$abortdescriptormissing."</td>" : "";
    echo (isset($abortmachinedisappeared) && $abortmachinedisappeared) ? "<td>".$abortmachinedisappeared."</td>" : "";
    echo (isset($abortdeploymentcancelledbyuser) && $abortdeploymentcancelledbyuser) ? "<td>".$abortdeploymentcancelledbyuser."</td>" : "";
    echo (isset($abortduplicatemachines) && $abortduplicatemachines) ? "<td>".$abortduplicatemachines."</td>" : "";
    echo (isset($deploymentdelayed) && $deploymentdelayed) ? "<td>".$deploymentdelayed."</td>" : "";
    echo (isset($deploymentstart) && $deploymentstart) ? "<td>".$deploymentstart."</td>" : "";
    echo (isset($deploymentpending) && $deploymentpending) ? "<td>".$deploymentpending."</td>" : "";
    echo (isset($wol1) && $wol1) ? "<td>".$wol1."</td>" : "";
    echo (isset($wol2) && $wol2) ? "<td>".$wol2."</td>" : "";
    echo (isset($wol3) && $wol3) ? "<td>".$wol3."</td>" : "";
    echo(isset($waitingmachineonline) && $waitingmachineonline) > 0 ? "<td>".$waitingmachineonline."</td>" : "";
    echo (isset($errorhashmissing) && $errorhashmissing) ? "<td>".$errorhashmissing."</td>" : "";
    echo (isset($aborthashinvalid) && $aborthashinvalid) ? "<td>".$aborthashinvalid."</td>" : "";
    echo (isset($otherstatus) && $otherstatus) ? "<td>".$otherstatus."</td>" : "";
    foreach($dynamicstatus as $label => $_status) {
        echo (isset($$label) && $$label) ? "<td>".$$label."</td>" : "";
    }
    echo "</tr></thead></table>";
}

echo '</div>';

echo '<h2>'._T("Package Detail", "xmppmaster").'</h2>';

$package_id = (isset($lastcommandid['package_id'])) ? $lastcommandid['package_id'] : "";
$package = get_package_summary($package_id);

if($package['name'] == "") {
    $package['name'] = _T("Package deleted", "pkgs");
    $package['Qsoftware'] = "";
    $package['Qversion'] = "";
    $package['Qvendor'] = "";
    $package['version'] = _T("Package deleted", "pkgs");
    $package['description'] = _T("Package deleted", "pkgs");
    $package['files'] = [];
    $package['Size'] = 0;
}
$associatedInventory = [];
if ($package['Qsoftware'] != "") {
    $associatedInventory[] = $package['Qsoftware'];
}
if($package['Qversion'] != "") {
    $associatedInventory[] = $package['Qversion'];
}
if($package['Qvendor'] != "") {
    $associatedInventory[] = $package['Qvendor'];
}

$files = "";

foreach($package['files'] as $file) {
    $files .= $file.'
';
}

echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
echo "<thead>";
echo "<tr>";
echo '<td style="width: ;">';
echo '<span style=" padding-left: 32px;">'._T('Name', 'xmppmaster').'</span>';
echo '</td>';
echo '<td style="width: ;">';
echo '<span style=" padding-left: 32px;">'._T('Associated Inventory', 'xmppmaster').'</span>';
echo '</td>';
echo '<td style="width: ;">';
echo '<span style=" padding-left: 32px;">'._T('Version', 'xmppmaster').'</span>';
echo '</td>';
echo '<td style="width: ;">';
echo '<span style=" padding-left: 32px;">'._T('Description', 'xmppmaster').'</span>';
echo '</td>';
echo '<td style="width: ;">';
echo '<span style=" padding-left: 32px;">'._T('Size', 'xmppmaster').'</span>';
echo '</td>';
echo "</tr>";
echo "</thead>";
echo "<tbody>";
echo "<tr>";
echo "<td>";
echo '<span title="'.$files.'">'.$package['name'].'</span>';
echo "</td>";
echo "<td>";
echo join(' / ', $associatedInventory);
echo "</td>";
echo "<td>";
echo $package['version'];
echo "</td>";
echo "<td>";
echo $package['description'];
echo "</td>";
echo "<td>";
echo $package['Size'];
echo "</td>";
echo "</tr>";
echo "</tbody>";
echo "</table>";

if ($count != 0) {
    $params = [];

    $info_from_machines[] = []; // Add 7th index
    $info_from_machines[] = []; // Add 8th index
    $info_from_machines[] = []; // Add 9th index

    foreach($info_from_machines[0] as $key => $value) {
        $infomachine = xmlrpc_getdeployfromcommandid($cmd_id, 'UUID'.$value);
        $sessionid = $infomachine['objectdeploy'][0]['sessionid'];

        if(isset($status['UUID'.$value])) {
            $info_from_machines[7][] = '<span class="status">'.$status['UUID'.$value].'</span>';
        }
        $info_from_machines[8][] = 'UUID'.$value;
        $params[] = [
          'displayName' => $info_from_machines[2][$key],
          'cn' => $info_from_machines[1][$key],
          'type' => $info_from_machines[4][$key],
          'objectUUID' => 'UUID'.$value,
          'entity' => $info_from_machines[6][$key],
          'owner' => $info_from_machines[5][$key],
          'user' => $_GET['login'],
          'os' => $info_from_machines[3][$key],
          'status' => isset($info_from_machines[7][$key]) ? $info_from_machines[7][$key] : '<span style="color:red">'._T('OFFLINE', 'xmppmaster').'</span>',
          'gid' => $_GET['gid'],
          'gr_cmd_id' => $_GET['cmd_id'],
          'gr_login' => $_GET['login'],
          'sessionid' => $sessionid,
          'title' => $_GET['title'],
          'start' => $creation_date,
          'startcmd' => $start_date,
          'endcmd' => $end_date
        ];

    }
    $presencemachinexmpplist = xmlrpc_getPresenceuuids($info_from_machines[8]);

    $action_log = new ActionItem(
        _T("View deployment details", 'xmppmaster'),
        "viewlogs",
        "logfile",
        "logfile",
        "xmppmaster",
        "xmppmaster"
    );


    $reloadAction = new ActionPopupItem(
        _("Restart deployment"),
        "popupReloadDeploy&previous=".$_GET['previous'],
        "reload",
        "",
        "xmppmaster",
        "xmppmaster"
    );

    $raw = 0;
    foreach($info_from_machines[8] as $key => $value) {
        $info_from_machines[2][$raw] = '<span class="machine-inventory">'.$info_from_machines[2][$raw].'</span>';
        $info_from_machines[3][$raw] = '<span class="machine-inventory">'.$info_from_machines[3][$raw].'</span>';
        $info_from_machines[4][$raw] = '<span class="machine-inventory">'.$info_from_machines[4][$raw].'</span>';
        $info_from_machines[5][$raw] = '<span class="machine-inventory">'.$info_from_machines[5][$raw].'</span>';
        $info_from_machines[6][$raw] = '<span class="machine-inventory">'.$info_from_machines[6][$raw].'</span>';
        $info_from_machines[9][] = ($presencemachinexmpplist[$value] == "1") ? 'machineNamepresente' : 'machineName';
        $actionsLog[] = $action_log;
        $actionsReload[] = $reloadAction;
        $raw++;
    }

    echo '<div style="clear:both"></div>';
    if ($count == 0) {
        echo'
<table class="listinfos" cellspacing="0" cellpadding="5" border="1">
<thead>
    <tr>
        <td style="width: ;"><span style=" padding-left: 32px;">Machine Name</span></td>
        <td style="width: ;"><span style=" ">Description</span></td>
        <td style="width: ;"><span style=" ">Operating System</span></td>
        <td style="width: ;"><span style=" ">Status</span></td>
        <td style="width: ;"><span style=" ">Type</span></td>
        <td style="width: ;"><span style=" ">Last User</span>
        </td><td style="width: ;"><span style=" ">Entity</span>
        </td><td style="text-align: center; width: ;"><span>Actions</span></td>
    </tr>
</thead>
<tbody>
</tbody>
</table>';
    } else {
        $action_log = new ActionItem(
            _T("View deployment details", 'xmppmaster'),
            "viewlogs",
            "reload",
            "logfile",
            "xmppmaster",
            "xmppmaster"
        );
        $n = new OptimizedListInfos($info_from_machines[1], _T("Machine Name", "xmppmaster"));

        $n->addExtraInfo($info_from_machines[2], _T("Description", "glpi"));
        $n->addExtraInfo($info_from_machines[3], _T("Operating System", "xmppmaster"));
        $n->addExtraInfo($info_from_machines[7], _T("Status", "xmppmaster"));
        $n->addExtraInfo($info_from_machines[4], _T("Type", "xmppmaster"));
        $n->addExtraInfo($info_from_machines[5], _T("Last User", "xmppmaster"));
        $n->addExtraInfo($info_from_machines[6], _T("Entity", "glpi"));

        $n->setParamInfo($params);
        $n->addActionItem($actionsLog);
        $n->addActionItem($actionsReload);
        $n->setMainActionClasses($info_from_machines[9]);
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $count;
        $n->display();
    }

    echo '<script src="modules/xmppmaster/graph/js/chart.js"></script>';
    ?>
<script>
function fillSearch(content){
    // Select the status or the machine inventory filter
    jQuery("#filter-type").prop("selectedIndex", 0);
    jQuery("#param").val(content);
    // Load the research
    pushSearch();
}
</script>
<?php
      $bluelistcolor = ["#7080AF",
                        "#665899",
                        "#6F01F3",
                        "#5D01A9",
                        "#2D0151",
                        "#3399CC",
                        "#000099",
                        "#6600FF"];
    $max = safeCount($bluelistcolor) - 1;

    if(!$terminate) {
        echo '<script>
    var u = "";
    var r = "";
    var datas = new Array();';
        if ($deploymentsuccess > 0) {
            echo 'datas.push({"label":"Deployment Success", "value":parseInt('.$deploymentsuccess.'), "color": "#2EFE2E", "href":"'.urlredirect_group_for_deploy("deploymentsuccess", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol1 > 0) {
            echo 'datas.push({"label":"WOL 1", "value":parseInt('.$wol1.'), "color": "#202020", "href":"'.urlredirect_group_for_deploy("wol1", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol2 > 0) {
            echo 'datas.push({"label":"WOL 2", "value":parseInt('.$wol2.'), "color": "#2D0151", "href":"'.urlredirect_group_for_deploy("wol2", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol3 > 0) {
            echo 'datas.push({"label":"WOL 3", "value":parseInt('.$wol3.'), "color": "#5D01A9", "href":"'.urlredirect_group_for_deploy("wol3", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($waitingmachineonline > 0) {
            echo 'datas.push({"label":"Waiting Machine Online", "value":parseInt('.$waitingmachineonline.'), "color": "#6F01F3", "href":"'.urlredirect_group_for_deploy("waitingmachineonline", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentpending > 0) {
            echo 'datas.push({"label":"Deployment Pending (Reboot/Shutdown/...)", "value":parseInt('.$deploymentpending.'), "color": "#665899", "href":"'.urlredirect_group_for_deploy("deploymentpending", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentdelayed > 0) {
            echo 'datas.push({"label":"Deployment Delayed", "value":parseInt('.$deploymentdelayed.'), "color": "#7080AF", "href":"'.urlredirect_group_for_deploy("deploymentdelayed", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentstart > 0) {
            echo 'datas.push({"label":"Deployment Start", "value":parseInt('.$deploymentstart.'), "color": "#2E9AFE", "href":"'.urlredirect_group_for_deploy("deploymentstart", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if($abortalternativerelaysdown > 0) {
            echo 'datas.push({"label":"Abort Alternative Relays Down", "value":parseInt('.$abortalternativerelaysdown.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortalternativerelaysdown", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortrelaydown > 0) {
            echo 'datas.push({"label":"Abort Relay Down", "value":parseInt('.$abortrelaydown.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortrelaydown", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortmissingagent > 0) {
            echo 'datas.push({"label":"Abort Missing Agent", "value":parseInt('.$abortmissingagent.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortmissingagent", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortinconsistentglpiinformation > 0) {
            echo 'datas.push({"label":"Abort Inconsistent GLPI Information", "value":parseInt('.$abortinconsistentglpiinformation.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortinconsistentglpiinformation", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }

        if ($abortinforelaymissing > 0) {
            echo 'datas.push({"label":"Abort Info For Relay Missing", "value":parseInt('.$abortinforelaymissing.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortinforelaymissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackageidentifiermissing > 0) {
            echo 'datas.push({"label":"Abort Package Identifier Missing", "value":parseInt('.$abortpackageidentifiermissing.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortpackageidentifiermissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackagenamemissing > 0) {
            echo 'datas.push({"label":"Abort Package Name Missing", "value":parseInt('.$abortpackagenamemissing.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortpackagenamemissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackageversionmissing > 0) {
            echo 'datas.push({"label":"Abort Package Version Missing", "value":parseInt('.$abortpackageversionmissing.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortpackageversionmissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortdescriptormissing > 0) {
            echo 'datas.push({"label":"Abort Descriptor Missing", "value":parseInt('.$abortdescriptormissing.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortdescriptormissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortmachinedisappeared > 0) {
            echo 'datas.push({"label":"Abort Machine Disappeared", "value":parseInt('.$abortmachinedisappeared.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortmachinedisappeared", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortdeploymentcancelledbyuser > 0) {
            echo 'datas.push({"label":"ABORT DEPLOYMENT CANCELLED BY USER", "value":parseInt('.$abortdeploymentcancelledbyuser.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortdeploymentcancelledbyuser", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortduplicatemachines > 0) {
            echo 'datas.push({"label":"Abort Duplicate Machines", "value":parseInt('.$abortduplicatemachines.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("abortduplicatemachines", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($errorunknownerror > 0) {
            echo 'datas.push({"label":"Error Unknown Error", "value":parseInt('.$errorunknownerror.'), "color": "#ff0000", "href":"'.urlredirect_group_for_deploy("errorunknownerror", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($errorhashmissing > 0) {
            echo 'datas.push({"label":"Error Hash Missing", "value":parseInt('.$errorhashmissing.'), "color": "#ff0000", "href":"'.urlredirect_group_for_deploy("errorhashmissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($aborthashinvalid > 0) {
            echo 'datas.push({"label":"Abort Hash Invalid", "value":parseInt('.$aborthashinvalid.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("aborthashinvalid", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($otherstatus > 0) {
            echo 'datas.push({"label":"Other Status", "value":parseInt('.$otherstatus.'), "color": "#FFDA00", "href":"'.urlredirect_group_for_deploy("otherstatus", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }

        foreach($dynamicstatus as $label => $status) {
            if(isset($$label) && $$label) {
                if(preg_match("#^abort#i", $status)) {
                    $color = "#FF8600";
                } elseif(preg_match("#^error#i", $status)) {
                    $color = "#ff0000";
                } else {
                    $color = $bluelistcolor[rand(0, $max)];
                }
                echo 'datas.push({"label":"'.ucfirst(strtolower($status)).'", "value":parseInt('.$$label.'), "color": "'.$color.'", "href":"'.urlredirect_group_for_deploy($label, $_GET['gid'], $_GET['login'], $cmd_id).'"});';
            }
        }
    } else {
        echo '<script>
    var u = "";
    var r = "";
    var datas = new Array();';
        echo 'datas.push({"label":"Deployment Success", "value":'.$deploymentsuccess.', "color": "#2EFE2E", "href":"'.urlredirect_group_for_deploy("deploymentsuccess", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        echo 'datas.push({"label":"Deployment Aborted", "value":'.$aborted.', "color": "orange", "href":"'.urlredirect_group_for_deploy("abort", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        echo 'datas.push({"label":"Deployment Error", "value":'.$errors.', "color": "red", "href":"'.urlredirect_group_for_deploy("error", $_GET['gid'], $_GET['login'], $cmd_id).'"});';

        echo 'var datas2 = new Array();';
        if ($deploymentsuccess > 0) {
            echo 'datas2.push({"label":"Deployment Success", "value":parseInt('.$deploymentsuccess.'), "color": "#2EFE2E", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("deploymentsuccess", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol1 > 0) {
            echo 'datas2.push({"label":"WOL 1", "value":parseInt('.$wol1.'), "color": "#202020", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("wol1", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol2 > 0) {
            echo 'datas2.push({"label":"WOL 2", "value":parseInt('.$wol2.'), "color": "#2D0151", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("wol2", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($wol3 > 0) {
            echo 'datas2.push({"label":"WOL 3", "value":parseInt('.$wol3.'), "color": "#5D01A9", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("wol3", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($waitingmachineonline > 0) {
            echo 'datas2.push({"label":"Waiting Machine Online", "value":parseInt('.$waitingmachineonline.'), "color": "#6F01F3", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("waitingmachineonline", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentpending > 0) {
            echo 'datas2.push({"label":"Deployment Pending (Reboot/Shutdown/...)", "value":parseInt('.$deploymentpending.'), "color": "#665899", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("deploymentpending", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentdelayed > 0) {
            echo 'datas2.push({"label":"Deployment Delayed", "value":parseInt('.$deploymentdelayed.'), "color": "#7080AF", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("deploymentdelayed", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($deploymentstart > 0) {
            echo 'datas2.push({"label":"Deployment Start", "value":parseInt('.$deploymentstart.'), "color": "#2E9AFE", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("deploymentstart", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if($abortalternativerelaysdown > 0) {
            echo 'datas2.push({"label":"Abort Alternative Relays Down", "value":parseInt('.$abortalternativerelaysdown.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortalternativerelaysdown", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortrelaydown > 0) {
            echo 'datas2.push({"label":"Abort Relay Down", "value":parseInt('.$abortrelaydown.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortrelaydown", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortmissingagent > 0) {
            echo 'datas2.push({"label":"Abort Missing Agent", "value":parseInt('.$abortmissingagent.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortmissingagent", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }

        if ($abortinconsistentglpiinformation > 0) {
            echo 'datas2.push({"label":"Abort Inconsistent GLPI Information", "value":parseInt('.$abortinconsistentglpiinformation.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortinconsistentglpiinformation", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }

        if ($abortinforelaymissing > 0) {
            echo 'datas2.push({"label":"Abort Info For Relay Missing", "value":parseInt('.$abortinforelaymissing.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortinforelaymissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackageidentifiermissing > 0) {
            echo 'datas2.push({"label":"Abort Package Identifier Missing", "value":parseInt('.$abortpackageidentifiermissing.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortpackageidentifiermissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackagenamemissing > 0) {
            echo 'datas2.push({"label":"Abort Package Name Missing", "value":parseInt('.$abortpackagenamemissing.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortpackagenamemissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortpackageversionmissing > 0) {
            echo 'datas2.push({"label":"Abort Package Version Missing", "value":parseInt('.$abortpackageversionmissing.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortpackageversionmissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortdescriptormissing > 0) {
            echo 'datas2.push({"label":"Abort Descriptor Missing", "value":parseInt('.$abortdescriptormissing.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortdescriptormissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortmachinedisappeared > 0) {
            echo 'datas2.push({"label":"Abort Machine Disappeared", "value":parseInt('.$abortmachinedisappeared.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortmachinedisappeared", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortdeploymentcancelledbyuser > 0) {
            echo 'datas2.push({"label":"ABORT DEPLOYMENT CANCELLED BY USER", "value":parseInt('.$abortdeploymentcancelledbyuser.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortdeploymentcancelledbyuser", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($abortduplicatemachines > 0) {
            echo 'datas2.push({"label":"Abort Duplicate Machines", "value":parseInt('.$abortduplicatemachines.'), "color": "#FF8600", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("abortduplicatemachines", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($errorunknownerror > 0) {
            echo 'datas2.push({"label":"Error Unknown Error", "value":parseInt('.$errorunknownerror.'), "color": "#ff0000", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("errorunknownerror", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($errorhashmissing > 0) {
            echo 'datas2.push({"label":"Error Hash Missing", "value":parseInt('.$errorhashmissing.'), "color": "#ff0000", "href":"'.urlredirect_group_for_deploy("errorhashmissing", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($aborthashinvalid > 0) {
            echo 'datas2.push({"label":"Abort Hash Invalid", "value":parseInt('.$aborthashinvalid.'), "color": "#FF8600", "href":"'.urlredirect_group_for_deploy("aborthashinvalid", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }
        if ($otherstatus > 0) {
            echo 'datas2.push({"label":"Other Status", "value":parseInt('.$otherstatus.'), "color": "#FFDA00", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy("otherstatus", $_GET['gid'], $_GET['login'], $cmd_id).'"});';
        }

        foreach($dynamicstatus as $label => $status) {
            if(isset($$label) && $$label) {
                if(preg_match("#^abort#i", $status)) {
                    $color = "#FF8600";
                } elseif(preg_match("#^error#i", $status)) {
                    $color = "#ff0000";
                } else {
                    $color = $bluelistcolor[rand(0, $max)];
                }
                echo 'datas2.push({"label":"'.ucfirst(strtolower($status)).'", "value":parseInt('.$$label.'), "color": "'.$color.'", "onclick":"fillSearch", "href":"'.urlredirect_group_for_deploy($label, $_GET['gid'], $_GET['login'], $cmd_id).'"});';
            }
        }

        $aborted = 0;
        $errors = 0;
    }
    echo 'chart("holder", datas);';
    echo 'if(typeof(datas2) != "undefined"){';
    echo 'chart("holder2", datas2);';
    echo "}";
    echo'</script>';
}
?>

<script>
    jQuery(".status, .machine-inventory").on("click", function(){
        // Select the status or the machine inventory filter
        if(jQuery(this).prop("class") == "status")
        {
            jQuery("#filter-type").prop("selectedIndex", 0);
        }
        else if(jQuery(this).prop("class") == "machine-inventory"){
            jQuery("#filter-type").prop("selectedIndex", 1);
        }
        // Put the status value
        jQuery("#param").val(jQuery(this).text());
        // Load the research
        pushSearch();
    });
</script>
