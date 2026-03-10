<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
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

require("modules/admin/admin/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

$id = htmlentities($_GET['id']);
$name = htmlentities($_GET['name']);
$description = htmlentities($_GET['description']);


if(isset($_POST['bconfirm'])){
  $cluster_id = htmlentities($_POST['cluster_id']);
  $cluster_name = htmlentities($_POST['cluster_name']);
  $cluster_description = htmlentities($_POST['cluster_description']);
  $relay_ids = htmlentities($_POST['relays_id']);
  $result = xmlrpc_update_cluster($cluster_id, $cluster_name, $cluster_description, $relay_ids);

  if($result['state'] == 'success'){
    new NotifyWidgetSuccess(_T("The cluster <b>$cluster_name</b> has been edited", "admin"));
    header("Location: " . urlStrRedirect("admin/admin/clustersList"));
    exit;
  }
  else{
    new NotifyWidgetFailure(_T("Error during <b>$cluster_name</b> edition", "admin"));
  }
  header("Location: " . urlStrRedirect("admin/admin/clustersList", array()));
  exit;
}

$p = new PageGenerator(_T("Edit Cluster [$name]", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

// Relays associated to the cluster
$list = xmlprc_get_ars_from_cluster($id);
$outoptions = "";
$inoptions = "";
$default_list = [];
$default_id = [];

foreach($list['out_cluster'] as $outCluster){
    $outoptions .= '<option data-jid="'.$outCluster['jid'].'" data-idars="'.$outCluster['id_ars'].'" value="'.$outCluster['id_ars'].'">'.$outCluster['name'].'</option>';
}
foreach($list['in_cluster'] as $inCluster){
    $inoptions .= '<option data-jid="'.$inCluster['jid'].'" data-idars="'.$inCluster['id_ars'].'" value="'.$inCluster['id_ars'].'">'.$inCluster['name'].'</option>';
    $default_list[] = $inCluster['jid'];
    $default_id[] = $inCluster['id_ars'];
}

?>
<form class="mmc-form" method="post" onsubmit="return validateForm('clusterForm');" id="clusterForm">
<table class="mmc-form-table" cellspacing="0">
<tr class="mmc-form-row">
  <td class="mmc-label"><?php echo _T("Cluster Name", "admin"); ?></td>
  <td><input class="mmc-input" type="text" name="cluster_name" value="<?php echo $name; ?>" data-regexp="/.+/" autocomplete="off" /></td>
</tr>
<tr class="mmc-form-row">
  <td class="mmc-label"><?php echo _T("Cluster Description", "admin"); ?></td>
  <td><input class="mmc-input" type="text" name="cluster_description" value="<?php echo $description; ?>" autocomplete="off" /></td>
</tr>
</table>

<div class="cluster-widget">
  <div class="cluster-col">
    <h3><?php echo _T('Relays <b>outside</b> the cluster', 'admin'); ?></h3>
    <select multiple class="cluster-list" id="outCluster"><?php echo $outoptions; ?></select>
  </div>
  <div class="cluster-actions">
    <span class="cluster-arrow-right" id="moveToInCluster"></span>
    <span class="cluster-arrow-left" id="moveToOutCluster"></span>
  </div>
  <div class="cluster-col">
    <h3><?php echo _T("Relays <b>inside</b> the cluster", "admin"); ?></h3>
    <select multiple class="cluster-list" id="inCluster"><?php echo $inoptions; ?></select>
  </div>
</div>

<input type="hidden" name="cluster_id" value="<?php echo $id; ?>" />
<input type="hidden" name="relays_id" value="<?php echo implode(',',$default_id); ?>" />
<input type="hidden" name="relays_list" value="<?php echo implode(',',$default_list); ?>" />
<input type="hidden" name="auth_token" value="<?php echo $_SESSION['auth_token']; ?>" />
<input type="submit" name="bconfirm" value="<?php echo _T('Edit', 'admin'); ?>" class="btnPrimary" />
</form>
<?php
?>
<script>
jQuery(function(){
  function updateHiddenFields(){
    var ids = [], jids = [];
    jQuery("#inCluster option").each(function(){
      ids.push(jQuery(this).val());
      jids.push(jQuery(this).data("jid"));
    });
    jQuery("input[name='relays_id']").val(ids.join(','));
    jQuery("input[name='relays_list']").val(jids.join(','));
  }

  jQuery("#moveToInCluster").on("click", function(){
    jQuery("#outCluster option:selected").appendTo("#inCluster");
    updateHiddenFields();
  });

  jQuery("#moveToOutCluster").on("click", function(){
    jQuery("#inCluster option:selected").appendTo("#outCluster");
    updateHiddenFields();
  });

  jQuery("#outCluster, #inCluster").on("dblclick", "option", function(){
    var target = jQuery(this).closest("#outCluster").length ? "#inCluster" : "#outCluster";
    jQuery(this).appendTo(target);
    updateHiddenFields();
  });
});
</script>
