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

$f = new ValidatingForm();
$f->push(new Table());

// General infos for cluster
$f->add(new TrFormElement(_T("Cluster Name", "admin"), new InputTpl('cluster_name')), ['value'=>$name]);
$f->add(new TrFormElement(_T("Cluster Description", "admin"), new InputTpl('cluster_description')), ['value'=>$description]);


// Relays associated to the cluster
$list = xmlprc_get_ars_from_cluster($id);
$outoptions = "";
$inoptions = "";
$default_list = [];
$default_id = [];

foreach($list['out_cluster'] as $outCluster){
    $outoptions.='<li data-jid="'.$outCluster['jid'].'" data-idars="'.$outCluster['id_ars'].'" data-idcluster="'.$outCluster['id_cluster'].'" value="'.$outCluster['jid'].'">'.$outCluster['name'].'</li>';
}
foreach($list['in_cluster'] as $inCluster){
    $inoptions .= '<li data-jid="'.$inCluster['jid'].'" data-idars="'.$inCluster['id_ars'].'" data-idcluster="'.$inCluster['id_cluster'].'" value="'.$inCluster['jid'].'">'.$inCluster['name'].'</li>';
    $default_list[] = $inCluster['jid'];
    $default_id[] = $inCluster['id_ars'];
}
$f->add(new TrFormElement(_T("Cluster List", "admin"),new SpanElement('<div style="display:flex">
<div>
<h3>'._T('Relays <b>outside</b> the cluster', 'admin').'</h3>
<ul id="outCluster" name="outCluster">'.$outoptions.'</ul>
</div>

<div style="width:10px;"></div>

<div><h3>'._T("Relays <b>inside</b> the cluster", "admin").'</h3>
<ul id="inCluster" name="inCluster">'.$inoptions.'</ul>
</div>
</div>')));

$hidden = new HiddenTpl('cluster_id');
$f->add($hidden, array("value" => $id, 'id'=>"cluster_id", "hide" => True));

$hidden = new HiddenTpl('relays_id');
$f->add($hidden, ['value'=>implode(',',$default_id), 'hide'=>true]);

$hidden = new HiddenTpl('relays_list');
$f->add($hidden, ['value'=>implode(',',$default_list), 'hide'=>true]);
//$f->add(new TrFormElement("", new HiddenTpl('relays_list[]', ['hidden'=>true])), ['value'=>$default_list, 'hide'=>true]);
//$f->pop();
$f->addValidateButton("bconfirm", _T("Edit", "admin"));
$f->display();
?>
<style>
#inCluster, #outCluster{
  background-color: white;
  width:250px;
  height:200px;
  margin-right:30px;
  border : black, solid, 1px;
}

#inCluster, #outCluster{
  padding-left:5px;
  padding-top:5px;
  overflow-y: auto;
}

#inCluster li, #outCluster li{
  list-style-type: none;
}

#inCluster li:hover, #outCluster li:hover{
  background-color: rgb(240,240,250);
}
</style>

<script>
jQuery(function(){
  jQuery("#outCluster li, #inCluster li").draggable({
    connectToSortable: "#inCluster, #outCluster",
    stop: function(){
      cluster_list = []
      cluster_id = []

      jQuery("#inCluster li").each(function(id, relay){
          //
          if(typeof(jQuery(relay).attr('data-jid')) != "undefined"){
            cluster_list.push(jQuery(relay).attr('data-jid'))
            cluster_id.push(jQuery(relay).attr('data-idars'))
          }

      })

      jQuery("input[name='relays_id']").val(cluster_id.join(','))
      jQuery("input[name='relays_list']").val(cluster_list.join(','))
    },
  })

  jQuery( "#outCluster, #inCluster" ).sortable({
    revert: true
  });
  jQuery( "ul, li" ).disableSelection();
});


</script>
