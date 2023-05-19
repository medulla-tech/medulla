<?
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

print "<h1>"._T('Available updates','update')."</h1>";

require_once("includes/xmlrpc.inc.php");
//require_once("modules/update/includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/xmlrpc.inc.php");
$updates = getProductUpdates();
$update_titles = array();

foreach ($updates as $update){
    $update_titles[] = $update['title'];
}


$n = new OptimizedListInfos($update_titles, _T("Update", "update"));
$n->setItemCount(safeCount($updates));
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->start = 0;
$n->end = 50;

ob_start();
$n->display();
$list = ob_get_clean();


//print "<pre>";
//print ;
$text  = "<h1>"._T('Available updates','backuppc')."</h1>";
$text .= '<div style="height:400px;width:100%;overflow-y:scroll;">';
$text .= $list;
$text .= "</div>";
$f = new NotifyWidget();
$f->add($text);

?>
