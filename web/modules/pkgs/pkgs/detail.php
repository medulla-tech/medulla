<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("includes/PageGenerator.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/msc/includes/utilities.php");
?>

<style>
thead{
  text-align: :left;
}
</style>

<?php
function renderAction($sequence, $os){
  $header = "";
  $values = "";
  $content = "";

  //associations is used to create association label=> action name
  $associations = [];
  foreach($sequence as $action){
    $associations[$action['actionlabel']] = ltrim($action['action'], 'action');
  }

  foreach($sequence as $action){
    $content .= '<div class="actions" id="'.$os.'-'.$action['actionlabel'].'">';
    $content .= '<h3>Action '.ltrim(ltrim($action['action'], 'action'), '_').'</h3>';

    $content.= '<ul>';
    if(isset($action['command'])){
      $command = base64_decode($action['command'], true) == false ? $action['command'] : base64_decode($action['command']);
      $content.= '<li>';
      $content .= _T("Executed Command", "pkgs").' : '.nl2br(htmlentities($command));
      $content .= '</li>';
    }
    if(isset($action['typescript']) && $action['typescript'] != ""){
      $content.= '<li>';
      $content .= _T("Type Script", "pkgs").' : '.htmlentities($action['typescript']);
      $content .= '</li>';
    }
    if(isset($action['bang']) && $action['bang'] != ""){
      $content.= '<li>';
      $content .= _T("Shebang", "pkgs").' : '.htmlentities($action['bang']);
      $content .= '</li>';
    }
    if(isset($action['script'])){
      $script = (base64_decode($action['script'], true) == false) ? $action['script'] : base64_decode($action['script']);
      $content.= '<li>';
      $content .= _T("Script", "pkgs").' : '.nl2br(htmlentities($script));
      $content .= '</li>';
    }
    if(isset($action['timeout']) && $action['timeout'] != ""){
      $content.= '<li>';
      $content .= _T("Timeout", "pkgs").' : '.htmlentities($action['timeout']);
      $content .= '</li>';
    }
    if(isset($action['codereturn']) && $action['codereturn'] != ""){
      $content.= '<li>';
      $content .= _T("Code Return", "pkgs").' : '.htmlentities($action['codereturn']);
      $content .= '</li>';
    }
    if(isset($action['packageuuid'])  && $action['packageuuid'] != ""){
      $content.= '<li>';
      $content .= _T("Alternate Package", "pkgs").' : '.htmlentities($action['packageuuid']);
      $content .= '</li>';
    }
    if(isset($action['environ'])  && $action['environ'] != []){
      $content .= '<li>';
      $content .= _T("Set Environ Variable", "pkgs").' : ';
      $content .= '<ul>';
      foreach($action['environ'] as $opt=>$optval){
        $content  .= '<li>'.htmlentities($opt).': '.htmlentities($optval).'</li>';
      }
      $content .= '</ul>';
      $content .= '</li>';
    }
    if(isset($action['filename'])  && $action['filename'] != ""){
      $content.= '<li>';
      $content .= _T("File", "pkgs").' : '.htmlentities($action['filename']);
      $content .= '</li>';
    }
    if(isset($action['set'])  && $action['set'] != ""){
      $set = (base64_decode($action['set'], true) == false) ? $action['set'] : base64_decode($action['set']);
      $content.= '<li>';
      $content .= _T("Set", "pkgs").' : '.htmlentities($set);
      $content .= '</li>';
    }
    if(isset($action['url'])  && $action['url'] != ""){
      $content.= '<li>';
      $content .= _T("Download File", "pkgs").' : <a href="'.htmlentities($action['url']).'">'.htmlentities($action['url']).'</a>';
      $content .= '</li>';
    }
    if(isset($action['@resultcommand']) && $action['@resultcommand'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['@resultcommand']);
      $content .= '</li>';
    }
    if(isset($action['1@lastlines']) && $action['1@lastlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['1@lastlines']);
      $content .= '</li>';
    }
    if(isset($action['10@lastlines']) && $action['10@lastlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['10@lastlines']);
      $content .= '</li>';
    }
    if(isset($action['20@lastlines']) && $action['20@lastlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['20@lastlines']);
      $content .= '</li>';
    }
    if(isset($action['30@lastlines']) && $action['30@lastlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['30@lastlines']);
      $content .= '</li>';
    }

    if(isset($action['1@firstlines']) && $action['1@firstlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['1@firstlines']);
      $content .= '</li>';
    }
    if(isset($action['10@firstlines']) && $action['10@firstlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['10@firstlines']);
      $content .= '</li>';
    }
    if(isset($action['20@firstlines']) && $action['20@firstlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['20@firstlines']);
      $content .= '</li>';
    }
    if(isset($action['30@firstlines']) && $action['30@firstlines'] != ""){
      $content.= '<li>';
      $content .= _T("Result Command", "pkgs").' : '.htmlentities($action['30@firstlines']);
      $content .= '</li>';
    }

    if(isset($action['targetrestart'])  && $action['targetrestart'] != ""){
      $content.= '<li>';
      $content .= ($action['targetrestart'] == "AM") ? _T("Restart", "pkgs").' : '._T("Agent Machine", "pkgs"): _T("Restart", "pkgs").' : '._T("Machine", "pkgs");
      $content .= '</li>';
    }
    if(isset($action['waiting'])  && $action['waiting'] != ""){
      $content.= '<li>';
      $content .= _T("Waiting", "pkgs").' : '.$action['waiting'].' '._T('secs.', "pkgs").'<br>';
      $content .= _T("Go to", "pkgs").' : <a href="#'.$os.'-'.htmlentities($action['goto']).'">'.htmlentities($associations[$action['goto']]).'</a>';
      $content .= '</li>';
    }
    if(isset($action['comment'])  && $action['comment'] != ""){
      $content.= '<li>';
      $comment = (base64_decode($action['comment'], true) == false) ? $action['comment'] : base64_decode($action['comment']);
      $content .= _T("Comment", "pkgs").' : '.nl2br(htmlentities($comment));
      $content .= '</li>';
    }
    if(isset($action['inventory'])){
      $content.= '<li>';
      $content .= _T("Inventory Activated", "pkgs").' : '.htmlentities($action['inventory']);
      $content .= '</li>';
    }
    if(isset($action['clear'])){
      $content.= '<li>';
      $content .= _T("Clear package after install", "pkgs").' : '.htmlentities($action['clear']);
      $content .= '</li>';
    }
    $content .= '</ul>';
    if(isset($action['error'])){
      $content .= _T('If error go to', 'pkgs').' : <a href="#'.$os.'-'.$action['error'].'">'.$associations[$action['error']].'</a><br>';
    }
    if(isset($action['success'])){
      $content .= _T('If success go to', 'pkgs').' : <a href="#'.$os.'-'.$action['success'].'">'.$associations[$action['success']].'</a><br>';
    }
    $content .= '</div>';
  }

  return $content;
}

$json = json_decode(get_xmpp_package($_GET['packageUuid']),true);
$package = xmpp_getPackageDetail($_GET['packageUuid']);



$page = new PageGenerator(_T("Detail of Package ", "pkgs").'['.$json['info']['name'].']');
$page->setSideMenu($sidemenu);
$page->display();

// Display package context
echo '<h2 id="toggle-context" onclick="_toggle(\'#context\')">'._T("Context", "pkgs").'</h2>';
echo '<div id="context">';
$context = new OptimizedListInfos([$json['info']['name']], _T("Package Name", "pkgs"));
$context->addExtraInfo([isset($json['info']['creator']) ? $json['info']['creator'] : ''], _T("Creator", "pkgs"));
if(isset($json['info']['editor']) && $json['info']['editor'] != "")
  $context->addExtraInfo([$json['info']['editor']], _T("Edited By", "pkgs"));
  $context->addExtraInfo([isset($json['info']['creation_date']) ? $json['info']['creation_date'] : ''], _T("Creation Date", "pkgs"));
if(isset($json['info']['edition_date']))
  $context->addExtraInfo([$json['info']['edition_date']], _T("Last Modification Date", "pkgs"));
if(isset($json['info']['localisation_server']))
  $context->addExtraInfo([$json['info']['localisation_server']], _T("Sharing Location", "pkgs"));
$context->addExtraInfo([$package['id']], _T("Package Uuid", "pkgs"));
$context->addExtraInfo([$json['info']['description']], _T("Description", "pkgs"));
$context->addExtraInfo([$json['info']['version']], _T("Version", "pkgs"));
$context->addExtraInfo([$json['info']['metagenerator']], _T("Type", "pkgs"));
if(isset($json['info']['licenses']))
  $context->addExtraInfo([$json['info']['licenses']], _T("Licenses", "pkgs"));
$context->setNavBar(new AjaxNavBar(0, ""));
$context->display();
echo '</div>';
// Used for both transfer table and files table
$totalSize = (int)$package['size'];

// Transfer method table
echo '<h2 onclick="_toggle(\'#transfer\')">'._T("Transfer Method", "pkgs").'</h2>';
echo '<div id="transfer">';
$transfer = new OptimizedListInfos([$json['info']['methodetransfert']], _T("Transfer method", "pkgs"));
$transfer->addExtraInfo([prettyOctetDisplay($totalSize)], _T("Size", "pkgs"));
$transfer->addExtraInfo([$json['info']['transferfile']], _T("Transferfile", "pkgs"));
if(isset($json['info']['limit_rate_ko']) && $json['info']['limit_rate_ko'] != "")
  $transfer->addExtraInfo([$json['info']['limit_rate_ko']], _T("bandwidth throttling (ko)", "pkgs"));
  $transfer->addExtraInfo([isset($json['info']['spooling']) ? $json['info']['spooling'] : ''], _T("Spooling", "pkgs").' ('._T("Priority", "pkgs").')');
$transfer->addExtraInfo([$json['info']['inventory']], _T("Inventory", "pkgs"));
$transfer->addExtraInfo([$package['do_reboot']], _T("Restart", "pkgs"));
$transfer->setNavBar(new AjaxNavBar(0, ""));
$transfer->display();
echo '</div>';

// Files table
$filesInfos = xmlrpc_get_files_infos($package['id']);
$fileViewerAction = new ActionPopupItem(_T("View File Content", "pkgs"), "preview", "display", "pkgs", "pkgs");

// Using manual table because we don't want pagination
echo '<h2 onclick="_toggle(\'#files\')">'._T("Files", "pkgs").' - ('._T("Total", "pkgs").': '.prettyOctetDisplay($totalSize).')</h2>';
echo '<div id="files">';
echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
echo '<thead>';
echo '<tr>';
  echo '<th style="text-align: center;">'._T("File", "pkgs").'</th>';
  echo '<th style="text-align: center;">'._T("Size", "pkgs").'</th>';
  echo '<th style="text-align: center;">'._T("Ratio Size/Total", "pkgs").'</th>';
  echo '<th style="text-align: center;">'._T("Mime Type", "pkgs").'</th>';
  echo '<th style="text-align: center;">'._T("Action", "pkgs").'</th>';
echo '</tr>';
echo '</thead>';
echo '<tbody>';
foreach($filesInfos['files'] as $id=>$file){
  echo '<tr class="alternate">';
    echo '<td style="text-align: center;">'.$file['name'].'</td>';
    echo '<td style="text-align: center;">'.prettyOctetDisplay((int)$file['size']).'</td>';
    echo '<td style="text-align: center;">'.round(((int)$file['size']/$totalSize)*100, 2).'%</td>';
    echo '<td style="text-align: center;">'.$file["mime"][0].'</td>';
    echo '<td style="text-align: center;" class="action">';
    if(preg_match("#text/(.*)#i", $file['mime'][0])){
      echo '<ul class="action">';
      $fileViewerAction->display("", ["uuid"=>$_GET['packageUuid'], "name"=>$file["name"]]);
      echo '</ul>';
    }
    echo '</td>';
  echo '</tr>';
}
echo '</tbody>';
echo '</table>';
echo '</div>';

// Dependencies table
$detailAction = new ActionItem(_T("Package Detail", "pkgs"), "detail", "display", "pkgs", "pkgs");

// Get the name and uuid of all the packages (without restrictions) in the dependencies list
$allPkgNames = get_pkg_name_from_uuid($json['info']['Dependency']);

// get the restricted (with rights) list of dependencies
$allPackagesList = get_dependencies_list_from_permissions($_SESSION["login"]);
$allDependencies = [];

//thanks to $allPkgNames we have all the packages names
//thanks to $allPackagesList we have the rights for each packages
//thanks to $json['Dependency'] we have all the dependencies
foreach($allPackagesList as $pkg){
  $allDependencies[$pkg['uuid']] = $pkg['name'];
}

echo '<h2 onclick="_toggle(\'#dependencies\')">'._T("Dependencies", "pkgs").'</h2>';

echo '<div id="dependencies">';
// Using manual table because we don't want pagination
echo '<table class="listinfos" cellspacing="0" cellpadding="5" border="1">';
echo '<thead>';
echo '<tr>';
  echo '<th>'._T("Package", "pkgs").'</th>';
  echo '<th>'._T("Uuid", "pkgs").'</th>';
  echo '<th>'._T("Action", "pkgs").'</th>';
echo '</tr>';
echo '</thead>';
foreach($json['info']['Dependency'] as $dep){
  echo '<tr class="alternate">';
    // To ensure we have the name we use the global list
    echo '<td>'.$allPkgNames[$dep].'</td>';
    echo '<td>'.$dep.'</td>';

    echo '<td class="action">';
      echo '<ul class="action">';
      if(isset($allDependencies[$dep]))
      echo $detailAction->display("", ["packageUuid"=>$dep]);
      echo '</ul>';
    echo '</td>';
  echo '</tr>';
}
echo '</table>';
echo '</div>';
$tabsnames = "";
$tabscontents= "";

foreach($json as $key=>$arr){
  if($key != "info"){
    $tabsnames .= '<li><a href="#tabs-'.$key.'">'.$key.'</a></li>';
    $tabscontents .= '<div id="tabs-'.$key.'">'.renderAction($arr["sequence"], $key).'</div>';
  }
}
echo '<h2 onclick="_toggle(\'#tabs\')">'._T("Sequences", "pkgs").'</h2>';
echo '<div id="tabs">';
  echo '<ul>';
  echo $tabsnames;
  echo '</ul>';

  echo $tabscontents;
echo '</div>';
?>
<style>
.actions:target {
   background-color: #ffa;
}
.actions{
  margin-bottom:5px;
  padding:3px;
  border: dashed 1px rgb(100,100,100);
}

.actions a:hover{
  background-color: #007fff;
  color:rgb(255, 255, 255);
  border: 1px solid #003eff
}

.actions a{
  padding:1px;
}
</style>

<script>
jQuery( "#tabs" ).tabs();

_toggle = function(selector){
  jQuery(selector).toggle(500);
}
</script>
