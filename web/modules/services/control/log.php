<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/services/control/localSidebar.php");
require("graph/navbar.inc.php");

$service = isset($_GET['service']) ? $_GET['service'] : "";

$ajax = new AjaxFilter(urlStrRedirect("services/control/ajaxLogFilter"), "logContainer", 
                       array("service" => $service));
$ajax->display();

#if (!$service)
#    $sidemenu->forceActiveItem($_GET['parent']);

if ($service)
    $title = sprintf(_T("%s service log"), ucfirst(substr($service, 0, -8)));
else
    $title = _T("Services log");

$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();

$ajax->displayDivToUpdate();

?>
