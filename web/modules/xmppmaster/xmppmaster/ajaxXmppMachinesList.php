<?php
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$filter = $_GET["filter"];

$filter  = isset($_GET['filter'])?$_GET['filter']:"";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);

$machines = xmlrpc_get_xmppmachines_list($start, $maxperpage, $filter, 'all');

$raw = 0;
$params = [];

$configActions = [];
foreach($machines['datas']['hostname'] as $key=>$array){
  $params[] = [
    'id' => $machines['datas']['id'][$raw],
    'hostname' => $machines['datas']['hostname'][$raw],
    'enabled' => $machines['datas']['enabled'][$raw],
    'enabled_css' => $machines['datas']['enabled_css'][$raw],
    'jid'=> $machines['datas']['jid'][$raw],
    'archi' => $machines['datas']['archi'][$raw],
    'classutil' => $machines['datas']['classutil'][$raw],
    'kiosk_presence' => $machines['datas']['kiosk_presence'][$raw],
    'ad_ou_user' => $machines['datas']['ad_ou_user'][$raw],
    'ad_ou_machine' => $machines['datas']['ad_ou_machine'][$raw],
    'cluster_name' => $machines['datas']['cluster_name'][$raw],
    'cluster_description' => $machines['datas']['cluster_description'][$raw],
    'macaddress'=> $machines['datas']['macaddress'][$raw],
    'ip_xmpp' => $machines['datas']['ip_xmpp'][$raw],
    'agenttype' => 'machine'
  ];
  $machines['datas']['hostname'][$raw] = '<span class="machine-clickable">'.$machines['datas']['hostname'][$raw].'</span>';
  $machines['datas']['jid'][$raw] = '<span class="machine-clickable">'.$machines['datas']['jid'][$raw].'</span>';
  $machines['datas']['archi'][$raw] = '<span class="machine-clickable">'.$machines['datas']['archi'][$raw].'</span>';
  $machines['datas']['classutil'][$raw] = '<span class="machine-clickable">'.$machines['datas']['classutil'][$raw].'</span>';
  $machines['datas']['kiosk_presence'][$raw] = '<span class="machine-clickable">'.$machines['datas']['kiosk_presence'][$raw].'</span>';
  $machines['datas']['ad_ou_user'][$raw] = '<span class="machine-clickable">'.$machines['datas']['ad_ou_user'][$raw].'</span>';
  $machines['datas']['ad_ou_machine'][$raw] = '<span class="machine-clickable">'.$machines['datas']['ad_ou_machine'][$raw].'</span>';
  $machines['datas']['cluster_name'][$raw] = '<span class="machine-clickable">'.$machines['datas']['cluster_name'][$raw].'</span>';
  $machines['datas']['cluster_description'][$raw] = '<span class="machine-clickable">'.$machines['datas']['cluster_description'][$raw].'</span>';
  $machines['datas']['cluster_name'][$raw] = '<span class="machine-clickable">'.$machines['datas']['cluster_name'][$raw].'</span>';
  $machines['datas']['macaddress'][$raw] = '<span class="machine-clickable">'.$machines['datas']['macaddress'][$raw].'</span>';
  $machines['datas']['ip_xmpp'][$raw] = '<span class="machine-clickable">'.$machines['datas']['ip_xmpp'][$raw].'</span>';


  $editremoteconfigurationempty = new EmptyActionItem1(_("Edit config files"),"listconffile", "configg","computers","xmppmaster", "xmppmaster");
  $editremoteconfiguration = new ActionItem(_("Edit config files"),"listconffile","config","computers", "xmppmaster", "xmppmaster");
  if ($machines['datas']['enabled'][$raw]){
    $configActions[] =$editremoteconfiguration;
  }
  else{
    $configActions[] =$editremoteconfigurationempty;
  }
  $raw++;
}

$n = new OptimizedListInfos( $machines['datas']['hostname'], _T("Machines Xmpp", "xmppmaster"));
$n->setMainActionClasses($machines['datas']['enabled_css']);
$n->disableFirstColumnActionLink();
$n->addExtraInfo( $machines['datas']['jid'], _T("Jid", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['archi'], _T("Arch", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['classutil'], _T("Class Util", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['kiosk_presence'], _T("Kiosk presence", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['ad_ou_user'], _T("AD OU User", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['ad_ou_machine'], _T("AD OU Machine", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['cluster_name'], _T("Cluster Name", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['cluster_description'], _T("cluster_description", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['macaddress'], _T("Mac Address", "xmppmaster"));
$n->addExtraInfo( $machines['datas']['ip_xmpp'], _T("Xmpp IP", "xmppmaster"));
$n->setTableHeaderPadding(0);
$n->setItemCount($machines['total']);
$n->setNavBar(new AjaxNavBar($machines['total'], $filter, "updateSearchParamformRunning1"));
$n->addActionItemArray($configActions);
$n->setParamInfo($params);
$n->start = 0;
$n->end = $machines['total'];

$n->display();
?>

<style>
  .machine-clickable{
    cursor: pointer;
  }
</style>
<script>
jQuery(".machine-clickable").on("click", function(){
  jQuery("#paramformRunning").val(jQuery(this).text());
  updateSearchformRunning();
});
</script>
