<?php
/*
 * (c) 2017 Siveo, http://www.siveo.net
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
 *
 * File customQA.php
 */
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

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

include_once('modules/pulse2/includes/menu_actionaudit.php');
echo "<br><br><br>";

    $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
    $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
    $ma = xmlrpc_getMachinefromjid($machine);

    if (isset($_POST["bcreate"])){
        header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/editfileconf", array()));
    }


$param = array(
    "cn" => $_GET['cn'],
    "type" => $_GET['type'],
    "objectUUID" => $_GET['objectUUID'],
    "entity" => $_GET['entity'],
    "owner" => $_GET['owner'],
    "user" => $_GET['user'],
    "os" => $_GET['os']
);

    $ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxFilterfileconf"),"container", $param);
    $p = new PageGenerator(_T("Edit config file", 'xmppmaster')." on ". $ma['hostname']);
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm(array());
    echo "<br><br>";
$ajax->display();
$ajax->displayDivToUpdate();

?>
