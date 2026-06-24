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
$updatetype="all";
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

// compliance
   $k = new ListInfos(array($count), _T("Tatal linux", "updates"));
   $compliance_total_percent_bar = (string) new medulla_progressbar_static(
        $compliance_total_percent,
        "",
        "Overall Linux compliance rate for entity {$completename}.\nPercentage of machines fully up to date."
    );
    $k->addExtraInfo(array( $compliance_total_percent_bar),
                       _T("compliance total", "updates"));


    $compliance_security_percent_bar = (string) new medulla_progressbar_static(
        $compliance_security_percent,
        "",
        "Linux security update compliance for entity {$completename}.\nMachines without pending security patches."
    );

    $k->addExtraInfo(array($compliance_security_percent_bar),
                     _T("compliance secutity", "updates"));


    $compliance_kernel_percent_bar = (string) new medulla_progressbar_static(
        $compliance_kernel_percent,
        "",
        "Linux kernel compliance for entity {$completename}.\nMachines running an up-to-date kernel version."
    );

    $k->addExtraInfo(array( $compliance_kernel_percent_bar),
                     _T("compliance kernel", "updates"));

    $compliance_other_percent_bar = (string) new medulla_progressbar_static(
        $compliance_other_percent,
        "",
        "Other Linux updates compliance for entity {$completename}.\nCovers non-security and non-kernel packages."
    );
    $k->addExtraInfo(array( $compliance_other_percent_bar),
                     _T("compliance other", "updates"));

    $converter = new ConvertCouleur();

    $k->setCaptionText(sprintf("%s %s",
                            _T("Detail Machine Linux on Entity ", 'updates'),
                                $_GET['completename']));

    $k->setCssCaption(  $border = 1,
                        $bold = 0,
                        $bgColor = "lightgray",
                        $textColor = "black",
                        $padding = "10px 0",
                        $size = "20",
                        $emboss = 1,
                        $rowColor = $converter->convert("lightgray"));
    $k->disableFirstColumnActionLink();
    $k->display($navbar = 0, $header = 0);


$actions_update_complete_machines = $actions_update_kernel_machines = $actions_update_secutity_machines = $actions_update_other_machines = array();
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
    /*

      $compliance_total_percent_bar = (string) new medulla_progressbar_static(
        $compliance_total_percent,
        "",
        "Overall Linux compliance rate for entity {$completename}.\nPercentage of machines fully up to date."
    );

    */

    $intValue = intval($param['total_count']);
    if ($intValue > 0) {
        $actions_update_complete_machines[]= new ActionPopupItem( _T("Update complete machine linux [$hostname] on entity [$completename]", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateone", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                320,
                                                                "actions_update_complete_machine");
    } else {
          $actions_update_complete_machines[] = new EmptyActionItem1( _T("No update complete on the Linux machine [$hostname] of the entity [$completename]", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg", "", "updates", "updates");
    }

    $intValue = intval($param['kernel_count']);
    if ($intValue > 0) {
        $actions_update_kernel_machines[]= new ActionPopupItem( _T("Update kernel machine linux [$hostname] on entity [$completename]", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateone", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                320,
                                                                "actions_update_kernel_machine");
    } else {
          $actions_update_kernel_machines[] = new EmptyActionItem1(_T("No update type kernel on the Linux machine [$hostname] of the entity [$completename]", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg", "", "updates", "updates");
    }

    $intValue = intval($param['security_count']);
    if ($intValue > 0) {
        $actions_update_secutity_machines[]= new ActionPopupItem( _T("Update security machine linux [$hostname] on entity [$completename]", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateone", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                320,
                                                                "actions_update_secutity_machine");
    } else {
          $actions_update_secutity_machines[] = new EmptyActionItem1(_T("No update type security on the Linux machine [$hostname] of the entity [$completename]", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg", "", "updates", "updates");
    }

    $intValue = intval($param['other_count']);
    if ($intValue > 0) {
        $actions_update_other_machines[]= new ActionPopupItem( _T("Update other machine linux [$hostname] on entity [$completename]", "updates"),
                                                                "deployUpdateLinuxType",
                                                                "updateone", "",
                                                                "updates",
                                                                "updates",
                                                                null,
                                                                320,
                                                                "actions_update_other_machine");
    }
    else {
          $actions_update_other_machines[] = new EmptyActionItem1(_T("No update type security on the Linux machine [$hostname] of the entity [$completename]", "updates"),
                                                            "deployUpdateLinuxType",
                                                            "updateoneg", "", "updates", "updates");
    }


}// end params


    $n = new OptimizedListInfos($machines['hostname'], _T("Hostname", "updates"));

    $n->addExtraInfo($machines['platform'],
                       _T("Platform", "updates"));

    $n->addExtraInfo($machines['security_count'],
                       _T("Security", "updates"));

    $n->addExtraInfo($machines['kernel_count'],
                       _T("Kernel", "updates"));

    $n->addExtraInfo($machines['other_count'],
                       _T("other", "updates"));


    $n->addExtraInfo($machines['total_count'],
                       _T("total", "updates"));
    $n->setcssIds("linux");

    $n->addActionItemArray($actions_update_complete_machines);
    $n->addActionItemArray($actions_update_kernel_machines);
    $n->addActionItemArray($actions_update_secutity_machines);
    $n->addActionItemArray($actions_update_other_machines);

    $n->setTableHeaderPadding(10);
    $n->start = 0;
    $n->end = $count;
    // $converter = new ConvertCouleur();
    $n->setItemCount($count);
    $n->disableFirstColumnActionLink();
    $n->setNavBar(new AjaxNavBar($count, $filter));
    $n->setParamInfo($params);
    $n->display($navbar = 0, $header =5);

 //     echo "<pre>";
 // print_r($params);
 // echo "</pre>";

?>
