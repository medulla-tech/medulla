<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2011 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/ppolicy/includes/ppolicy.inc.php");

if (isset($_GET["filter"]))
    $filter = $_GET["filter"];
else
    $filter = "";

$editActions = array();
$delActions = array();
$ppolicies = array();

foreach(listPPolicy($filter) as $dn => $entry) {
    if (isset($entry[1]["description"][0]))
        $text = '(' . $entry[1]["description"][0] . ')';
    else
        $text = '';
    $name = $entry[1]["cn"][0];
    if ($name == "default") {
        $editActions[] = new ActionItem(_T("Edit password policy", "ppolicy"),"editppolicy","edit","ppolicy", "base", "users");
        $delActions[] = new EmptyActionItem();
    } else {
        $editActions[] = new ActionItem(_T("Edit password policy", "ppolicy"),"editppolicy","edit","ppolicy", "base", "users");
        $delActions[] = new ActionPopupItem(_T("Delete password policy", "ppolicy"),"deleteppolicy","delete","ppolicy", "base", "users");
    }
    $ppolicies[$name] = $text;
}

$n = new ListInfos(array_keys($ppolicies), _T("Password policies", "ppolicy"));
$n->setAdditionalInfo(array_values($ppolicies));
$n->setNavBar(new AjaxNavBar(count($ppolicies), $filter));
$n->setCssClass("groupName");
$n->addActionItemArray($editActions);
$n->addActionItemArray($delActions);
$n->display();

?>
