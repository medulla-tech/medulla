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

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/backuppc/includes/functions.php");
require_once("modules/backuppc/includes/html.inc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require("graph/navbar.inc.php");
require("localSidebar.php");
?>
<style>
li.folder a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.folderg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/folder.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.console a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.consoleg a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/console.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quick a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guaca a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

li.guacag a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/guaca.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
li.quickg a {
        padding: 0px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/quick.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
        filter: grayscale(50%);
        -webkit-filter: grayscale(50%);
        -moz-filter: grayscale(50%);
        opacity:0.5;
}
</style>
<?php
$computer_name = $_GET['cn'];
$uuid = $_GET['objectUUID'];

// ==========================================================
// Receiving request to set backup for host
// ==========================================================

if (isset($_POST['setBackup'],$_POST['host'])) {
    $response = set_backup_for_host($_POST['host']);
    // Checking reponse
    if (isset($response)) {
        if (isXMLRPCError() || $response['err']) {
            xmlrpc_setfromxmppmasterlogxmpp(_T('Notify Error : Backup configuration Computer', 'backuppc')." ". $computer_name." ".$response['err'],
                                                "BPC",
                                                '',
                                                0,
                                                $computer_name ,
                                                'Manual',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Backup | Configuration | Error | Manual | auto');
            new NotifyWidgetFailure(nl2br($response['errtext']));
        }
        else {
            xmlrpc_setfromxmppmasterlogxmpp(_T('Notify Computer :', 'backuppc')." ". $computer_name." "._T('has been added to backup system successfully.', 'backuppc'),
                                                "BPC",
                                                '',
                                                0,
                                                $computer_name ,
                                                'Manual',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Backup | Configuration | Manual | auto');
            new NotifyWidgetSuccess(sprintf(_T('Computer %s has been added to backup system successfully.<br />You can now configure its filesets and scheduling.', 'backuppc'), $computer_name));
            $_GET['tab'] = 'tab2';
        }
    }
    // Setting default profile to nightly
    set_host_period_profile($_POST['host'], 1);

    $rep = getComputersOS($_POST['host']);
    $os = $rep[0]['OSName'];
    // Init best profile
    $bestProfile = NULL;
    $bestSim = 0;

    $backup_profiles = get_backup_profiles();
    foreach ($backup_profiles as $profile){
        $profilename = $profile['profilename'];
        similar_text($os, $profilename,$perc);//
        if ($perc > $bestSim){
            $bestSim = $perc;
            $bestProfile = $profile;
        }
        // Windows 7 special case
        similar_text($os, str_replace('/Vista','',$profilename),$perc);//
        if ($perc > $bestSim){
            $bestSim = $perc;
            $bestProfile = $profile;
        }
    }

    if ($bestSim > 35) {
        $_GET['preselected_profile'] = $bestProfile['id'];
        set_host_backup_profile($_POST['host'], $bestProfile['id']);
    }
}

// ==========================================================
// Receiving POST DATA
// ==========================================================

if (isset($_POST['bconfirm'],$_POST['host'])){

    $backup_port_reverse_ssh = get_host_backup_reverse_port($_POST['host']);
    $rsync_path = get_host_rsync_path($_POST['host']);

    // Setting host profiles
    set_host_backup_profile($_POST['host'], $_POST['backup_profile']);
    set_host_period_profile($_POST['host'], $_POST['period_profile']);
    // Sending Host config to backupPC
    $cfg = array();
    // 1 - Shares and exclude settings
    $cfg['RsyncShareName'] = $_POST['sharenames'];
    // Charset
    $cfg['ClientCharset'] = $_POST['encoding'];

    // Splitting excludes by \n
    foreach ($_POST['excludes'] as $key => $value) {
        $_POST['excludes'][$key] = explode("\n",trim($value));
        for ($j = 0 ; $j< count($_POST['excludes'][$key]); $j++)
            $_POST['excludes'][$key][$j] = trim ($_POST['excludes'][$key][$j]);
    }

    $cfg['BackupFilesExclude'] = array_combine($_POST['sharenames'],$_POST['excludes']);

    // 2 -Backup Period settings

    $cfg['FullPeriod'] = fmtFloat(fmtfloat($_POST['full'])-0.03);
    $cfg['IncrPeriod'] = fmtFloat(fmtfloat($_POST['incr'])-0.03);

    // Blackout periods
    $starthours = $_POST['starthour'];
    $endhours = $_POST['endhour'];

    $cfg['BlackoutPeriods'] = array();

    for ($i = 0 ; $i<count($starthours); $i++) {
        $daystring = implode(', ',$_POST['days'.$i]);
        $cfg['BlackoutPeriods'][] = array(
            'hourBegin' => hhmm2float($starthours[$i]),
            'hourEnd'   => hhmm2float($endhours[$i]),
            'weekDays'  => $daystring
                );
    }
    // Rsync and NmbLookup command lines
    $rep = getComputersOS($_POST['host']);
    $os = strtolower($rep[0]['OSName']);
    
    $backup_manager_cmd  = "/usr/sbin/pulse2-connect-machine-backuppc -m ".$_POST['host']." -p ".$backup_port_reverse_ssh;
    $backup_manager_cmd1 = "/usr/sbin/pulse2-disconnect-machine-backuppc -m ".$_POST['host']." -p ".$backup_port_reverse_ssh;
    $cfg['DumpPreUserCmd']  = $cfg['RestorePreUserCmd']  = $backup_manager_cmd;
    $cfg['DumpPostUserCmd'] = $cfg['RestorePostUserCmd'] = $backup_manager_cmd1;
    $cfg['ClientNameAlias'] = "localhost";
    

    $cfg['RsyncClientPath'] = $rsync_path;
    if (strpos($os, 'ubuntu') !== false || strpos($os, 'linux') !== false ){
        $cfg['RsyncClientPath'] = " sudo '".$rsync_path."' ";
    }
    $username = "pulseuser";
    $sudo="";
    if (strtolower($os) == 'macos' || strpos($os, 'ubuntu') || strpos($os, 'linux') ) {
        $sudo="sudo";
     }

    $cfg['RsyncClientCmd'] = '$sshPath -q -x -o StrictHostKeyChecking=no -l '.$username.' -p '.$backup_port_reverse_ssh.' localhost  $rsyncPath $argList+';
    $cfg['RsyncClientRestoreCmd'] = '$sshPath -q -x -o StrictHostKeyChecking=no -l '.$username.' -p '.$backup_port_reverse_ssh.' localhost $rsyncPath $argList+';
    
    $cfg['NmbLookupCmd'] = '/usr/bin/python /usr/bin/pulse2-uuid-resolver -A $host';
    $cfg['NmbLookupFindHostCmd'] = '/usr/bin/python /usr/bin/pulse2-uuid-resolver $host';
    $cfg['XferMethod'] = 'rsync';
    $cfg['RsyncRestoreArgs'] = explode(" ", "--numeric-ids --perms --owner --group -D --links --hard-links --times --block-size=2048 --relative --ignore-times --recursive --super");
    $cfg['PingCmd'] = '/bin/true';

    $cfg['UserCmdCheckStatus'] = 1;

    // Enable or disable backup
    $cfg['BackupsDisable'] = isset($_POST['active'])?'0':'1';

    set_host_config($_POST['host'], $cfg);
    xmlrpc_setfromxmppmasterlogxmpp(_T('Notify Computer :', 'backuppc')." ". $computer_name." "._T('Save configure host ', 'backuppc'),
                                                "BPC",
                                                '',
                                                0,
                                                $computer_name ,
                                                'Manual',
                                                '',
                                                '',
                                                '',
                                                "session user ".$_SESSION["login"],
                                                'Backup | Configuration | Manual | auto');
    new NotifyWidgetSuccess(_T('Configuration saved', 'backuppc'));
}

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();


// ==========================================================
// Tab generator
// ==========================================================

$p = new TabbedPageGenerator();
$p->addTop(sprintf(_T("%s's backup status", 'backuppc'),$computer_name), "modules/backuppc/backuppc/header.php");

// Adding tabs
$p->addTab("tab1", _T('Summary', 'backuppc'), "", "modules/backuppc/backuppc/hostSummary.php", array('objectUUID'=>$uuid, 'cn'=>$computer_name));

if (host_exists($uuid))
{
    $p->addTab("tab2", _T('Configuration', 'backuppc'), "", "modules/backuppc/backuppc/edit.php", array('objectUUID'=>$uuid, 'cn'=>$computer_name));
    $p->addTab("tab3", _T('Advanced scripts', 'backuppc'), "", "modules/backuppc/backuppc/advScripts.php", array('objectUUID'=>$uuid, 'cn'=>$computer_name));
    $p->addTab("tab4", _T('File search', 'backuppc'), "", "modules/backuppc/backuppc/fileSearch.php", array('objectUUID'=>$uuid, 'cn'=>$computer_name));
}

$p->setSideMenu($sidemenu);
$p->display();

?>
