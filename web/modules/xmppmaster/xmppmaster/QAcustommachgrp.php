<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
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
 * file: QAcustommachgrp.php
 */
require("modules/base/computers/localSidebar.php");
// require("modules/xmppmaster/xmppmaster/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

include_once('modules/medulla_server/includes/menu_actionaudit.php');
?>
<style type='text/css'>
.qa-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.command-section {
    margin-bottom: 30px;
}

.section-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #555;
}

.command-box {
    background: #f5f5f5;
    color: #333;
    padding: 15px;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
    border-left: 4px solid #4CAF50;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.terminal-section {
    margin-bottom: 30px;
}

.terminal-output {
    background: #1e1e1e;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.terminal-output pre {
    margin: 0;
    padding: 0;
    color: #d4d4d4;
    background: #1e1e1e;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
    line-height: 1.6;
    white-space: pre;
    overflow-wrap: normal;
    overflow-x: auto;
    max-height: 600px;
    overflow-y: auto;
}

.terminal-output pre::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

.terminal-output pre::-webkit-scrollbar-track {
    background: #2d2d2d;
    border-radius: 4px;
}

.terminal-output pre::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 4px;
}

.terminal-output pre::-webkit-scrollbar-thumb:hover {
    background: #777;
}

.log-section {
    margin-bottom: 30px;
}

.log-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-radius: 4px;
    overflow: hidden;
}

.log-table thead tr {
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
}

.log-table th {
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    color: #495057;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.log-table tbody tr {
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
}

.log-table tbody tr:last-child {
    border-bottom: none;
}

.log-table tbody tr:hover {
    background: #f8f9fa;
}

.log-table td {
    padding: 12px 15px;
    font-size: 13px;
    color: #333;
}

.log-type-badge {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 10px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.back-button-container {
    margin-top: 40px;
    text-align: center;
}
</style>

<?php
// Retrieve machine information
if($_GET['uuid'] != '') {
    $machinelist = getRestrictedComputersList(0, -1, array('uuid' => $_GET['uuid']), false);
    $machine = $machinelist[$_GET['uuid']][1];
    $namemachine = $machine['cn'][0];
    $usermachine = $machine['user'][0];
} elseif(isset($_GET['jid']) && $_GET['jid'] != "") {
    $xmppmachine = xmlrpc_getMachinefromjid(htmlentities($_GET['jid']));
    $namemachine = $xmppmachine["hostname"];
    $usermachine = "";
} else {
    $namemachine = _T("Undefined", "xmppmaster");
    $usermachine = _T("Undefined", "xmppmaster");
}

$p = new PageGenerator(_T("Quick action on machine", 'xmppmaster')." : $namemachine");
$p->setSideMenu($sidemenu);
$p->display();

$custom_command = xmlrpc_getCommand_qa_by_cmdid($_GET['cmd_id']);
$startdate = $custom_command['command_start'];

$result = "";
$listmessage = array();

if($_GET['uuid'] != '') {
    $resultAQformachine = xmlrpc_getQAforMachine($_GET['cmd_id'], $_GET['uuid']);
} elseif(isset($_GET['jid']) && $_GET['jid'] != "") {
    $resultAQformachine = xmlrpc_getQAforMachineByJid($_GET['cmd_id'], $_GET['jid']);
} else {
    $resultAQformachine = [];
}

if (safeCount($resultAQformachine) != 0) {
    foreach($resultAQformachine as $message) {
        if ($message[3] == "result") {
            $rawResult = $message[4];

            if (is_object($rawResult) && isset($rawResult->scalar)) {
                $rawResult = $rawResult->scalar;
            }
            $rawResult = (string)$rawResult;
            $decoded = base64_decode($rawResult, true);
            if ($decoded !== false) {
                $result = $decoded;
            } else {
                $result = $rawResult;
            }
        } else {
            $messageContent = $message[4];
            if (is_object($messageContent) && isset($messageContent->scalar)) {
                $message[4] = $messageContent->scalar;
            }
            $listmessage[] = $message;
        }
    }
}

// Normalize newlines
if ($result != "") {
    $result = str_replace("\r\n", "\n", $result);
    $result = str_replace("\r", "\n", $result);
}
?>

<div class="qa-container">
    <div class="command-section">
        <div class="section-title"><?php echo _T("Command:", "xmppmaster"); ?></div>
        <div class="command-box"><?php echo htmlspecialchars($custom_command['command_action']); ?></div>
    </div>

    <?php if (safeCount($listmessage) != 0): ?>
    <div class="log-section">
        <div class="section-title"><?php echo _T("Execution Log:", "xmppmaster"); ?></div>
        <table class="log-table">
            <thead>
                <tr>
                    <th><?php echo _T("Date", "xmppmaster"); ?></th>
                    <th><?php echo _T("Type", "xmppmaster"); ?></th>
                    <th><?php echo _T("Message", "xmppmaster"); ?></th>
                </tr>
            </thead>
            <tbody>
                <?php foreach($listmessage as $message): ?>
                <tr>
                    <td><?php echo htmlspecialchars($message[1]); ?></td>
                    <td><span class="log-type-badge"><?php echo htmlspecialchars($message[3]); ?></span></td>
                    <td class="text-monospace"><?php echo htmlspecialchars($message[4]); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <?php endif; ?>

    <?php if ($result != ""): ?>
    <div class="terminal-section">
        <div class="section-title"><?php echo _T("Result:", "xmppmaster"); ?></div>
        <div class="terminal-output">
            <pre><?php echo htmlspecialchars($result, ENT_QUOTES, 'UTF-8'); ?></pre>
        </div>
    </div>
    <?php endif; ?>

    <div class="back-button-container">
        <form>
            <input class="btnPrimary" type="button" value="<?php echo _T("Back", "xmppmaster"); ?>" onclick="history.go(-1)">
        </form>
    </div>

</div>
