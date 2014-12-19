<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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

require_once("modules/update/includes/xmlrpc.inc.php");
require_once("modules/update/includes/utils.inc.php");

echo "<br/><br/>";

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

if (isset($_GET["start"]))
    $start = $_GET["start"];
else
    $start = 0;

$params = array(
    'min' => $start,
    'max' => $start + $maxperpage,
    'filters' => array()
);
if (isset($_GET["status"]))
    $params['filters']['status'] = $_GET["status"];

if (isset($_GET["os_class_id"]))
    $params['filters']['os_class_id'] = $_GET["os_class_id"];

if (isset($_GET["gid"])) {
    $params['gid'] = $_GET["gid"];
    print ("<div id=\"gid\" style=\"display:none;\">".$params['gid']."</div>");
}
if (isset($_GET["uuids"]))
    $params['uuids'] = $_GET["uuids"];

if (isset($_GET["filter"]) && $_GET["filter"]) {
   $params['like_filters']['title'] = $_GET["filter"];
   // to get all elements
   unset($params['max']);
}

extract(get_updates($params));

if (!$count) {
    print _T('No entry found', 'update');
    return;
}
//to disable pagination
if (isset($_GET["filter"]) && $_GET["filter"]) {
   $maxperpage=$count;
   $_REQUEST['maxperpage']=$count;
}
//  Listinfo params
$listinfoParams = array();
$checkboxes = array();
foreach ($data as $row) {
    if (isset($_GET["gid"])) {
        $listinfoParams[] = array('id' => $row['id'],'gid' => $_GET["gid"]);
    } else {
        $listinfoParams[] = array('id' => $row['id']);
    }
    $checkboxes[] = '<input type="checkbox" name="selected_updates[]" value="' . $row['id'] . '">';
}

$check_all = '<input type="checkbox" id="check_all" />';

$cols = listInfoFriendly($data);

// Update types strings
$cols['type_str'] = array_map('getUpdateTypeLabel', $cols['type_id']);
// Creating installed/total col
$cols['targets'] = array();
for ($i = 0; $i < count($cols['total_targets']); $i++){
    $cols['targets'][] = $cols['total_installed'][$i] . ' / ' . $cols['total_targets'][$i];
}

// Printing selected updates form
print '<form id="sel_updates_form">';

$n = new OptimizedListInfos($checkboxes, $check_all, '', '10px');
$n->first_elt_padding = '0';
$n->addExtraInfo($cols['title'], _T("Update title", "update"));
$n->addExtraInfo($cols['type_str'], _T("Type", "update"));
$n->addExtraInfo($cols['targets'], _T("Installed count", "update"));

$n->addActionItem(new ActionPopupItem(_T("Enable", "update"), "enableUpdate", "enable", "id", "update", "update"));
$n->addActionItem(new ActionPopupItem(_T("Disable", "update"), "disableUpdate", "disable", "id", "update", "update"));
if (isset($_POST['gid'])){
    $n->add(new HiddenTpl("gid"), array("value" => $_GET['gid'], "hide" => True));
}
$n->setParamInfo($listinfoParams);
$n->setItemCount($count);

$n->setNavBar(new AjaxNavBar($count, $status,"updateSearchParam",$maxperpage));
$n->start = 0;
$n->end = $maxperpage;
$n->disableFirstColumnActionLink();

$n->display();

// End selected updates form
print '</form>';

?>
<input id="btnEnableUpdates" type="button" value="<?php print _T('Enable selected updates', 'update'); ?>" class="btnPrimary">
<input id="btnDisableUpdates" type="button" value="<?php print _T('Disable selected updates', 'update'); ?>" class="btnPrimary">

<script type="text/javascript">
// Enable Updates button
jQuery('#btnEnableUpdates').click(function(){

    jQuery.ajax({
        url: '<?php print urlStrRedirect("update/update/enableUpdate"); ?>',
        type: 'POST',
        data: jQuery('#sel_updates_form').serialize(),
        success: function(result){
            pushSearch();
        }
    });

});


// Disable Updates button
jQuery('#btnDisableUpdates').click(function(){

    jQuery.ajax({
        url: '<?php print urlStrRedirect("update/update/disableUpdate"); ?>',
        type: 'POST',
        data: jQuery('#sel_updates_form').serialize(),
        success: function(result){
            pushSearch();
        }
    });

});

// Check all checkbox
jQuery('#check_all').click(function(){
    jQuery(this).parents('table:first').find('input[type=checkbox]').prop('checked', jQuery(this).is(':checked'));
});


</script>

