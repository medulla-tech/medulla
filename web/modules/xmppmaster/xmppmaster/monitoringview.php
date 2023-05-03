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
iframe{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
    }
</style>
<?
    require("modules/base/computers/localSidebar.php");
    require("graph/navbar.inc.php");
    require_once("modules/xmppmaster/includes/xmlrpc.php");

    require_once("modules/medulla_server/includes/utilities.php"); # for quickGet method
    require_once("modules/dyngroup/includes/utilities.php");

    global $conf;
    $maxperpage = $conf["global"]["maxperpage"];
    $filter= isset($_GET["filter"]) ? $_GET["filter"] : "";
    if (isset($_GET["start"])) {
        $start = $_GET["start"];
    } else {
        $start = 0;
    }

    $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
    $jid  = isset($_GET['jid']) ? $_GET['jid'] : ( isset($_POST['jid']) ? $_POST['jid'] : "");
    $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : ($jid == '' ?  xmlrpc_getjidMachinefromuuid( $uuid ) : $jid);

    $hostname = $_GET['cn'];

    $p = new PageGenerator(_T("Monitoring for", 'xmppmaster')." $hostname");

    $p->setSideMenu($sidemenu);
    $p->display();

    ## il faut refaire la fonction xmlrpc_getPanelsForMachine pour permettre la navigation ($hostname, $filter, $start, $start + $maxperpage);
    // la function doit renvoyer [count le nbelement,$panels_list]
    $panels_list = xmlrpc_getPanelsForMachine(strtolower($hostname));

    $count = count($panels_list); // nombre total de d'element

    /*
    $debut_de_la_journee = mktime(0, 0, 0, date("m"),date("j"), date("Y"));
    $debut_du_mois = mktime(0, 0, 0, date("m"), 1, date("Y"));
    $debut_le_debut_3_mois = mktime(0, 0, 0, date("m")-3, 1 , date("Y"));
    // timestamp debut de la semaine
    $jour_actuel = date('d'); // On récupère le numéro du jour
    $numero_jour = date('w'); // On récupère le numéro du jour de la semaine (0 = dimanche)
    $date_lundi = $jour_actuel - $numero_jour + 1; // On fait le calcul
    // Lundi est égale à la date du jour - son numéro de jour + 1
    $debut_de_la_semaine = mktime(0,0,0,date('m'),$date_lundi,date('Y'));
    $array_timefrom=[ $debut_de_la_journee,
                      $debut_de_la_semaine,
                      $debut_du_mois,
                      $debut_le_debut_3_mois];
    */
    $to = time();
    $array_timefrom=[ $to - (24 * 60 * 60),          // day 24h
                      $to - (7 * 24 * 60 * 60),      // week 7 jour
                      $to - (31 * 24 * 60 * 60),     // mois considere 31 jour.
                      $to - (3 * 31 * 24 * 60 * 60)]; // considere 63 jour
    $oneyear = $to - (60 * 60 * 24 * 365);

    $params= array();
    $array_col_Monitoring_item = array();
    $array_col_lastvalue = array();
    $array_col_historyaction = array();
    $arraytitle=[array(_T("Graph for one day",      "xmppmaster"),_T("1 day",    "xmppmaster")),
                 array(_T("Graph for one week",     "xmppmaster"),_T("1 week",   "xmppmaster")),
                 array(_T("Graph for one month",    "xmppmaster"),_T("1 month",  "xmppmaster")),
                 array(_T("Graph for three months", "xmppmaster"),_T("3 months", "xmppmaster"))];


    foreach($panels_list as $val){
        $array_col_Monitoring_item[]= $val['title'];

        switch($val['title']) {
                case 'Online-Offline Status':
                    $array_col_lastvalue[]  = (xmlrpc_getLastOnlineStatus($machine) == 1 ) ? "Online" : "Offline";
                    break;
                default:
                    $array_col_lastvalue[]  = "not defined";
        }

        $arrayurl = array();
        $arrayurlpage = array();
        foreach($array_timefrom as $index => $from){
            $url = xmlrpc_getPanelImage(strtolower($hostname), $val['title'], $from, $to);
            $arrayurl[]="<a class='showgraph' title='".
                        $arraytitle[$index][0].
                        "' href='".$url."'>".
                        $arraytitle[$index][1].
                        "</a>";
        }
        $urlpage = xmlrpc_getPanelGraph(strtolower($hostname), $val['title'], $oneyear, $to);
        $arrayurl[]="<a class='showgraph1' title='".
                        _T("Panel Graph for one year","xmppmaster").
                        "' href='".$urlpage."'>".
                        _T("custom","xmppmaster").
                        "</a>";
        $array_col_historyaction[] = implode(" | ", $arrayurl);
    }
    echo '<div id="dialog"></div>';
    echo '<div id="dialog1"></div>';
    // Display the list
    $n = new OptimizedListInfos($array_col_Monitoring_item, _T("Monitoring item", "xmppmaster"));
    $n->disableFirstColumnActionLink();
    $n->addExtraInfo($array_col_lastvalue, _T("Last value", "xmppmaster"));
    $n->addExtraInfo($array_col_historyaction, _T("History", "xmppmaster"));
    //navigation et filter
    $n->setItemCount($count);
    $n->setNavBar(new AjaxNavBar($count, $filter));
    //addition parameters general les parametre pour les action. pas actions ici.
    //$n->setParamInfo($params);
    $n->start = 0;
    $n->end = $count;

    print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent
    $n->display();

  ?>

<script type="text/javascript">
jQuery( document ).ready(function() {

    jQuery(function(){
        //modal window start
        jQuery(".showgraph").unbind('click');
        jQuery(".showgraph").bind('click',function(){
                showDialog();
                var titletext=jQuery(this).attr("title");
                var openpage=jQuery(this).attr("href");
                jQuery("#dialog").dialog( "option", "title", titletext );
                jQuery("#dialog").dialog( "option", "resizable", false );
        //  add bouton
        //         jQuery("#dialog").dialog( "option", "buttons", {
        //             "Close": function() {
        //                 jQuery(this).dialog("close");
        //                // jQuery(this).dialog("destroy");
        //             }
        //         });
                //jQuery("#dialog").load(openpage);
                jQuery("#dialog").html(jQuery("<img>").attr("src", openpage));
                return false;
            });
    });
    //modal window end


    jQuery(function(){
        //modal window start
        jQuery(".showgraph1").unbind('click');
        jQuery(".showgraph1").bind('click',function(){
                showDialog1();
                var titletext=jQuery(this).attr("title");
                var openpage=jQuery(this).attr("href");
                jQuery("#dialog1").dialog( "option", "title", titletext );
                jQuery("#dialog1").dialog( "option", "resizable", true );
                jQuery("#dialog1").html(jQuery("<iframe>").attr("src", openpage));
                return false;
            });
    });


    //Modal Window Initiation start
    function showDialog(){
        jQuery("#dialog").dialog({
            autoOpen: false,
            height: 450,
            width: 835,
            modal: true
        });
        jQuery("#dialog").dialog("open");
    }
    //Modal Window Initiation start
    function showDialog1(){
        jQuery("#dialog1").dialog({
            autoOpen: false,
            height: 650,
            width: 1000,
            modal: true
        });
        jQuery("#dialog1").dialog("open");
    }
});

</script>
