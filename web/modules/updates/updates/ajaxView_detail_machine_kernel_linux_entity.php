<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxView_detail_machine_kernel_linux_entity.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/updates/includes/html.inc.php");


// echo "<pre>";
// print_r($_GET);
// echo "</pre>";

$completename=$_GET['completename'];

 if (isset($_GET['compliance_total_percent'])) {
        $compliance_total_percent = filter_var($_GET['compliance_total_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_security_percent'])) {
        $compliance_security_percent = filter_var($_GET['compliance_security_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_kernel_percent'])) {
        $compliance_kernel_percent = filter_var($_GET['compliance_kernel_percent'], FILTER_SANITIZE_NUMBER_FLOAT, ['flags' => FILTER_FLAG_ALLOW_FRACTION]);
    }

    if (isset($_GET['compliance_other_percent'])) {
        $compliance_other_percent = filter_var($_GET['compliance_other_percent'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_not_up_to_date'])) {
        $machines_not_up_to_date = filter_var($_GET['machines_not_up_to_date'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_up_to_date'])) {
        $machines_up_to_date = filter_var($_GET['machines_up_to_date'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_security_not_ok'])) {
        $machines_security_not_ok = filter_var($_GET['machines_security_not_ok'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['machines_kernel_not_ok'])) {
        $machines_kernel_not_ok = filter_var($_GET['machines_kernel_not_ok'], FILTER_SANITIZE_NUMBER_INT);
    }

    if (isset($_GET['machines_other_not_ok'])) {
        $machines_other_not_ok = filter_var($_GET['machines_other_not_ok'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }

    if (isset($_GET['total_machines'])) {
        $total_machines = filter_var($_GET['total_machines'], FILTER_VALIDATE_INT, ['options' => ['default' => 0]]);
    }



$entity_id = isset($_GET['entity_id']) ? intval($_GET['entity_id'], 10) : -1;
// "any" : toutes les machines de l'entite, y compris celles a jour.
$updatetype="any";
$maxperpage = $conf["global"]["maxperpage"];
$filter  = isset($_GET['filter']) ? htmlentities($_GET['filter']) : "";
$start = isset($_GET['start']) ? htmlentities($_GET['start']) : 0;
$end   = (isset($_GET['end']) ? $start+$maxperpage : $maxperpage);

// echo "<pre>";
// echo $entity_id;
// echo "<br>";
// echo $updatetype;
// echo "</pre>";
// echo "View_detail_machine_kernel_linux_entity";



$machines  = xmlrpc_get_machines_by_update_type($entity_id,
                                                $updatetype,
                                                $filter,
                                                $start,
                                                $end);

/*

echo "<pre>";
print_r($machines);
echo "</pre>";*/

$count = $machines['total_rows'];


$actions_update_complete_machines = $actions_update_kernel_machines = $actions_update_secutity_machines = $actions_update_other_machines = array();
$machineComplianceBars = array();
$params=[];

foreach($machines['hostname'] as $index => $valeur ){
    $param=[];
    $param['hostname']=$machines['hostname'][$index];
    $param['platform']=$machines['platform'][$index];
    $param['harduuid']=$machines['harduuid'][$index];
    $param['uuid_inventorymachine']=$machines['uuid_inventorymachine'][$index];
    $param['jid']=$machines['jid'][$index];
    $param['security_count']=$machines['security_count'][$index];
    $param['kernel_count']=$machines['kernel_count'][$index];
    $param['other_count']=$machines['other_count'][$index];
    $param['total_count']=$machines['total_count'][$index];

    $param = array_merge($param, $_GET);
    unset($param['module']); // Supprime la clé 'module'
    unset($param['mod']); // Supprime la clé 'mod'
    unset($param['submod']); // Supprime la clé 'submod'
    unset($param['action']); // Supprime la clé 'action'
    unset($param['filter']); // Supprime la clé 'filter'


    $hostname= $param['hostname'];
    $params[]=$param;

    // Binaire : up_machine_linux ne stocke que les mises a jour en attente,
    // aucun ratio n'est calculable.
    $machineIsCompliant = intval($param['total_count']) === 0;
    $machineComplianceBars[] = (string) new medulla_progressbar_static(
        $machineIsCompliant ? 100 : 0,
        "",
        $machineIsCompliant
            ? _T("This machine has no pending update.", "updates")
            : sprintf(_T("This machine has %s pending update(s).", "updates"), intval($param['total_count']))
    );
    /*

      $compliance_total_percent_bar = (string) new medulla_progressbar_static(
        $compliance_total_percent,
        "",
        "Overall Linux compliance rate for entity {$completename}.\nPercentage of machines fully up to date."
    );

    */

    $intValue = intval($param['total_count']);
    if ($intValue > 0) {
        $actions_update_complete_machines[]= new ActionPopupItem( _T("Full update", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateall", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                640,
                                                                "actions_update_complete_machine");
    } else {
          $actions_update_complete_machines[] = new EmptyActionItem1( _T("No update pending", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateallg", "", "updates", "updates");
    }

    $intValue = intval($param['kernel_count']);
    if ($intValue > 0) {
        $actions_update_kernel_machines[]= new ActionPopupItem( _T("Update kernel", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updatekernel", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                640,
                                                                "actions_update_kernel_machine");
    } else {
          $actions_update_kernel_machines[] = new EmptyActionItem1(_T("No kernel update pending", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updatekernelg", "", "updates", "updates");
    }

    $intValue = intval($param['security_count']);
    if ($intValue > 0) {
        $actions_update_secutity_machines[]= new ActionPopupItem( _T("Update security", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updatesecurity", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                640,
                                                                "actions_update_secutity_machine");
    } else {
          $actions_update_secutity_machines[] = new EmptyActionItem1(_T("No security update pending", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updatesecurityg", "", "updates", "updates");
    }

    $intValue = intval($param['other_count']);
    if ($intValue > 0) {
        $actions_update_other_machines[]= new ActionPopupItem( _T("Update other packages", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "package", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                640,
                                                                "actions_update_other_machine");
    }
    else {
          $actions_update_other_machines[] = new EmptyActionItem1(_T("No other update pending", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "packageg", "", "updates", "updates");
    }


}// end params


    echo '<h2>' . sprintf(_T("Linux computers from entity %s", "updates"),
                          htmlspecialchars($completename, ENT_QUOTES, 'UTF-8')) . '</h2>';

    $n = new OptimizedListInfos($machines['hostname'],
                       _T("Machine name", "updates"),
                       "",
                       "",
                       _T("Hostname reported by the Medulla agent.", "updates"));

    $n->addExtraInfo($machines['platform'],
                       _T("Platform", "updates"),
                       "",
                       _T("Distribution and version detected on the machine.", "updates"));

    $n->addExtraInfoRaw($machineComplianceBars,
                       _T("Compliance rate", "updates"),
                       "",
                       _T("Green when the machine has no pending update.", "updates"));

    $n->addExtraInfoCentered($machines['security_count'],
                       _T("Security", "updates"),
                       "",
                       _T("Number of pending security updates on this machine.", "updates"));

    $n->addExtraInfoCentered($machines['kernel_count'],
                       _T("Kernel", "updates"),
                       "",
                       _T("Number of pending kernel updates on this machine.", "updates"));

    $n->addExtraInfoCentered($machines['other_count'],
                       _T("Other", "updates"),
                       "",
                       _T("Number of pending updates other than security or kernel on this machine.", "updates"));

    $n->addExtraInfoCentered($machines['total_count'],
                       _T("Total", "updates"),
                       "",
                       _T("Total number of pending updates on this machine, all categories included.", "updates"));
    $n->setcssIds("linux");

    $n->addActionItemArray($actions_update_complete_machines);
    $n->addActionItemArray($actions_update_kernel_machines);
    $n->addActionItemArray($actions_update_secutity_machines);
    $n->addActionItemArray($actions_update_other_machines);

    $n->setResizable();
    $n->setTableHeaderPadding(10);
    $n->start = 0;
    $n->end = $count;
    // $converter = new ConvertCouleur();
    $n->setItemCount($count);
    $n->disableFirstColumnActionLink();
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->setEmptyState(_T("No Linux machine found", "updates"),
                      _T("No Linux machine has reported a scan for this entity yet.", "updates"));
    $n->display();

 //     echo "<pre>";
 // print_r($params);
 // echo "</pre>";

?>
