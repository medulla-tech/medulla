<style>
    p.listinfos,
    table.listinfos {
        width: 100% !important;
    }

    .listinfos th,
    .listinfos td {
        padding: 8px !important;
        vertical-align: middle;
    }

    .listinfos thead th:first-child span {
        padding-left: 0 !important;
    }

    .listinfos th:nth-child(4),
    .listinfos td:nth-child(4) {
        text-align: center !important;
        width: 120px;
    }

    .listinfos thead th:nth-child(4) span {
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 0 !important;
        margin: 0 !important;
    }
    .listinfos thead tr td:first-child span {
        padding-left: 0 !important;
        margin: 0 !important;
        display: inline-block;
        text-align: left;
    }
</style>
<?php
require_once("includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

$updates_raw = (isset($_GET['updates'])) ? json_decode(base64_decode($_GET['updates'])) : getProductUpdates();
?>
<h1><?= _T('Available updates', 'update') ?></h1>
<?php
if (
    !isset($updates_raw->data->header) ||
    !isset($updates_raw->data->content) ||
    !is_array($updates_raw->data->header) ||
    !is_array($updates_raw->data->content)
) {
    echo "<p style='color:red; font-weight:bold'>" . _T('No updates data available', 'update') . "</p>";
    return;
}

$headers = $updates_raw->data->header;
$rows = $updates_raw->data->content;

$columns = array_fill_keys($headers, []);
foreach ($rows as $row) {
    foreach ($headers as $i => $col) {
        $columns[$col][] = $row[$i] ?? '';
    }
}

$n = new OptimizedListInfos($columns['package'], _T("Package name", "update"));
$n->disableFirstColumnActionLink();
$n->setCssClass("updates-table");

if (isset($columns['description'])) {
    $n->addExtraInfo($columns['description'], _T("Description", "update"));
}

if (isset($columns['version'])) {
    $n->addExtraInfo($columns['version'], _T("Version", "update"));
}

if (isset($columns['needs_reboot'])) {
    $n->addExtraInfo(
        array_map(fn($val) => $val ? _("Yes") : _("No"), $columns['needs_reboot']),
        _T("Reboot", "update")
    );
}

$n->setItemCount(count($columns['package']));
$n->setNavBar(new AjaxNavBar($n->getItemCount(), ""));
$n->start = 0;
$n->end = 50;

$n->display();
?>