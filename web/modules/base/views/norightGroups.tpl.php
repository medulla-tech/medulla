<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

/* Insert these attributes in the main ACL array, so that the widget system
   hide them automatically */
global $aclArray; 
$aclArray['base']['primary_autocomplete'] = '';
$aclArray['base']['groupsselected'] = '';

if ($_GET["action"] == "add") {
    $primary = getUserDefaultPrimaryGroup();
    $secondary = array();
} else {
    $primary = getUserPrimaryGroup($detailArr["uid"][0]);
    $secondary = getUserSecondaryGroups($detailArr["uid"][0]);
}

$table = new Table();
$table->add(
            new TrFormElement(_("Primary group"), new InputTpl("primary_autocomplete")),
            array("value" => $primary)
            );
$table->add(
            new TrFormElement(_("Groups"), new MultipleInputTpl("groupsselected")),
            $secondary
            );

$table->display();
