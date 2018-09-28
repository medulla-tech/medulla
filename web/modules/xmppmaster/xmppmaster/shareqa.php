<?php
/*
 * (c) 2018 Siveo, http://www.siveo.net
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
 * File shareqa.php
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/base/includes/users-xmlrpc.inc.php");
require("modules/kiosk/graph/packages.css");

if (isset($_POST['bcreate'])){
  $json = json_decode($_POST['jsonDatas'], true);
  $json["users"] = json_decode($json['users'], true);
  if(count($json['users']) != 0)
  {
    $fail_list = [];
    foreach($json['users'] as $user)
    {
      $response = xmlrpc_create_Qa_custom_command($user, $json['os'], $json['namecmd'], $json['customcmd'], $json['description'] );
      if ($response== -1) {
        $fail_list[] = $user;
      }
    }
    if (count($fail_list)){
      new NotifyWidgetFailure("Error creating custom Quick Action");
    }
    else {
      new NotifyWidgetSuccess(sprintf("Custom Quick Action %s shared successfully",$json['namecmd']));
    }
  }
  else {
    new NotifyWidgetFailure(sprintf("No user selected to share the Quick Action %s",$json['namecmd']));
  }
  //header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/shareqa", array()));
}


$p = new PageGenerator(_T("Share the Quick Action",'xmppmaster').' '.$_GET['namecmd']);
$p->setSideMenu($sidemenu);
$p->display();


$errors = "";
$count = get_users_detailed($errors, "", 0, 0)[0];
$users_list = get_users_detailed($errors, "", 0, $count);

$list_str = "";
foreach($users_list[1] as $user)
{
  if($user['uid'] != $_SESSION['login'])
    $list_str .= '<li data-draggable="item" data-uuid="'.$user['uid'].'">'.$user['uid'].'</li>';
}

if($_SESSION['login'] != "root")
{
  $list_str .= '<li data-draggable="item" data-uuid="root">root</li>';
}

$f = new ValidatingForm(array("id" => "profile-form", "onchange"=>"generate_json()","onclick"=>"generate_json()"));
$f->push(new Table());
$f->add(new TitleElement(_T("Select Users", "xmppmaster")));
$f->add(new SpanElement('<div style="display:inline-flex; width:100%" id="users">
    <!-- Source : https://www.sitepoint.com/accessible-drag-drop/ -->
    <div style="width:100%">
        <h1>'._T("Available users","xmppmaster").'</h1>
        <ol data-draggable="target" id="available-users">'.$list_str.'</ol>
    </div>

    <div style="width:100%">
        <h1>'._T("Selected users","xmppmaster").'</h1>
        <ol data-draggable="target" id="selected-users">
        </ol>
    </div>
</div>',"users"));

$f->add(new HiddenTpl("jsonDatas"), array("value" => "", "hide" => True));

$f->addValidateButton("bcreate");
$f->pop();
$f->display(); // display the form
?>
<script src="modules/xmppmaster/graph/js/drag-and-drop.js"></script>
<script>
  function generate_json()
  {
      //Clean the json and regenere new users list
      users = [];

      var selector = ["selected"];

      jQuery.each(selector, function(id, selectedValue){

          //For each selector, create a list
          users[selectedValue] = {};
          jQuery.each(jQuery('#'+selectedValue+'-users li'), function(id, user){
              users.push(jQuery(user).html());
          });
      });

      var datas = {};
      datas['users'] = users;
      datas['action'] = 'share';
      datas['namecmd'] = "<?php echo addslashes($_GET["namecmd"]);?>";
      datas["customcmd"] = "<?php echo addslashes($_GET["customcmd"]);?>";
      datas["os"] = "<?php echo addslashes($_GET["os"]);?>";
      datas["description"] = "<?php echo addslashes($_GET["description"]);?>";

      jQuery("input[name='jsonDatas']").val(JSON.stringify(datas))
  }

</script>
