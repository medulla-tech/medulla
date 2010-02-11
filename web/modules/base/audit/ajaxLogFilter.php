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
$maxperpage = $conf["global"]["maxperpage"];
if (isset($_GET["start"])) $start = $_GET["start"];
else
$start=0;

$module=$_GET["page"];

if ( ($_GET["filtertype"]!=NULL) && ($_GET["filter"]!=NULL) ) {
    $filter=$_GET["filter"];
    $filtertype=$_GET["filtertype"];
}
else {
    $filter="";
    $filtertype="";
}

$startdate = 0;
$enddate = 0;
if($_GET["begindate"]!=_("Begin date")) {
    $startdate = $_GET["begindate"];
}
if ($_GET["enddate"]!=_("End date")) {
    $enddate = $_GET["enddate"];
}

$loguser= array();
$loglist= array();
$logid= array();
list($nblog, $loglist) = get_log_filter($start,$start+$maxperpage,$module,$filter,$filtertype,$startdate,$enddate);
$logdate = array();
$logaction = array();
$logplugin = array();
$loguser= array();
$logplug= array();
$loginterface= array();
$logipinterface= array();
$logobject = array();
$logtypeobject = array();
$logid= array();
$logcommit= array();

if($loglist) {
    foreach ($loglist as $log) {
        if(is_array($log)) {
            $logid[]=$log["id"];
            $loguser[]=$log["user"];
            $logcommit[]=$log["commit"];
            $logdate[]=$log["date"];
            $logaction[]=_($log["action"]);
            $logplug[]=$log["plugin"];
            if(count($log["objects"]) > 0){
                $logobject[]=$log["objects"][0]["object"];
                $logtypeobject[]=_($log["objects"][0]["type"]);      
            }else{
                $logobject[]=" ";
                $logtypeobject[]=" ";
            }
        }   
    }
}

$n = new LogListInfos($logdate, _("Date"));
$n->setNavBar(new AjaxLogNavBar($nblog, $filter, $maxperpage));
$n->setItemCount($nblog);
$n->start = 0;
$n->end = $nblog - 1;
$n->setRowsPerPage($maxperpage);
$n->addCommitInfo($logcommit,"Commit");
$n->addExtraInfo($loguser,_("User"));
$n->addExtraInfo($logaction,_("Action"));
$n->addExtraInfo($logtypeobject,_("Type"));
$n->addExtraInfo($logobject,_("Object Name"));
if ($module=="all")
{
    $n->addExtraInfo($logplug,_("Plugin"));    
}
$n->setParamInfo($logid,"logid");
$n->disableFirstColumnActionLink();
$n->addActionItem(new ActionItem(_("View details"),"view","display","logid"));
$n->setName(_("Logs"));
$n->display();

?>
