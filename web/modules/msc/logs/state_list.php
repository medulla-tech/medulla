<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id: widgets.inc.php 561 2009-03-24 08:50:42Z cdelfosse $
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

include_once("modules/msc/includes/commands_xmlrpc.inc.php");

if (!empty($_GET["commands"])) {
    setCommandsFilter($_GET["commands"]);
}

$paramname2 = $_GET['paramname2'];

$res = get_all_commandsonhost_currentstate();

$states = new SelectItem($paramname2, 'pushSearch', 'searchfieldreal noborder');

$list = array();
$labels = array();
foreach ($res as $name) {
    $labels[$name] = _T(preg_replace("[_]", ' ', ucfirst($name)), 'msc');
    $list[$name] = $name;
}
$states->setElements($labels);
$states->setElementsVal($list);

if (in_array($_GET['selected'], array_keys($labels))) {
    $states->setSelected($_GET['selected']);
}

$states->displayContent();

?>
