<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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
require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/msc/includes/widgets.inc.php");

global $maxperpage;

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);



echo "<pre>";
//print_r($entities);
//print_r($compliancerate);
echo "</pre>";

$nameEntitie = "TEST_ENTITIE";
$nameGroup = "";

$params = [];
$familyNames = [];

$f = new ValidatingForm();

if ($nameGroup == '')
{
    $label = new RenderedLabel(3, sprintf(_T('Run all updates on entitie : "%s"', 'updates'), $nameEntitie));
}
else
{
    $label = new RenderedLabel(3, sprintf(_T('Run all updates on group : "%s"', 'updates'), $nameGroup));
}
$f->push(new Table());
$label->display();

$f->add(
    new TrFormElement(
        _T('Deployment interval', 'msc'), new multifieldTpl($deployment_fields)
    ), $deployment_values
);

$bandwidth = new IntegerTpl("limit_rate_ko");
$bandwidth->setAttributCustom('min = 1  max = 100');
$f->add(
        new TrFormElement(_T("bandwidth throttling (ko)",'pkgs'), $bandwidth), array_merge(array("value" => ''), array('placeholder' => _T('<in ko>', 'pkgs')))
);

$f->pop();

$f->addCancelButton("bback");
$f->display();


?>
