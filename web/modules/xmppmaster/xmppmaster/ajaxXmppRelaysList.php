<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$relays = xmlrpc_get_xmpprelays_list($start, $maxperpage, $filter, 'all');

$raw = 0;
$params = [];
foreach($relays['datas']['hostname'] as $key=>$array){
  $params[] = [
    'id' => $relays['datas']['id'][$raw],
    'hostname' => $relays['datas']['hostname'][$raw],
    'enabled' => $relays['datas']['enabled'][$raw],
    'enabled_css' => $relays['datas']['enabled_css'][$raw],
    'jid'=> $relays['datas']['jid'][$raw],
    'cluster_name' => $relays['datas']['cluster_name'],
    'cluster_description' => $relays['datas']['cluster_description'],
    'classutil' => $relays['datas']['classutil'][$raw],
    'macaddress'=> $relays['datas']['macaddress'][$raw],
    'ip_xmpp' => $relays['datas']['ip_xmpp'][$raw],
    'agenttype'=> 'relayserver'
  ];

  $relays['datas']['hostname'][$raw] = '<span class="relay-clickable">'.$relays['datas']['hostname'][$raw].'</span>';
  $relays['datas']['jid'][$raw] = '<span class="relay-clickable">'.$relays['datas']['jid'][$raw].'</span>';
  $relays['datas']['cluster_name'][$raw] = '<span class="relay-clickable">'.$relays['datas']['cluster_name'][$raw].'</span>';
  $relays['datas']['cluster_description'][$raw] = '<span class="relay-clickable">'.$relays['datas']['cluster_description'][$raw].'</span>';
  $relays['datas']['classutil'][$raw] = '<span class="relay-clickable">'.$relays['datas']['classutil'][$raw].'</span>';
  $relays['datas']['macaddress'][$raw] = '<span class="relay-clickable">'.$relays['datas']['macaddress'][$raw].'</span>';
  $relays['datas']['ip_xmpp'][$raw] = '<span class="relay-clickable">'.$relays['datas']['ip_xmpp'][$raw].'</span>';

  $editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
  $editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");
  if ($relays['datas']['enabled'][$raw]){
    $configActions[] =$editremoteconfiguration;
  }
  else{
    $configActions[] =$editremoteconfigurationempty;
  }
  $raw++;
}

$n = new OptimizedListInfos( $relays['datas']['hostname'], _T("Relays Xmpp", "xmppmaster"));
$n->setMainActionClasses($relays['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $relays['datas']['jid'], _T("Jid", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_name'], _T("Cluster Name", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['cluster_description'], _T("Cluster Description", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['classutil'], _T("Class Util", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['macaddress'], _T("Mac Address", "xmppmaster"));
$n->addExtraInfo( $relays['datas']['ip_xmpp'], _T("Xmpp IP", "xmppmaster"));


$n->setTableHeaderPadding(0);
$n->setItemCount($relays['total']);
$n->setNavBar(new AjaxNavBar($relays['total'], $filter, "updateSearchParamformRunning"));
$n->addActionItemArray($configActions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $relays['total'];

$n->display();
?>

<style>
  .relay-clickable{
    cursor: pointer;
  }
</style>

<script>
jQuery(".relay-clickable").on("click", function(){
  jQuery("#paramformRunning").val(jQuery(this).text());
  pushSearchformRunning();
});
</script>
