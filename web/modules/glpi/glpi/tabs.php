<?php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 * (c) 2021-2022 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://siveo.net
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

require_once("modules/glpi/includes/xmlrpc.php");
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/pulse2/includes/utilities.php");

global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? htmlentities($conf['global']['glpidisplayname']) : "GLPI";

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn']; }
if (!isset($_GET['uuid'])) { $_GET['uuid'] = $_GET['objectUUID']; }
if (!isset($_GET['part'])) { $_GET['part'] = 'Summary'; }

$uuid = '';
$hostname = '';
if (isset($_GET['uuid'])) { $uuid = $_GET['uuid']; }
//clean_xss function is located in pulse2/includes/utilities.php
if (isset($_GET['hostname'])) { $hostname = clean_xss($_GET['hostname']); }

$uri = getGlpiMachineUri();
if ($uri) {
    $glpi_link = sprintf('<a href="%s" target="new">%s</a>', $uri.str_replace('UUID', '', clean_xss($uuid)), $glpidisplayname);
}
else {
    $glpi_link = $glpidisplayname;
}

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);
if (isset($_SESSION['pull_targets']) && in_array($uuid, $_SESSION['pull_targets'])) {
    if (hasCorrectAcl('base', 'computers', 'remove_from_pull')) {
        $remove_pull_id = uniqid();
        $_SESSION['remove_pull_id'] = $remove_pull_id;
        $p->setDescription(
            sprintf('%s <a class="btn btn-primary" href="%s">%s</a>',
                _T('This client has been registered in pull mode', 'glpi'),
                urlStrRedirect('base/computers/remove_from_pull', array('uuid' => clean_xss($uuid), 'remove_pull_id' => $remove_pull_id)),
                _T('Leave pull mode', 'glpi')
            )
        );
    }
    else {
        $p->setDescription(
            sprintf('%s', _T('This client has been registered in pull mode', 'glpi'))
        );
    }
}
$p->addTop(sprintf(_T("%s's inventory %s", "glpi"), $hostname, $glpi_link), "modules/glpi/glpi/header.php");

$i = 0;
// TODO get the list with trads from agent (conf file...)

$version = glpi_version();

$tabList = array(
    'Summary' => _T('Summary', "glpi"),
    'Hardware' => _T('Hardware', "glpi"),
    'Connections' => _t("Connections", "glpi"),
    'Storage' => _T('Storage', "glpi"),
    'Network' => _T('Network', "glpi"),
    'Softwares' => _T('Software', "glpi"),
    'Administrative' => _T('Administrative', "glpi"),
    'History' => _T('History', "glpi"),
    'Antivirus' => _T('Antivirus', "glpi"),
);

// Compatibility for glpi 8.4
if (!preg_match('/^0\.84(.+)/', $version))
    $tabList['Registry'] = _T('Registry', "glpi");


foreach ($tabList as $tab => $str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", array('hostname'=>$hostname, 'uuid'=>$uuid, 'part' => $tab));
    $i++;
}
$p->display();
if (isset ($uuid))
{
    $f = new ValidatingForm();
    print("<br><br>");
    $result['xls_path']=getReport($uuid,$_SESSION['lang']);
   $link = new SpanElement(sprintf('<br /><a class="btn btn-primary" href="%s">%s</a>&nbsp;&nbsp;',
     urlStrRedirect("base/computers/get_file", array('path' => $result['xls_path'])), _T("Get XLS Report", "glpi")));
    $f->add($link);
    $f->pop();
    $f->display();
}

?>
