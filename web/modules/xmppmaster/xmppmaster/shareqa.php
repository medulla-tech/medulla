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

if (isset($_POST['bcreate'])){
  $json = json_decode($_POST['jsonDatas'], true);
  if (!is_array($json)) { $json = array(); }
  // 'users' is already an array after the decode above; decode again only if it came as a JSON string
  if (isset($json['users']) && is_string($json['users'])) {
    $json["users"] = json_decode($json['users'], true);
  }
}
// Only reconcile on a valid payload, so an empty POST never wipes every share
if (isset($_POST['bcreate']) && isset($json['namecmd'])){
  $self = $_SESSION['login'];
  // Desired "shared with" set = right column, never including the owner himself
  $desired = is_array($json['users']) ? $json['users'] : [];
  $desired = array_values(array_filter($desired, function($u) use ($self) { return $u != $self; }));
  // Current "shared with" set (authoritative, server-side), owner excluded
  $current = xmlrpc_get_list_of_users_for_shared_qa($json['namecmd']);
  if (!is_array($current)) { $current = []; }
  $current = array_values(array_filter($current, function($u) use ($self) { return $u != $self; }));

  $to_add    = array_diff($desired, $current); // newly shared
  $to_remove = array_diff($current, $desired); // un-shared

  $fail_list = [];
  foreach($to_add as $user)
  {
    $response = xmlrpc_create_Qa_custom_command($user, $json['os'], $json['namecmd'], $json['customcmd'], $json['description'] );
    if ($response== -1) {
      $response = xmlrpc_updateName_Qa_custom_command($user, $json['os'], $json['namecmd'], $json['customcmd'], $json['description']);
      if($response == -1)
        $fail_list[] = $user;
    }
  }
  foreach($to_remove as $user)
  {
    // Argument order mirrors removeqa.php: (login, os, namecmd)
    xmlrpc_delQa_custom_command($user, $json['os'], $json['namecmd']);
  }

  if (safeCount($fail_list)){
    new NotifyWidgetFailure(sprintf(_T("Error when updating sharing of Quick Action %s","xmppmaster"), $json['namecmd']));
  }
  elseif (safeCount($to_add) || safeCount($to_remove)) {
    new NotifyWidgetSuccess(sprintf(_T("Sharing of Quick Action %s updated successfully","xmppmaster"), $json['namecmd']));
  }
  //header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/shareqa", array()));
}

$p = new PageGenerator(_T("Share the Quick Action",'xmppmaster').' '.$_GET['namecmd']);
$p->setSideMenu($sidemenu);
$p->display();

$errors = "";
$count = get_users_detailed($errors, "", 0, 0)[0];
$users_list = get_users_detailed($errors, "", 0, $count);

$users_owning_qa = xmlrpc_get_list_of_users_for_shared_qa($_GET["namecmd"]);

$self = $_SESSION['login'];
if (!is_array($users_owning_qa)) { $users_owning_qa = []; }
// Users the QA is currently shared with = owners minus the owner himself
$shared_with = array_values(array_filter($users_owning_qa, function($u) use ($self) { return $u != $self; }));

// Helper to render a draggable list item
$li = function($uid) {
  return '<li data-draggable="item" data-uuid="'.htmlspecialchars($uid).'">'.htmlspecialchars($uid).'</li>';
};

// Right column: every current share (rendered from the authoritative list so a
// share is never dropped just because the directory didn't return that user)
$selected_str = "";
foreach($shared_with as $uid) {
  $selected_str .= $li($uid);
}

// Left column: directory users not already shared with (and not the owner)
$shown = array_merge(array($self), $shared_with);
$available_str = "";
foreach($users_list[1] as $user)
{
  // XML-RPC may return uid as a stdClass wrapper (->scalar) instead of a string
  $uid = is_object($user['uid']) ? $user['uid']->scalar : $user['uid'];
  if (in_array($uid, $shown)) { continue; }
  $available_str .= $li($uid);
  $shown[] = $uid;
}
// root is not always returned by the directory search; expose it as a target
if ($self != "root" && !in_array("root", $shown)) {
  $available_str .= $li("root");
}

$f = new ValidatingForm(array("id" => "profile-form", "onchange"=>"generate_json()","onclick"=>"generate_json()"));
$f->push(new Table());

$f->add(new TitleElement(_T("Owner", "xmppmaster")));
$f->add(new SpanElement("<div class='qa-owner-box'><ul class='qa-owner-list'><li>".htmlspecialchars($self)."</li></ul></div>","users"));


$f->add(new TitleElement(_T("Select Users", "xmppmaster")));

$f->add(new SpanElement('<div class="qa-toolbar"><input type="button" class="btnSecondary" onclick="selectAllUsers()" value="'._T("Select all users","xmppmaster").'"/></div><div class="qa-users-container" id="users">
    <!-- Source : https://www.sitepoint.com/accessible-drag-drop/ -->
    <div class="qa-user-column">
        <h1>'._T("Available users","xmppmaster").'</h1>
        <ol class="qa-user-list" data-draggable="target" id="available-users">'.$available_str.'</ol>
    </div>

    <div class="qa-user-column">
        <h1>'._T("Shared with","xmppmaster").'</h1>
        <ol class="qa-user-list" data-draggable="target" id="selected-users">'.$selected_str.'</ol>
    </div>
</div>',"users"));

$f->add(new HiddenTpl("jsonDatas"), array("value" => "", "hide" => True));

$f->addValidateButton("bcreate");
$f->pop();
$f->display(); // display the form
?>
<script src="modules/xmppmaster/graph/js/drag-and-drop.js"></script>
<script>
  function selectAllUsers()
  {
    jQuery.each(jQuery("#available-users").children("li"), function(id, user){
      jQuery("#selected-users").append(user);
    });
    //generate_json();
  }

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
