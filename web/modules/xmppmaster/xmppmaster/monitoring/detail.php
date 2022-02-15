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
 * file : xmppmaster/xmppmaster/monitoring/alerts.php
 */

 require("graph/navbar.inc.php");
 require("modules/base/computers/localSidebar.php");
 require_once("modules/xmppmaster/includes/xmlrpc.php");
 $p = new PageGenerator(_T("Alerts Detail", 'xmppmaster'));
 $p->setSideMenu($sidemenu);
 $p->display();
?>
<h1><?php echo _T("Machine");?></h1>
<table class="listinfos" cellspacing="0" cellpadding="5" border="1">
  <thead>
    <tr>
      <th><?php echo _T("Hostname");?></th><th><?php echo _T("Date");?></th><th><?php echo _T("Jid");?></th><th><?php echo _T("Uuid");?></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="<?php echo ($_GET['machine_enabled'] == 1) ? 'machineNamepresente' : 'machineName';?>"><?php echo htmlentities($_GET['machine_hostname']);?></td>
      <td><?php echo htmlentities($_GET['mon_machine_date']);?></td>
      <td><?php echo htmlentities($_GET['machine_jid']);?></td>
      <td><?php echo htmlentities($_GET['machine_uuid']);?></td>
    </tr>
  </tbody>
</table>


<h1><?php echo _T("Event");?></h1>
<table class="listinfos" cellspacing="0" cellpadding="5" border="1">
  <thead>
    <tr>
      <th><?php echo _T("Event Name");?></th><th><?php echo _T("Event Type");?></th><th><?php echo _T("Event Date");?></th><th><?php echo _T("Event Status");?></th>
      <?php if($_GET['event_status'] == 0 && isset($_GET['ack_user'], $_GET['ack_date'])){
        echo '<th>';
        echo _T('Acknowledged By');
        echo '</th>';

        echo '<th>';
        echo _T('Acknowledged Date');
        echo '</th>';
      }?>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><?php echo htmlentities($_GET['rule_comment']);?></td>
      <td><?php echo htmlentities($_GET['event_type_event']);?></td>
      <td><?php echo htmlentities($_GET['mon_machine_date']);?></td>
      <td><?php echo ($_GET['event_status'] == 1) ? "Non Acknowledged": "Acknowledged";?></td>
      <?php if($_GET['event_status'] == 0 && isset($_GET['ack_user'], $_GET['ack_date'])){
        echo '<td>';
        echo htmlentities($_GET['ack_user']);
        echo '</td>';

        echo '<td>';
        echo htmlentities($_GET['ack_date']);
        echo '</td>';
      }?>
    </tr>
  </tbody>
</table>

<h1><?php echo _T("Device");?></h1>
<table class="listinfos" cellspacing="0" cellpadding="5" border="1">
  <thead>
    <tr>
      <th><?php echo _T("Device Status");?></th><th><?php echo _T("Device Type");?></th><th><?php echo _T("Device Firmware");?></th><th><?php echo _T("Event");?>Device Serial</th><th><?php echo _T("Device Doc");?></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><?php echo htmlentities($_GET['device_status']);?></td>
      <td><?php echo htmlentities($_GET['device_type']);?></td>
      <td><?php echo htmlentities($_GET['device_firmware']);?></td>
      <td><?php echo htmlentities($_GET['device_serial']);?></td>
      <td><?php echo htmlentities($_GET['device_doc']);?></td>
    </tr>
  </tbody>
</table>
