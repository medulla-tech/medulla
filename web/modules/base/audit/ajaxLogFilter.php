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

require_once("modules/base/includes/logging-xmlrpc.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");
require_once("includes/auditCodesManager.php");
$auditManager = new AuditCodesManager();

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
if (isset($_GET["start"])) $start = $_GET["start"];
else
$start=0;

$module = $_GET["page"];

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

$loglist = array();

// get logs
if(isset($_GET["user"])) {
    $user = $_GET["user"];
    list($nblog, $loglist) = get_log_user_filter($start,$start+$maxperpage,$module,$user,$filter,$filtertype,$startdate,$enddate);
    $logref = "";
}
else {
    list($nblog, $loglist) = get_log_filter($start,$start+$maxperpage,$module,$filter,$filtertype,$startdate,$enddate);
    $logref = $module;
}

$loguser   = array();
$logid     = array();
$logdate   = array();
$logaction = array();
$logplugin = array();
$loguser   = array();
$logplug   = array();
$loginterface   = array();
$logipinterface = array();
$logobject      = array();
$logtypeobject  = array();
$logid     = array();
$logcommit = array();
$logparams = array();

if($loglist) {
    $i = 0;
    foreach ($loglist as $log) {
        if(is_array($log)) {
            $logid[]     = $log["id"];
            /* transform LDAP user uri to a simple string */
            $loguser[]   = getObjectName($log["user"]);
            $logcommit[] = $log["commit"];
            $logdate[]   = $log["date"];
            $logplug[]   = $auditManager->getCode($log["plugin"]);
            if(count($log["objects"]) > 0) {
                $logobject[]     = getObjectName($log["objects"][0]["object"]);
                $logtypeobject[] = $auditManager->getCode($log["objects"][0]["type"]);
                if(isset($log["objects"][1]["object"]))
                    $logaction[] = $auditManager->getCode($log["action"])." (".getObjectName($log["objects"][1]["object"]).")";
                else
                    $logaction[] = $auditManager->getCode($log["action"]);
            }
            else {
                $logobject[]     = " ";
                $logtypeobject[] = " ";
                $logaction[] = $auditManager->getCode($log["action"]);
            }
            $logparams[$i]["logid"] = $log["id"];
            $logparams[$i]["logref"] = $logref;
            $i++;
        }
    }
}

$n = new LogListInfos($logdate, _("Date"));
$n->setNavBar(new AjaxLogNavBar($nblog, $filter, $maxperpage));
$n->setItemCount($nblog);
$n->start = 0;
$n->end = $nblog - 1;
$n->setRowsPerPage($maxperpage);
$n->addCommitInfo($logcommit, "Commit");
$n->addExtraInfo($loguser,_("User"));
$n->addExtraInfo($logaction,_("Event"));
$n->addExtraInfo($logtypeobject,_("Type"));
$n->addExtraInfo($logobject,_("Object Name"));
if ($module == "all") {
    $n->addExtraInfo($logplug,_("Module"));
}
$n->addExtraInfo($logcommit,_("Result"));
$n->setParamInfo($logparams);
$n->disableFirstColumnActionLink();
$n->setTableHeaderPadding(1);
$n->addActionItem(new ActionItem(_("View details"),"logview","display","logid"));
$n->setName(_T("Logs", "base"));
$n->display();

?>
