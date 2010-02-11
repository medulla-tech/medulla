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
require("modules/base/includes/logging-xmlrpc.inc.php");
require("modules/base/includes/AjaxFilterLog.inc.php");

$p = new PageGenerator();
$p->setTitle("Action details");
$p->setSideMenu($sidemenu);
$log=get_log_by_id($_GET["logid"]);
$f = new ValidatingForm();
$f->push(new Table());

$f->add(    new TrFormElement(_T("Date"), new HiddenTpl("date")),
            array("value" => $log[0]["date"])
       );

$f->add(    new TrFormElement(_T("User which do the action"), new HiddenTpl("user")),
            array("value" => $log[0]["user"])
       );

$f->add(    new TrFormElement(_T("Action"), new HiddenTpl("action")),
            array("value" => $log[0]["action"])
       );

$f->add(    new TrFormElement(_T("Plugin"), new HiddenTpl("plugin")),
            array("value" => $log[0]["plugin"])
       );
       
$f->add(    new TrFormElement(_T("Client"), new HiddenTpl("interface")),
            array("value" => $log[0]["client-type"])
       );

$f->add(    new TrFormElement(_T("Client hostname"), new HiddenTpl("hostname")),
            array("value" => $log[0]["client-host"])
       );
       
$f->add(    new TrFormElement(_T("Agent Hostname"), new HiddenTpl("ahostname")),
            array("value" => $log[0]["agent-host"])
       );
$i=1;
foreach ( $log[0]["objects"] as $obj)
{
    
$f->add(    new TrFormElement(_T("Objet"), new HiddenTpl("obj".$i)),
            array("value" => $obj["object"])
       );

$f->add(    new TrFormElement(_T("Objet type"), new HiddenTpl("type".$i)),
            array("value" => $obj["type"])
       );
    $i++;
}
        if (isset($obj["previous"])  && isset($obj["current"]))
        {
            $f->add(new TrFormElement(_("Previous"),new DisabledInputTpl("previous")), array("value"=> $obj["previous"][0],"disabled"=>True));
            for ($i = 1; $i < sizeof($obj["previous"]); $i++)
            {
                    $f->add(new TrFormElement("",new DisabledInputTpl("previous")), array("value"=> $obj["previous"][0],"disabled"=>True));
            }
            $f->add(new TrFormElement(_("Current"),new DisabledInputTpl("current")), array("value"=> $obj["current"][0],"disabled"=>True));
            for ($i = 1; $i < sizeof($obj["current"]); $i++)
            {
                    $f->add(new TrFormElement("",new DisabledInputTpl("current")), array("value"=> $obj["current"][0],"disabled"=>True));
            }
        }

$p->display();
$f->display();

$f->pop();

$g = new ValidatingForm();
$g->push(new DivExpertMode());
$g->push(new Table());

foreach ( $log[0]["parameters"] as $param=>$paramvalue)
{
    $g->add(    new TrFormElement($param, new HiddenTpl("param"+$param)),
            array("value" => $paramvalue)
    );
}

$g->pop();
$g->pop();
$g->display();




?>
