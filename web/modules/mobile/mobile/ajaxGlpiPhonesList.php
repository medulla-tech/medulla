<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 * GLPI Phones list for the mobile module.
 *
 * Queries glpi_phones (entity-scoped via the user's session entities) and
 * displays a clean phone-focused list. PC-specific actions (VNC, imaging,
 * software deployment, XMPP console) are intentionally omitted.
 */

require_once("modules/glpi/includes/xmlrpc.php");

global $config;

$location = isset($_GET['location']) ? $_GET['location'] : "";
$filter   = isset($_GET['filter'])   ? $_GET['filter']   : "";
$field    = isset($_GET['field'])    ? $_GET['field']     : "";
$contains = isset($_GET['contains']) ? $_GET['contains']  : "";

$start      = isset($_GET['start'])      ? intval($_GET['start'])      : 0;
$maxperpage = isset($_GET['maxperpage']) ? intval($_GET['maxperpage'])  : $config['maxperpage'];
$end        = isset($_GET['end'])        ? intval($_GET['end'])         : $maxperpage - 1;

$ctx = [
    'location'    => $location,
    'filter'      => $filter,
    'field'       => $field,
    'contains'    => $contains,
    'start'       => $start,
    'end'         => $end,
    'maxperpage'  => $maxperpage,
];

$machines = xmlrpc_get_devices_list($start, $maxperpage, $ctx);
$count    = $machines["count"];
$datas    = $machines["data"];
$xmppdatas = isset($machines['xmppdata']) ? $machines['xmppdata'] : [];

// Client-side filter by device name when a search string is given
if (!empty($filter) && isset($datas['name'])) {
    $filtered_indices = [];
    foreach ($datas['name'] as $idx => $name) {
        $deviceName = $name ?? (isset($datas['cn'][$idx]) ? $datas['cn'][$idx] : '');
        if (stripos($deviceName, $filter) !== false) {
            $filtered_indices[] = $idx;
        }
    }
    foreach ($datas as $key => $values) {
        if (is_array($values)) {
            $datas[$key] = array_values(array_intersect_key($values, array_flip($filtered_indices)));
        }
    }
    $count = count($filtered_indices);
}

// Actions: GLPI inventory tab within the mobile module (no VNC, imaging, deployment, console)
$glpiAction   = new ActionItem(_T("GLPI Inventory", "mobile"), "glpiPhoneTabs", "inventory", "inventory", "mobile", "mobile");
$inventAction = new ActionItem(_T("Inventory",      "mobile"), "glpiPhoneTabs", "inventory", "inventory", "mobile", "mobile");

$actionInventory = [];
$params          = [];
$cn              = [];
$raw             = 0;

foreach ($datas['uuid'] as $uuid) {

    $display_name = isset($datas['name'][$raw])
        ? $datas['name'][$raw]
        : (isset($datas['cn'][$raw]) ? $datas['cn'][$raw] : "");

    // Tooltip with XMPP data when available
    if (isset($xmppdatas['UUID' . $uuid])) {
        $xd = $xmppdatas['UUID' . $uuid];
        $cnstr  = '<span title="';
        $cnstr .= "jid : \t "          . ($xd['jid'] ?? '')          . "\n";
        $cnstr .= "ip_xmpp : \t "      . ($xd['ip_xmpp'] ?? '')      . "\n";
        $cnstr .= "ippublic : \t "     . ($xd['ippublic'] ?? '')      . "\n";
        $cnstr .= "subnetxmpp : \t "   . ($xd['subnetxmpp'] ?? '')    . "\n";
        $cnstr .= '">' . $display_name . '</span>';
        $cn[] = $cnstr;
    } else {
        $cn[] = $display_name;
    }

    // Format last_update (returned as array of date components from Python)
    if (isset($datas['last_update'][$raw]) && is_array($datas['last_update'][$raw])) {
        $lu = $datas['last_update'][$raw];
        $y  = $lu[0] ?? 0; $mo = $lu[1] ?? 0; $d  = $lu[2] ?? 0;
        $h  = $lu[3] ?? 0; $mi = $lu[4] ?? 0; $s  = $lu[5] ?? 0;
        $datas['last_update'][$raw] = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $y, $mo, $d, $h, $mi, $s);
    }

    $type_val  = (isset($datas['type'][$raw])  && $datas['type'][$raw]  !== "") ? $datas['type'][$raw]  : "";
    $model_val = (isset($datas['model'][$raw]) && $datas['model'][$raw] !== "") ? $datas['model'][$raw] : "";

    $params[] = [
        'id'               => isset($xmppdatas['UUID' . $uuid]['id']) ? $xmppdatas['UUID' . $uuid]['id'] : null,
        'objectUUID'       => 'UUID' . ($datas['uuid'][$raw] ?? ''),
        'UUID'             => $datas['uuid'][$raw] ?? '',
        'cn'               => $display_name,
        'name'             => $display_name,
        'type'             => $type_val,
        'model'            => $model_val,
        'entity'           => isset($datas['entity'][$raw])    ? $datas['entity'][$raw]    : '',
        'entityid'         => isset($datas['entityid'][$raw])  ? $datas['entityid'][$raw]  : '',
        'alternate_username' => isset($datas['alternate_username'][$raw]) ? $datas['alternate_username'][$raw] : '',
        'from'             => 'glpiPhonesList',
    ];

    // Inventory action
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $actionInventory[] = $inventAction;
    } else {
        $actionInventory[] = $glpiAction;
    }

    // Wrap values for click-to-search
    foreach ($datas as $fld => $table) {
        if ($fld !== 'name') {
            $datas[$fld][$raw] = '<span class="selectable">' . ($datas[$fld][$raw] ?? '') . '</span>';
        }
    }

    $raw++;
}

