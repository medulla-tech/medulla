<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxUpdateCreateGroup.php


require_once("modules/dyngroup/includes/dyngroup.php"); # for Group Class
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/updates/includes/html.inc.php");

$title = _T("Create a group", "updates");
$request = updatesGroupRequest();
$groupName = $request ? implode(" - ", array($request['tabLabel'], $request['categoryLabel'], date("Y-m-d H:i"))) : '';
$entity = updatesSelectedEntity();
$machines = array();
if (!hasCorrectAcl("base", "computers", "computersgroupcreator")) {
    $error = _T("You are not allowed to create groups.", "updates");
} elseif (!$entity && !empty($_GET['location'])) {
    $error = _T("Unknown entity.", "updates");
} else {
    list($machines, $error) = updatesGroupMachines($entity);
}
$count = count($machines);

if (isset($_POST['bconfirm'])) {
    verifyCSRFToken($_POST);
    $back = $request ? $request['back'] : updatesUpgradeUrl($entity, updatesUpgradeRequestTab());
    $group = new Group();
    if ($error !== null) {
        new NotifyWidgetFailure(htmlspecialchars($error));
    } elseif (!$group->create($groupName, false)) {
        new NotifyWidgetFailure(htmlspecialchars(_T("The group could not be created.", "updates")));
    } else {
        // miniAddMembers : addmembers_to_group bute sur les ecarts de casse UUID du cache dyngroup
        $added = $group->miniAddMembers($machines);
        if (!is_array($added) || empty($added[0])) {
            new NotifyWidgetFailure(htmlspecialchars(_T("The machines could not be added to the group.", "updates")));
        } else {
            $message = ($count === 1)
                ? updatesActionText(_T("Group \"%s\" created with 1 machine.", "updates"), $groupName)
                : updatesActionText(_T("Group \"%s\" created with %d machines.", "updates"), $groupName, $count);
            new NotifyWidgetSuccess($message);
            $back = urlStrRedirect("base/computers/display",
                                   array('id' => $group->getId(), 'gid' => $group->getId(), 'groupname' => $groupName));
        }
    }
    header("Location: " . $back);
    exit;
}

$f = new PopupForm($title);
if ($error === null) {
    $machinesText = ($count === 1) ? _T("1 machine", "updates") : sprintf(_T("%d machines", "updates"), $count);
    $what = $request['what'];
    $f->addText($entity
        ? updatesActionText(_T("Create a group with <b>%s</b> %s from entity <b>%s</b>?", "updates"),
                            $machinesText, $what, updatesEntityName($entity))
        : updatesActionText(_T("Create a group with <b>%s</b> %s?", "updates"), $machinesText, $what));
    $f->addText('<em>' . htmlspecialchars($groupName, ENT_QUOTES, 'UTF-8') . '</em>');
    $f->addValidateButtonWithValue("bconfirm", _T("Create", "updates"));
} else {
    $f->addText(htmlspecialchars($error));
}
$f->addCancelButton("bback");
$f->display();
?>
