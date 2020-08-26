<?php
/*
 * (c) 2016-2020 Siveo, http://www.siveo.net
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
 * file : xmppmaster/xmppmaster/monitoringview.php
 */
?>
<style type='text/css'>
textarea {
    width:50% ;
    height:150px;
    margin:auto;   /* example for centering */
    display:block; /* the actual centering ! */
}
.shadow
{
  -moz-box-shadow: 4px 4px 10px #888;
  -webkit-box-shadow: 4px 4px 10px #888;
  box-shadow:4px 4px 6px #888;
}

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
li.monit a {
        padding: 3px 0px  5px 22px;
        margin: 0 0px 0 0px;
        background-image: url("modules/base/graph/computers/process.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
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
<?
    require("modules/base/computers/localSidebar.php");
    require("graph/navbar.inc.php");
    require_once("modules/xmppmaster/includes/xmlrpc.php");

    require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
    require_once("modules/dyngroup/includes/utilities.php");
    if(!$_GET['uninventoried']){
      include_once('modules/pulse2/includes/menu_actionaudit.php');
    }
    $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
    if(!$_GET['uninventoried']){
      $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
    }
    else{
      $machine =$_GET['jid'];
    }

    $hostname = $_GET['cn'];

    $p = new PageGenerator(_T("Monitoring for", 'xmppmaster')." $hostname");

    $p->setSideMenu($sidemenu);
    $p->display();

    $panels_list = xmlrpc_getPanelsForMachine($hostname);
    echo "<table class='listinfos' cellspacing='0' cellpadding='5' border='1'>";
        echo "<thead>";
            echo "<tr>";
                echo '<td>'._T("Monitoring item", "xmppmaster").'</td>';
                echo '<td>'._T("Last value", "xmppmaster").'</td>';
                echo '<td>'._T("History", "xmppmaster").'</td>';
            echo "</tr>";
        echo "</thead>";
        echo "<tbody>";
            for($i = 0; $i < count($panels_list); ++$i) {
                echo "<tr>";
                    echo '<td>'.$panels_list[0]['title'].'</td>';
                    echo '<td>';
                        if ($panels_list[0]['title'] == 'Online-Offline Status') {
                            $last_val = xmlrpc_getLastOnlineStatus($machine);
                        }
                        echo $last_val;
                    echo '</td>';
                    echo "<td>";
                        $from = time() - (24 * 60 * 60);
                        $to = time();
                        $url = xmlrpc_getPanelImage($hostname, $panels_list[0]['title'], $from, $to);
                        echo "<a href='".$url."'>1 day</a>";
                        echo " | ";
                        $from = time() - (7 * 24 * 60 * 60);
                        $to = time();
                        $url = xmlrpc_getPanelImage($hostname, $panels_list[0]['title'], $from, $to);
                        echo "<a href='".$url."'>1 week</a>";
                        echo " | ";
                        $from = time() - (31 * 24 * 60 * 60);
                        $to = time();
                        $url = xmlrpc_getPanelImage($hostname, $panels_list[0]['title'], $from, $to);
                        echo "<a href='".$url."'>1 month</a>";
                        echo " | ";
                        $from = time() - (3 * 31 * 24 * 60 * 60);
                        $to = time();
                        $url = xmlrpc_getPanelImage($hostname, $panels_list[0]['title'], $from, $to);
                        echo "<a href='".$url."'>3 months</a>";
                    echo "</td>";
                echo "</tr>";
            }
        echo "</tbody>";
    echo '</table>';
  ?>

<script type="text/javascript">
       jQuery( document ).ready(function() {
           //si besoin action jquery
        });
</script>
