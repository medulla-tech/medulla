<style>
.popup {
    width: 650px !important;
}
/* Hide meter and nav */
#popup p.listInfos,
#popup ul.navList {
  display: none !important;
}

/* Wrapper scrollable around the table */
#popup .listinfos-wrapper {
  max-height: 40vh;
  overflow-y: auto;
  margin-bottom: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  box-sizing: border-box;
}

#popup .listinfos-wrapper table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

#popup .listinfos-wrapper colgroup col:nth-child(1) { width: 25%; }
#popup .listinfos-wrapper colgroup col:nth-child(2) { width: 40%; }
#popup .listinfos-wrapper colgroup col:nth-child(3) { width: 20%; }
#popup .listinfos-wrapper colgroup col:nth-child(4) { width: 15%; }

#popup .listinfos-wrapper thead th {
  background: #f5f5f5;
  padding: 8px;
  text-align: left;
  font-weight: bold;
  border-bottom: 1px solid #ddd;
}

#popup .listinfos-wrapper tbody td {
  padding: 8px;
  vertical-align: middle;
  text-align: left;
  white-space: normal;
  overflow-wrap: break-word;
  border-top: 1px solid #ddd;
}

#popup .listinfos-wrapper tbody td:nth-child(4) {
  text-align: center;
}

#popup .total-count {
  display: flex;
  align-items: center;
  margin: 0 0 5px;
  color: #999;
  font-size: 9px;
}
#popup .total-count strong {
  font-weight: bold;
  font-size: 11px;
}
#popup .total-count a {
  margin-left: auto;
  font-size: 9px;
  color: #888;
  text-decoration: underline;
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
?>

<h1><?= _T('Available updates', 'medulla_server') ?></h1>
<div class="total-count">
  <span class="total-info">
    <?= _T('Total updates', 'medulla_server') ?> :
    <strong><?= count($rows) ?></strong>
  </span>
  <a href="https://github.com/medulla-tech/medulla/blob/master/README.md" target="_blank">
    <?= _T('For more details, see the README.', 'update') ?>
  </a>
</div>

<div class="listinfos-wrapper">
  <table>
    <colgroup>
      <col />
      <col />
      <col />
      <col />
    </colgroup>
    <thead>
      <tr>
        <th><?= _T('Package name',      'medulla_server') ?></th>
        <th><?= _T('Description',       'medulla_server') ?></th>
        <th><?= _T('Version',           'medulla_server') ?></th>
        <th><?= _T('Reboot required',   'medulla_server') ?></th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($rows as $row): ?>
        <tr>
          <td><?= htmlspecialchars($row[0]) ?></td>
          <td><?= htmlspecialchars($row[1] ?? '') ?></td>
          <td><?= htmlspecialchars($row[2] ?? '') ?></td>
          <td>
            <?= ($row[3] ? _T('Yes','medulla_server') : _T('No','medulla_server')) ?>
          </td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>