<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxDeployAllUpdates.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/widgets.inc.php");

global $maxperpage;

$filter  = isset($_GET['filter']) ? $_GET['filter'] : "";
$start = isset($_GET['start']) ? $_GET['start'] : 0;
$end   = (isset($_GET['end']) ? $_GET['start'] + $maxperpage : $maxperpage);

$nameEntitie = "TEST_ENTITIE";
$nameGroup = "";

$params = [];
$familyNames = [];

$f = new ValidatingForm();

if ($nameGroup == '') {
    $label = new RenderedLabel(3, sprintf(_T('Run all updates on entitie : "%s"', 'updates'), $nameEntitie));
} else {
    $label = new RenderedLabel(3, sprintf(_T('Run all updates on group : "%s"', 'updates'), $nameGroup));
}
$f->push(new Table());
$label->display();

$f->add(
    new TrFormElement(
        _T('Deployment interval', 'msc'),
        new multifieldTpl($deployment_fields)
    ),
    $deployment_values
);

$bandwidth = new IntegerTpl("limit_rate_ko");
$bandwidth->setAttributCustom('min = 1  max = 100');
$f->add(
    new TrFormElement(_T("bandwidth throttling (ko)", 'pkgs'), $bandwidth),
    array_merge(array("value" => ''), array('placeholder' => _T('<in ko>', 'pkgs')))
);

$f->pop();

$f->addCancelButton("bback");
$f->display();
