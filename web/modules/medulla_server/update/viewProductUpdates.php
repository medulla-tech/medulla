<style>
/* Hide meter and nav */
#popup p.listInfos,
#popup ul.navList {
    display: none !important;
}

/* Scrollable table and frame */
#popup .listinfos {
    display: block !important;
    max-height: 40vh !important;
    overflow-y: auto !important;
    width: 100% !important;
    margin-bottom: 8px !important;
    border: 1px solid #ccc !important;
    border-radius: 4px !important;
    background-color: #fff !important;
    box-sizing: border-box;
}

#popup .listinfos thead td,
#popup .listinfos tbody td {
    padding: 8px !important;
    vertical-align: middle !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

#popup .listinfos thead td span {
    padding: 0 !important;
    margin: 0 !important;
    display: block;
    width: 100%;
}

/* Center the 4ᵉ column be reboot required */
#popup .listinfos tbody td:nth-child(4) {
    text-align: center !important;
}

#popup .total-count {
    color: #999;
    font-size: 9px;
    height: 22px;
    line-height: 22px;
    margin: 0px  0 5px  0;
    padding: 0;
}

#popup .total-count strong {
    font-weight: bold;
    font-size: 11px;
    color: #999;
    margin-left: 4px;
}
</style>

<?php
require_once("includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");

$updates_raw = isset($_GET['updates'])
    ? json_decode(base64_decode($_GET['updates']))
    : getProductUpdates();

if (
    empty($updates_raw->data->header) ||
    empty($updates_raw->data->content) ||
    !is_array($updates_raw->data->header) ||
    !is_array($updates_raw->data->content)
) {
    echo "<p style='color:red; font-weight:bold'>"
       . _T('No updates data available', 'update')
       . "</p>";
    return;
}

$headers = $updates_raw->data->header;
$rows    = $updates_raw->data->content;

$columns = array_fill_keys($headers, []);
foreach ($rows as $row) {
    foreach ($headers as $i => $col) {
        $columns[$col][] = $row[$i] ?? '';
    }
}
?>

<h1><?= _T('Available updates', 'update') ?></h1>
<div class="total-count">
  <?= _T('Total updates : ', 'update') ?> <strong><?= count($columns['package']) ?></strong>
</div>

<?php
$n = new OptimizedListInfos($columns['package'], _T("Package name", "update"));

if (isset($columns['description'])) {
    $n->addExtraInfo($columns['description'], _T("Description", "update"));
}
if (isset($columns['version'])) {
    $n->addExtraInfo($columns['version'], _T("Version", "update"));
}
if (isset($columns['needs_reboot'])) {
    $n->addExtraInfo(
        array_map(fn($val) => $val ? _("Yes") : _("No"), $columns['needs_reboot']),
        _T("Reboot required", "update")
    );
}

$n->setItemCount(count($columns['package']));
$n->setNavBar(new AjaxNavBar($n->getItemCount(), ""));
$n->start = 0;
$n->end = 50;

$n->display();
?>