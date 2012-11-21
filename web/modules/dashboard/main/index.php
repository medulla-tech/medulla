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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

$topLeft = 1;
require("graph/navbar.inc.php");

$p = new PageGenerator(_T("Dashboard", "dashboard"));
$p->display();

$f = new AjaxPage(urlStrRedirect("dashboard/main/ajaxPanels"), "dashboard", array("parent" => $_GET['action']), 5);
$f->display();

?>
<script src="jsframework/cookiejar.js"></script>
<script type="text/javascript" src="modules/dashboard/graph/js/raphael-min.js"></script>
<script type="text/javascript" src="modules/dashboard/graph/js/g.raphael-min.js"></script>
<script type="text/javascript" src="modules/dashboard/graph/js/g.pie-min.js"></script>
<script type="text/javascript" src="modules/dashboard/graph/js/g.bar-min.js"></script>
<style type="text/css">
    #section, #sectionTopRight, #sectionBottomLeft { margin: 0 0 0 17px; }
    #sectionTopRight { border-left: none; }
    #sectionTopLeft {
        height: 9px;
        padding: 0;
        margin: 0;
        background: url("img/common/sectionTopLeft.gif") no-repeat top left transparent;
    }
    #dashboard .dashboard-column {
        float: left;
        width: 220px;
        border: 1px solid white;
        background: white;
        min-height: 100px;
        border-radius: 10px;
        -moz-border-radius: 10px;
        -webkit-border-radius: 10px;
        margin-right: 5px;
        margin-bottom: 5px;
    }

    #dashboard .panel .handle {
        cursor: move;
    }

    .panel {
        float: left;
        background-color: rgb(238, 238, 238);
        padding: 5px;
        margin: 5px 5px 10px;
        width: 200px;
        -webkit-border-radius: 10px;
           -moz-border-radius: 10px;
                border-radius: 10px;
    }

    .subpanel {
        background-color: #E5E5E5;
        padding: 5px;
        margin: 10px;
        -webkit-border-radius: 5px;
           -moz-border-radius: 5px;
                border-radius: 5px;
    }

    .subpanel ul {
        margin: .5em 1em;
        padding: 0.5em;
    }

    .subpanel h4 {
        padding: 0;
    }

    .panel .errors {
        color: #a40000;
        font-weight: bold;
    }
</style>
