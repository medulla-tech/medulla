<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * file: admin/inventoryEntityRules.php
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");

$safe = fn($v) => htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8');
$login = (string)($_SESSION['login'] ?? '');
$isRoot = (strcasecmp($login, 'root') === 0);

$page = new PageGenerator(_T("Global Inventory Rules", "admin"));
$page->setSideMenu($sidemenu);
$page->display();

if (!$isRoot) {
    new NotifyWidgetFailure(_T("Access denied: root account required.", "admin"));
    return;
}

if (isset($_POST['save_rule'])) {
    $rule = [
        'id' => (int)($_POST['rule_id'] ?? 0),
        'enabled' => isset($_POST['enabled']) ? 1 : 0,
        'rule_name' => trim((string)($_POST['rule_name'] ?? '')),
        'tag_name' => trim((string)($_POST['tag_name'] ?? 'TAG')),
        'tag_value' => trim((string)($_POST['tag_value'] ?? '')),
        'entity_id' => (int)($_POST['entity_id'] ?? 0),
        'priority' => (int)($_POST['priority'] ?? 100),
        'stop_on_match' => 1,
        'comment' => trim((string)($_POST['comment'] ?? '')),
        'updated_by' => 'root',
        'created_by' => 'root',
    ];

    $res = xmlrpc_save_inventory_entity_rule($login, $rule);
    if (is_array($res) && !empty($res['ok'])) {
        new NotifyWidgetSuccess(_T("Rule saved.", "admin"));
    } else {
        $err = is_array($res) ? (string)($res['error'] ?? _T("Unknown error", "admin")) : _T("Unknown error", "admin");
        new NotifyWidgetFailure(_T("Rule save failed:", "admin") . ' ' . $safe($err));
    }

    header('Location: ' . urlStrRedirect('admin/admin/inventoryEntityRules'));
    exit;
}

if (isset($_POST['toggle_rule'])) {
    $ruleId = (int)($_POST['rule_id'] ?? 0);
    $enabled = (int)($_POST['enabled'] ?? 0);
    $res = xmlrpc_set_inventory_entity_rule_enabled($login, $ruleId, $enabled);

    if (is_array($res) && !empty($res['ok'])) {
        new NotifyWidgetSuccess(_T("Rule status updated.", "admin"));
    } else {
        $err = is_array($res) ? (string)($res['error'] ?? _T("Unknown error", "admin")) : _T("Unknown error", "admin");
        new NotifyWidgetFailure(_T("Rule status update failed:", "admin") . ' ' . $safe($err));
    }

    header('Location: ' . urlStrRedirect('admin/admin/inventoryEntityRules'));
    exit;
}

if (isset($_POST['delete_rule'])) {
    $ruleId = (int)($_POST['rule_id'] ?? 0);
    $res = xmlrpc_delete_inventory_entity_rule($login, $ruleId);

    if (is_array($res) && !empty($res['ok'])) {
        new NotifyWidgetSuccess(_T("Rule deleted.", "admin"));
    } else {
        $err = is_array($res) ? (string)($res['error'] ?? _T("Unknown error", "admin")) : _T("Unknown error", "admin");
        new NotifyWidgetFailure(_T("Rule deletion failed:", "admin") . ' ' . $safe($err));
    }

    header('Location: ' . urlStrRedirect('admin/admin/inventoryEntityRules'));
    exit;
}

$params = $_GET;
unset($params['module']);
unset($params['submod']);
unset($params['action']);

$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxInventoryEntityRules"), "container", $params);
$ajax->display();
$ajax->displayDivToUpdate();
