<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id: msctabspause.php 193 2008-03-20 18:31:49Z nrueff $
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

require('modules/msc/includes/commands_xmlrpc.inc.php');

$cmd_id = $_GET['cmd_id'];
$status = get_command_on_group_status($cmd_id);
$title = get_command_on_host_title($cmd_id);

$labels = array(
    array('success',_T('computers were successfully deployed', 'msc')),
    array('running',_T('computers are running a deploiement', 'msc')),
    array('failure',_T('computers failed to deploy', 'msc')),
);

$slabels = array(
    'success'=>array(),
    'running'=>array(
        array('wait_up', _T('waiting to upload', 'msc')),
        array('run_up', _T('running upload', 'msc')),
        array('wait_ex', _T('waiting to execute', 'msc')),
        array('run_ex', _T('running execution', 'msc')),
        array('wait_rm', _T('waiting to suppress', 'msc')),
        array('run_rm', _T('running suppression', 'msc'))
    ),
    'failure'=>array(
        array('fail_up', _T('failed during upload', 'msc'), 'conn_up', _T('(with %s beeing unreachable)', 'msc')),
        array('fail_ex', _T('failed during execution', 'msc'), 'conn_ex', _T('(with %s beeing unreachable)', 'msc')),
        array('fail_rm', _T('failed during suppression', 'msc'), 'conn_rm', _T('(with %s beeing unreachable)', 'msc'))
    )

);

print "<h3>".sprintf(_T("Command '%s' state concerning <b>%s</b> computers", "msc"), $title, $status['total'])."</h3>";
?> <table> <?php

foreach ($labels as $l) {
    $s = $status[$l[0]];
    print "<tr><td><b>".$s['total'][0]."</b> (".$s['total'][1]."%)</td><td></td><td>".$l[1]."</td></tr>";

    foreach ($slabels[$l[0]] as $sl) {
        $ss = $status[$l[0]][$sl[0]];
        print "<tr><td></td><td>".$ss[0]." (".$ss[1]."%)</td><td>".$sl[1];
        if (count($sl) == 4) {
            print " ".sprintf($sl[3], $status[$l[0]][$sl[2]][0]);
        }
        print "</td></tr>";
    }

?> </table>
