<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * GLPI inventory tabs for a phone, displayed within the mobile module
 * (uses the mobile sidebar instead of the computers sidebar).
 *
 * Functionally identical to modules/glpi/glpi/tabs.php but keeping the
 * user inside the mobile module context.
 */

require_once("modules/glpi/includes/xmlrpc.php");
require("modules/mobile/mobile/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

global $conf;
$glpidisplayname = (!empty($conf['global']['glpidisplayname'])) ? htmlentities($conf['global']['glpidisplayname']) : "GLPI";

right_top_shortcuts_display();

if (!isset($_GET['hostname'])) { $_GET['hostname'] = $_GET['cn'] ?? ''; }
if (!isset($_GET['uuid']))     { $_GET['uuid']     = $_GET['objectUUID'] ?? ''; }
if (!isset($_GET['part']))     { $_GET['part']     = 'Summary'; }

$uuid     = isset($_GET['uuid'])     ? $_GET['uuid']              : '';
$hostname = isset($_GET['hostname']) ? clean_xss($_GET['hostname']) : '';

$uri = getGlpiMachineUri();
if ($uri) {
    $glpi_link = sprintf('<a href="%s" target="new">%s</a>', $uri . str_replace('UUID', '', clean_xss($uuid)), $glpidisplayname);
} else {
    $glpi_link = $glpidisplayname;
}

$p = new TabbedPageGenerator();
$p->setSideMenu($sidemenu);

$version = glpi_version();

$tabList = [
    'Summary'        => _T('Summary',        'glpi'),
    'Hardware'       => _T('Hardware',        'glpi'),
    'Connections'    => _T('Connections',     'glpi'),
    'Storage'        => _T('Storage',         'glpi'),
    'Network'        => _T('Network',         'glpi'),
    'Softwares'      => _T('Software',        'glpi'),
    'Administrative' => _T('Administrative',  'glpi'),
    'History'        => _T('History',         'glpi'),
    'Antivirus'      => _T('Antivirus',       'glpi'),
];

if (!preg_match('/^0\.84(.+)/', $version)) {
    $tabList['Registry'] = _T('Registry', 'glpi');
}

if (!xmlrpc_check_saas()) {
    $p->addTop(sprintf(_T("%s's inventory %s", "glpi"), $hostname, $glpi_link), "modules/glpi/glpi/header.php");
} else {
    $p->addTop(sprintf(_T("%s's inventory %s", "glpi"), $hostname, ''), "modules/glpi/glpi/header.php");
}

$i = 0;
foreach ($tabList as $tab => $str) {
    $p->addTab("tab$i", $str, "", "modules/glpi/glpi/view_part.php", ['hostname' => $hostname, 'uuid' => $uuid, 'part' => $tab]);
    $i++;
}

$p->display();

if (isset($uuid)) {
    $f = new ValidatingForm();
    print("<br><br>");
    $result['xls_path'] = getReport($uuid, $_SESSION['lang']);
    $link = new SpanElement(sprintf(
        '<br /><a class="btn btn-primary" href="%s">%s</a>&nbsp;&nbsp;',
        urlStrRedirect("base/computers/get_file", ['path' => $result['xls_path']]),
        _T("Get XLS Report", "glpi")
    ));
    $f->add($link);
    $f->pop();
    $f->display();
}
?>
