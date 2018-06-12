<?php
/**
 *  (c) 2015-2017 Siveo, http://www.siveo.net
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
 *
 * file ajaxFiltercustom.php
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
?>
<style>
a.info{
    position:relative;
    z-index:24;
    color:#000;
    text-decoration:none
}

a.info:hover{
    z-index:25;
    background-color:#FFF
}

a.info span{
    display: none
}

a.info:hover span{
    display:block;
    position:absolute;
    top:2em; left:2em; width:25em;
    border:1px solid #000;
    background-color:#E0FFFF;
    color:#000;
    text-align: justify;
    font-weight:none;
    padding:5px;
}
</style>

<?php
    global $conf;
    $maxperpage = $conf["global"]["maxperpage"];
    $filter = $_GET["filter"];


    if (isset($_GET["start"])) {
        $start = $_GET["start"];
    } else {
        $start = 0;
    }

    $result = xmlrpc_getlistcommandforuserbyos($_SESSION['login'], '', $start, $end, $filter, $edit=1);

    $params = array();
    $names  = array();
    $desc   = array();
    $os   = array();
    $count = $result['len'];
    foreach($result['command'] as $val){
        $names[] = $val['namecmd'];
        $desc[]  = $val['description'];
        $os[]    = $val['os'];
        $val['editcreate'] = 'editeqa';
        $params[] = $val;
    }
    $n = new OptimizedListInfos($names, _T("Custom command name", "xmppmaster"));
    $n->setCssClass("package");
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($desc, _T("Description", "xmppmaster"));
    $n->addExtraInfo($os, _T("Operating System", "xmppmaster"));
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->start = isset($_GET['start'])?$_GET['start']:0;
    $n->end = (isset($_GET['end'])?$_GET['end']:$maxperpage);

$n->addActionItem(new ActionItem(_T("Edit a Quick Action", "xmppmaster"), "editqa", "edit", "xmppmaster", "xmppmaster", "xmppmaster"));
$n->addActionItem(new ActionPopupItem(_T("Delete a Quick Action", "xmppmaster"), "deleteqa", "delete", "xmppmaster", "xmppmaster", "xmppmaster"));
print "<br/><br/>";
$n->display();
?>
