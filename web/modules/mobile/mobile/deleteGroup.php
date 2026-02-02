<?php
require_once("modules/mobile/includes/xmlrpc.php");

$group_id = isset($_GET['group_id']) ? $_GET['group_id'] : '';
$group_name = isset($_GET['group_name']) ? $_GET['group_name'] : '';

if (empty($group_id)) {
    new NotifyWidgetFailure(_T("Group ID is missing", "mobile"));
    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
}

if (isset($_POST['bdelete'])) {
    // Call the delete function
    $result = xmlrpc_delete_hmdm_group_by_id($group_id);

    if ($result && ((is_array($result) && isset($result['status']) && $result['status'] === 'OK') || $result === true)) {
        new NotifyWidgetSuccess(sprintf(_T("Group '%s' successfully deleted", "mobile"), $group_name));
    } else {
        $error_msg = is_array($result) && isset($result['message']) ? $result['message'] : _T('Unknown error occurred', 'mobile');
        new NotifyWidgetFailure(sprintf(_T("Failed to delete group: %s", "mobile"), $error_msg));
    }

    header("Location: " . urlStrRedirect("mobile/mobile/groups"));
    exit;
} else {
    $f = new PopupForm(_T("Delete Group", "mobile"));
    $f->addText(sprintf(_T("Are you sure you want to delete the group <b>%s</b>.", "mobile"), htmlspecialchars($group_name)));
    $hidden = new HiddenTpl("group_id");
    $f->add($hidden, array("value" => $group_id, "hide" => true));
    $hidden_name = new HiddenTpl("group_name");
    $f->add($hidden_name, array("value" => $group_name, "hide" => true));
    $f->addValidateButton("bdelete");
    $f->addCancelButton("bback");
    $f->display();
}

?>
