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
require_once("modules/xmppmaster/includes/html.inc.php");
?>

<style>
#popup{
  min-height: 400px;
  overflow: scroll;
}

</style>

<?php global $maxperpage;

$start = (isset($_GET['start'])) ? $_GET['start'] : 0;
$end = (isset($_GET['maxperpage'])) ? $_GET['maxperpage'] : $maxperpage;
$filter = (isset($_GET['filter'])) ? $_GET['filter'] : "";

$machines_list = xmlrpc_get_machines_to_unban($_GET['jid'], $start, $end, $filter);

$checks = [];
$names = [];
$startDates = [];
$jids = [];

// Used for default date and min-date
$today = date("Y-m-d");

foreach($machines_list['datas'] as $key=>$machine){
  $checks[] = '<input type="checkbox" name="selected_machine[]" value="'.$machine['jid'].'"/>';
  $reasons[] = '<input type="text" name="reason[]" value="" disabled/>';
  //$startDates[] = '<input type="date" name="start_date[]" min="'.$today.'" value="'.$today.'" disabled/><input type="time" name="start_time[]" min="'.$today.'" value="'.$today.'" disabled/>';
  $jids[] = $machine['jid'];
  $names[] = $machine['name'];
}

if($machines_list['total'] > 0){
  $n = new OptimizedListInfos( $checks, _T("Selection", "admin"));
  $n->disableFirstColumnActionLink();
  $n->setParamInfo($machines_list['datas']);
  $n->addExtraInfo($names, _T("Name", "admin"));
  //$n->addExtraInfo($startDates, _T("From Date", "admin"));
  //$n->addExtraInfo($reasons, _T("Reason", "admin"));
  $n->setTableHeaderPadding(0);
  $n->setItemCount($machines_list['total']);
  $n->setNavBar(new AjaxNavBar($machines_list['total'], $filter));


  $n->start = 0;
  $n->end = $machines_list['total'];

  echo '<form action="'.urlStrRedirect("admin/admin/relaysList").'" method="POST">';
  echo '<input type="checkbox" name="unban_all" id="ban_all">Unban All machines from this relay';
  $n->display();
  echo '<input type="hidden" name="jid_ars" value="'.$_GET['jid'].'">';
  echo '<input type="submit" name="unban" value="'._T('Unban Machines', 'admin').'" />';
  echo '</form>';
}
else{
  echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
  echo '<thead>';
  echo '<tr>';
  echo '<td>'._T("Selection", "admin").'</td>';
  echo '<td>'._T("Name", "admin").'</td>';
  echo '</tr>';
  echo '</thead>';
  echo '</table>';
}
?>

<script>
jQuery("input[type='checkbox']").on('click', function(){
  jQuery(this).parent().siblings().children('input').each(function(id, element){
    if(jQuery(element).prop('disabled') == true)
    {
      jQuery(element).prop('disabled', false);
    }
    else{
      jQuery(element).prop('disabled', true);
    }
  })

})
</script>