// Safe CSS IDs
$ids       = [];
$name_list = isset($datas['name']) ? $datas['name'] : (isset($datas['cn']) ? $datas['cn'] : []);
foreach ($name_list as $cn_machine) {
    $ids[] = 'p_' . preg_replace('/[^a-zA-Z0-9_\-]/', '_', $cn_machine);
}

// Build prepared value arrays
$type_arr       = [];
$model_arr      = [];
$lastupdate_arr = [];
$altuser_arr    = [];
for ($i = 0; $i < count($params); $i++) {
    $type_arr[]       = $params[$i]['type']               ?? '';
    $model_arr[]      = $params[$i]['model']              ?? '';
    $lastupdate_arr[] = isset($datas['last_update'][$i])  ? $datas['last_update'][$i] : '';
    $altuser_arr[]    = $params[$i]['alternate_username']  ?? '';
}

// --- Display ---
$n = new OptimizedListInfos($cn, _T("Device Name", "mobile"));
$n->setcssIds($ids);
$n->setParamInfo($params);

if (array_key_exists("manufacturer", $datas)) {
    $n->addExtraInfo($datas["manufacturer"], _T("Manufacturer", "mobile"));
}
$n->addExtraInfo($model_arr,      _T("Model",              "mobile"));
$n->addExtraInfo($type_arr,       _T("Type",               "mobile"));
$n->addExtraInfo($altuser_arr,    _T("Contact",            "mobile"));
$n->addExtraInfo($lastupdate_arr, _T("Last Update",        "mobile"));
if (array_key_exists("entity", $datas)) {
    $n->addExtraInfo($datas["entity"], _T("Entity", "mobile"));
}
if (array_key_exists("location", $datas)) {
    $n->addExtraInfo($datas["location"], _T("Localization", "mobile"));
}

$n->addActionItemArray($actionInventory);

$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $location));
$n->start = 0;
$n->end   = $count;
$n->display();
?>

<style>
.selectable { cursor: pointer; }
</style>
<script type="text/javascript">
jQuery(".selectable").on("click", function () {
    jQuery("#param").val(jQuery(this).text());
    pushSearch();
});
</script>
