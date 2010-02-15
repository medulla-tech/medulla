<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: index.php 382 2008-03-03 15:13:24Z cedric $
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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/base/includes/logging-xmlrpc.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");
require_once("includes/auditCodesManager.php");
$auditManager = new AuditCodesManager();

$p = new PageGenerator();
$p->setTitle("Action details");
if($_GET["logref"]) {
    $item = "index".$_GET["logref"];
}
else {
    $item = " ";
}
$sidemenu->forceActiveItem($item);
$p->setSideMenu($sidemenu);
$p->display();

$log=get_log_by_id($_GET["logid"]);

if($log[0]["commit"]) {
    $style = "audit_ok";
}
else {
    $style = "audit_nok";
}

$f = new ValidatingForm(array("class" => $style));
$f->push(new Table());
$f->add(new TrFormElement(_("Date"), new HiddenTpl("date")),
        array("value" => $log[0]["date"]));
$f->add(new TrFormElement(_("User which do the action"), new HiddenTpl("user")),
        array("value" => getObjectName($log[0]["user"])." (".$log[0]["user"].")"));
$f->add(new TrFormElement(_("Action"), new HiddenTpl("action")),
        array("value" => $auditManager->getCode($log[0]["action"])));
$f->add(new TrFormElement(_("Plugin"), new HiddenTpl("plugin")),
        array("value" => $auditManager->getCode($log[0]["plugin"])));
$f->add(new TrFormElement(_("Client"), new HiddenTpl("interface")),
        array("value" => $log[0]["client-type"]));
$f->add(new TrFormElement(_("Client hostname"), new HiddenTpl("hostname")),
        array("value" => $log[0]["client-host"]));
$f->add(new TrFormElement(_("Agent Hostname"), new HiddenTpl("ahostname")),
        array("value" => $log[0]["agent-host"]));
        
$i=1;

/*echo "<pre>";
print_r($log[0]["objects"]);
echo "</pre>";*/

foreach ($log[0]["objects"] as $obj) {    

    $f->add(new TrFormElement(_("Object"), new HiddenTpl("obj".$i)),
        array("value" => $obj["object"]));
    $f->add(new TrFormElement(_("Object type"), new HiddenTpl("type".$i)),
        array("value" => $auditManager->getCode($obj["type"])));

    if (isset($obj["previous"])  && isset($obj["current"])) {

        if(isset($obj["previous"][0])) {
            $previous = $obj["previous"][0];
        }
        else {
            $previous = " ";
        }

        if(isset($obj["current"][0])) {
            $current = $obj["current"][0];
        }
        else {
            $current = " ";
        }        
    
        if($previous != " " or $current != " ") {
            $f->add(new TrFormElement(_("Previous"), new DisabledInputTpl("previous")), 
                array("value"=> $previous, "disabled"=>True));
            
            /*for ($i = 1; $i < sizeof($obj["previous"]); $i++) {
                $f->add(new TrFormElement("",new DisabledInputTpl("previous")), 
                array("value"=> $previous, "disabled"=>True));
            }*/
            
            $f->add(new TrFormElement(_("Current"),new DisabledInputTpl("current")), 
                array("value"=> $current, "disabled"=>True));

            /*for ($i = 1; $i < sizeof($obj["current"]); $i++) {
                $f->add(new TrFormElement("",new DisabledInputTpl("current")), 
                array("value"=> $current, "disabled"=>True));            
            }*/
        }
    }
    $i++;        
}
$f->pop();
$f->display();

$g = new ValidatingForm();
$g->push(new DivExpertMode());
$g->push(new Table());
foreach ($log[0]["parameters"] as $param=>$paramvalue) {
    $g->add(new TrFormElement($param, new HiddenTpl("param"+$param)),
            array("value" => $paramvalue));
}
$g->pop();
$g->pop();
$g->display();

?>
