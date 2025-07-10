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
    height: auto !important;
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
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
  height: auto !important;
  line-height: normal !important;
  margin: 0 0 5px !important;
  padding: 0 !important;
  color: #999 !important;
  font-size: 9px !important;
}

#popup .total-count strong {
  font-weight: bold !important;
  font-size: 11px !important;
  color: #999 !important;
}

#popup .total-count a {
  margin-left: auto !important;
  font-size: 9px !important;
  color: #888 !important;
  text-decoration: underline !important;
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
  <span class="total-info">
    <?= _T('Total updates : ', 'update') ?>
    <strong><?= count($columns['package']) ?></strong>
  </span>
  <a href="https://github.com/medulla-tech/medulla/blob/master/README.md" target="_blank">
    <?= _T('For more details, see the README.', 'update') ?>
  </a>
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