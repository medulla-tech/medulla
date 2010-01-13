<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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

require('modules/msc/includes/commands_xmlrpc.inc.php');
require('modules/msc/includes/functions.php');

if (strlen($_GET['cmd_id'])) {
    $cmd_id = $_GET['cmd_id'];
    $coh_ids = get_id_command_on_host($cmd_id);
    $coh = get_commands_on_host($coh_ids[0]);
    
    $title = get_command_on_host_title($cmd_id);
    $title = sprintf(_T("Command '%s' state concerning <b>%s</b>", "msc"), $title, $coh['host']);
    print "<h3>$title</h3>";
    
    $statusTable = getStatusTable();
    print '<table width="100%">';
    print '<tr><th>'._T('Current State', 'msc').'</th><th>'._T('uploaded', 'msc').'</th><th>'._T('executed', 'msc').'</th><th>'._T('deleted', 'msc').'</th></tr>';
    print '<tr><td>'.$statusTable[$coh['current_state']].'</td>';
    print '<td width="33%"><img style="vertical-align: middle;" alt="'.$coh['uploaded'].'" src="modules/msc/graph/images/status/'.return_icon($coh['uploaded']).'"/></td> ';
    print '<td width="33%"><img style="vertical-align: middle;" alt="'.$coh['executed'].'" src="modules/msc/graph/images/status/'.return_icon($coh['executed']).'"/></td> ';
    print '<td width="33%"><img style="vertical-align: middle;" alt="'.$coh['deleted'].'" src="modules/msc/graph/images/status/'.return_icon($coh['deleted']).'"/></td> ';
    print '</tr></table>';


} else {
    print _T("error : cmd_id must be given", "msc");
}
?>
