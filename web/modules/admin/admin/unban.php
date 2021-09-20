<?php
/*
 * (c) 2021 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 *
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");

global $maxperpage;

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end = (isset($_GET['end'])) ? $_GET['end'] : $maxperpage;
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";

$page = new PageGenerator(_T("Unban machines on relay", "admin").' '.htmlentities($_GET['hostname']).' : '.htmlentities($_GET['jid']));
$page->display();

print "<br/><br/><br/>";
//$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxban"), "container1", ['jid'=>$_GET['jid']], 'popupSearch');
$ajax = new AjaxFilter(urlStrRedirect("admin/admin/ajaxunban"), "container1", ['jid'=>$_GET['jid']]);
$ajax->display();
print "<br/><br/><br/>";
$ajax->displayDivToUpdate();

?>
