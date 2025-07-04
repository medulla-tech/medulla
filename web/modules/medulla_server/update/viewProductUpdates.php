<style>
#__popup_container {
    display: flex;
    justify-content: center;
    flex-direction: column;
    max-width: 100%;
    overflow-x: auto;
}

#popup {
  max-height: 90vh;
  max-width: 90vw;
  min-width: 45vw;
  overflow: auto;
  padding: 10px;
  box-sizing: border-box;
}

table.listinfos {
    margin: 0 auto;
    width: 100%;
    margin-bottom: 5px;
}

table.listinfos td,
table.listinfos th {
    white-space: normal;
    word-break: break-word;
}

table.listinfos span {
    padding-left: 0 !important;
}

table.listinfos tbody td:nth-child(4) {
    text-align: center;
}
</style>
<?php

require_once("includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

print "<h1>"._T('Available updates','update')."</h1>";

$updates_raw = (isset($_GET['updates'])) ? json_decode(base64_decode($_GET['updates']), true) : getProductUpdates();

if (!isset($updates_raw['data']['content']) || !isset($updates_raw['data']['header'])) {
    echo "<p style='color:red; font-weight:bold'>"._T('No updates data available', 'update')."</p>";
    return;
}

$header = $updates_raw['data']['header'];
$content = $updates_raw['data']['content'];

$pkg_names = [];
$description = [];
$versions = [];
$reboots = [];
$urls = [];

foreach ($content as $line) {
    $pkg_names[] = $line[1];
    $description[] = $line[0];
    $versions[] = $line[2];
    $reboots[] = $line[4] ? '<span style="color:red">Yes</span>' : 'No';
    $urls[] = $line[6] ? htmlspecialchars($line[6]) : '-';
}

$n = new OptimizedListInfos($pkg_names, _T("Package name", "update"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($description, _T("Description", "update"));
$n->addExtraInfo($versions, _T("Version", "update"));
$n->addExtraInfo($reboots, _T("Reboot required", "update"));

$n->setItemCount(count($pkg_names));

$nav = new AjaxNavBar(count($pkg_names), "");
$n->setNavBar($nav);

$n->display();
