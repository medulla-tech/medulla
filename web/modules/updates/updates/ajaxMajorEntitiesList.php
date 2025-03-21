<?php
/**
 * (c) 2022-2024 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require_once("modules/updates/includes/html.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

require_once("modules/updates/includes/xmlrpc.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);
$source  = (isset($_GET['$source']) ? $_GET['$source']: "");
if ($_GET['source'] == "xmppmaster" || $_GET['source'] == "glpi" ){

    if ($_GET['source'] == "xmppmaster" ){
        $p = new PageGenerator(_T("Manage Updates Major Lists", 'updates'));
        $p->display();
        $statglpiversion = xmlrpc_get_os_xmpp_update_major_stats();
    }else{
        $p = new PageGenerator(_T("Manage Updates Major Lists", 'updates'));
        $p->display();
        $statglpiversion=xmlrpc_get_os_update_major_stats();
    };

$complete_name_major  = array();
$comformite_name_major  = array();
$win10towin10_major = array();
$win10towin11_major = array();
$win11towin11_major = array();
$total_win=array();
$complRates=array();

$title = _T("update mach", "updates");
$texte_help = _T("%s machines in the entity \"%s\" can benefit from a major update.", "updates");
foreach ($statglpiversion['entity'] as  $index=>$datacolonne) {
    // on initialise le tableau
    $complete_name_major[]=$datacolonne['name'];
    $win10towin10_major[]=$datacolonne['W10to10'];
    $win10towin11_major[]=$datacolonne['W10to11'];
    $win11towin11_major[]=$datacolonne['W11to11'];
    $total_win[]=$datacolonne['count'];
    $nbupdate = $datacolonne['W10to10'] + $datacolonne['W10to11'] + $datacolonne['W11to11'];
    $formattedText_bar = sprintf("(%s)",$nbupdate);
    $formattedText_help = sprintf($texte_help, $nbupdate, $datacolonne['name']);
    $comformite_name_major[]=(string) new medulla_progressbar_static($datacolonne['Conformite'],
                                                                     $formattedText_bar,
                                                                     $formattedText_help  );
}
$count = count($complete_name_major);
$n = new OptimizedListInfos($complete_name_major, _T("Entity name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($comformite_name_major, _T("Conformite", "updates"));
$n->addExtraInfo($win10towin10_major, _T("major update W10->W10", "updates"));
$n->addExtraInfo($win10towin11_major, _T("major update W10->W11", "updates"));
$n->addExtraInfo($win11towin11_major, _T("major update W11->W11", "updates"));
$n->addExtraInfo($total_win, _T("total computer", "updates"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = $start;
$n->end = $count;
$n->display();
}else{
    echo "object inexistant";
}

?>

