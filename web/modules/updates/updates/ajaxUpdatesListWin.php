<?php
/*
 * (c) 2022 Siveo, http://www.siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/updates/includes/xmlrpc.php");

$titreentity = _T("Entity : ", 'updates');
$selected_location=$_GET['selected_location'];
$completename = $selected_location['completename'];

// Remplace les "+" par un espace
$completename_cleaned = str_replace('+', ' ', $completename);
// Remplace ">" par " → "
$completename_cleaned = str_replace('>', ' → ', $completename_cleaned);
// Remplace les "&nbsp;" par un espace
$completename_cleaned = str_replace('&nbsp;', ' ', $completename_cleaned);
// Supprime les espaces multiples
$completename_cleaned = preg_replace('/\s+/', ' ', $completename_cleaned);
// Supprime les espaces en début et fin de chaîne
$completename_cleaned = trim($completename_cleaned);
$ide =$selected_location['uuid'];
$titreentitystr = sprintf("%s  [%s] (%s)", $titreentity , $completename_cleaned, $ide);

echo '<div style="display: block; clear: both;">';
$p = new PageGenerator($titreentitystr);
$p->setSideMenu($sidemenu);
$p->display();
echo "</div>";
$ajaxG = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinGray"), "containerGray", $_GET['selected_location'], "formGray");
$ajaxG->display();
print "<br/><br/><br/>";
$ajaxG->displayDivToUpdate();


print "<br/><br/><br/>";
$ajaxW = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinWhite"), "containerWhite", $_GET['selected_location'], "formWhite");
$ajaxW->display();
print "<br/><br/><br/>";
$ajaxW->displayDivToUpdate();

print "<br/><br/><br/>";

$ajaxB = new AjaxFilter(urlStrRedirect("updates/updates/ajaxUpdatesListWinBlack"), "containerBlack", $_GET['selected_location'], "formBlack");
$ajaxB->display();
print "<br/><br/><br/>";
$ajaxB->displayDivToUpdate();
?>

