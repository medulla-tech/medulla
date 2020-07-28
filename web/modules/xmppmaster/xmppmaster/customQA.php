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

<?php

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

    if (isset($_POST["bcreate"])){
        header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/editqa", array()));
    }

    $ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxFiltercustom"));
    $p = new PageGenerator(sprintf (_T("Quick action list for user %s", 'xmppmaster'),$_SESSION['login']));
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm(array());
    echo "<br><br>";
    $f->add(new HiddenTpl("editcreate"), array("value" => "createqa", "hide" => True));
    $f->addButton("bcreate", _T("Create new Quick Action", "xmppmaster"));
    $f->display();
$ajax->display();
$ajax->displayDivToUpdate();

?>
