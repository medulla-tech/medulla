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

if($__submod == "audit") {
    require_once("localSidebar.php");
}
require("graph/navbar.inc.php");
require_once("modules/base/includes/logging-xmlrpc.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");
require_once("includes/auditCodesManager.php");
$auditManager = new AuditCodesManager();

$p = new PageGenerator();
$p->setTitle(_("Event details"));
if(isset($_GET["logref"])) {
    $item = "index".$_GET["logref"];
}
else {
    $item = "index";
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
$f->add(new TrFormElement(_("User that initiated the event"), new HiddenTpl("user")),
        array("value" => getObjectName($log[0]["user"])." (".$log[0]["user"].")"));
$f->add(new TrFormElement(_("Event"), new HiddenTpl("action")),
        array("value" => $auditManager->getCode($log[0]["action"])));
$f->add(new TrFormElement(_("Plugin"), new HiddenTpl("plugin")),
        array("value" => $auditManager->getCode($log[0]["plugin"])));
$f->add(new TrFormElement(_("Client"), new HiddenTpl("interface")),
        array("value" => $log[0]["client-type"]));
$f->add(new TrFormElement(_("Client hostname"), new HiddenTpl("hostname")),
        array("value" => $log[0]["client-host"]));
$f->add(new TrFormElement(_("Agent hostname"), new HiddenTpl("ahostname")),
        array("value" => $log[0]["agent-host"]));

$i = 1;
foreach ($log[0]["objects"] as $obj) {
    $f->add(new TrFormElement(_("Object"), new HiddenTpl("obj".$i)),
        array("value" => $obj["object"]));
    $f->add(new TrFormElement(_("Object type"), new HiddenTpl("type".$i)),
        array("value" => $auditManager->getCode($obj["type"])));
    if (isset($obj["current"])) {
        foreach($obj["current"] as $current) {
            if($current) {
                $current_val = trim($current);
            }
            else {
                $current_val = "(empty)";
            }
            $f->add(new TrFormElement(_("Value"), new HiddenTpl("current")), 
                array("value"=> $current_val));
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
