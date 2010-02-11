<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: ajaxFilter.php 382 2008-03-03 15:13:24Z cedric $
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


//require("includes/PageGenerator.php");

require("modules/base/includes/logging-xmlrpc.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");

global $conf;
if(isset($conf["global"]["maxlogperpage"])) {
    $maxlogperpage = $conf["global"]["maxlogperpage"];
}
else {
    $maxlogperpage = 10;
}

$user=$_GET["user"];


if (isset($_GET["start"])) $start = $_GET["start"];
else
$start=0;

if ( ($_GET["filtertype"]=="") or ($_GET["filter"]=="") )
{
    $filter=0;
    $filtertype=0;    
}
else
{
    $filtertype=$_GET["filtertype"];
    $filter=$_GET["filter"];
}

$startdate = 0;
$enddate = 0;
if($_GET["begindate"]!=_("Begin date")) {
    $startdate = $_GET["begindate"];
}
if ($_GET["enddate"]!=_("End date")) {
    $enddate = $_GET["enddate"];
}

$module = "all";

$loguser = array();
$loglist = array();
list($nblog, $loglist) = get_log_user_filter($start,$start+$maxlogperpage,$module,$user,$filter,$filtertype,$startdate,$enddate);
$logid = array();
$logdate = array();
$logaction = array();
$logplugin = array();
$loguser = array();
$logplug = array();
$logobject = array();
$logtypeobject = array();
$loginterface = array();
$logipinterface = array();
$logid = array();
$logcommit = array();

if($nblog > 0) {
    foreach ($loglist as $log) {
        if (is_array($log)) {
            $logid[]=$log["id"];
            $loguser[]=$log["user"];
            $logcommit[]=$log["commit"];
            $logdate[]=$log["date"];
            $logaction[]=_($log["action"]);
            if(isset($log["plug"])) {
                $logplug[]=$log["plug"];
            }
            else {
                $logplug[]=" ";
            }
            if (isset($log["objects"][0]["object"])) {
                $logobject[]=$log["objects"][0]["object"];
                $logtypeobject[]=_($log["objects"][0]["type"]);      
            } 
            else {
                $logobject[]=" ";
                $logtypeobject[]=" ";
            }
        }   
    }
}

$n = new LogListInfos($logdate, _("Date"));
$n->setNavBar(new AjaxLogNavBar($nblog, $filter, $maxlogperpage));
$n->setItemCount($nblog);
$n->start = 0;
$n->end = $nblog - 1;
$n->setRowsPerPage($maxlogperpage);
$n->addCommitInfo($logcommit,"Commit");
$n->addExtraInfo($loguser,_("User"));
$n->addExtraInfo($logaction,_("Action"));
$n->addExtraInfo($logplug,"Plugin");
$n->addExtraInfo($logobject,_("Object Name"));
$n->addExtraInfo($logtypeobject,_("Type"));
$n->setParamInfo($logid,"logid");
$n->disableFirstColumnActionLink();
$n->addActionItem(new ActionItem(_("View details"),"userlogview","display","logid"));
$n->setName(_("Logs"));
$n->display();

?>
