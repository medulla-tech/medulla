<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<style type="text/css">
<!--

<?php
global $conf;
require("modules/base/includes/users.inc.php");
require("includes/template.inc.php");

?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Users"),
                    "link" => "main.php?module=base&submod=users&action=index"),
              array("name" => _("Edit ACL")));

require("localSidebar.php");

require("graph/navbar.inc.php");
?>

<?php

//if we post information
if ($_POST["buser"]) {
  $acl=$_POST["acl"];
  $aclattr=$_POST["aclattr"];
}
else {
  $aclString=getAcl($_GET["user"]);
  $aclArr=createAclArray($aclString);
  $acl=$aclArr["acl"];
  $aclattr=$aclArr["aclattr"];
}

if ($_POST["buser"]) {

  $aclString=getAcl($_GET["user"]);
  $aclArr=createAclArray($aclString);
  $acl=$aclArr["acl"];
  unset($acl[0]);
  $aclattr=$aclArr["aclattr"];
  unset($aclattr[0]);

  foreach ($_SESSION['supportModList'] as $mod) {
    unset($acl[$mod]);
  }
    foreach ($_POST["acl"] as $key => $value) {
        $acl[$key]=$value;
    }

  foreach ($_POST["aclattr"] as $key => $value) {
    $aclattr[$key]=$value;
  }

  setAcl($_GET["user"],createAclString($acl,$aclattr));
}

function createAclAttrTemplate($module_name,$aclattr) {
  global $aclArray;
  $rowNum=1;

  //if not acl array
  if (!$aclArray[$module_name]) { return ''; }

  $tpl = new Template('.', 'keep');
  $tpl->set_file("main", "modules/base/templates/editacl_attr.html");
  $tpl->set_block("main", "formacl", "formacls");

  $tpl->set_var("hide",_("hide"));
  $tpl->set_var("description_dsc",_("description"));
  $tpl->set_var("read_only",_("read only"));
  $tpl->set_var("read_write",_("read/write"));

  //foreach $aclArray definition in infopackage
  foreach ($aclArray[$module_name] as $key => $value) {

    //alternate class for display
    if ($rowNum%2) {
      $tr_class='class="alternate"';
    }
    else {
      $tr_class="";
    }
    $rowNum++;

    $tpl->set_var("tr_class",$tr_class);



    $tpl->set_var("nom",$key);
    $tpl->set_var("description",$value);

    $tpl->set_var("checked_hide","");
    $tpl->set_var("checked_ro","");
    $tpl->set_var("checked_rw","");

    if ($aclattr[$key]=="ro") {
      $tpl->set_var("checked_ro","checked");
    } else if ($aclattr[$key]=="rw"){
      $tpl->set_var("checked_rw","checked");
    } else {
      $tpl->set_var("checked_hide","checked");
    }

    $tpl->parse('formacls', 'formacl', true);
  }

  $bidule = $tpl->parse("bidule", "main");
  return $bidule;
}

function createRedirectAclTemplate($module_name,$acl) {
    global $descArray;
    global $redirArray;
    $key=$module_name;
    $rowNum=1;

    $tpl = new Template('.', 'keep');

    $tpl->set_file("ptable", "modules/base/templates/editacl_page.html");
    $tpl->set_block("ptable", "action", "actions");
    $tpl->set_block("ptable", "submodule", "submodules");

    $tpl->set_var("module_name",$module_name);
    $tpl->set_var("select_all",_("Select all"));
    $tpl->set_var("unselect_all",_("Deselect all"));
    $tpl->set_var("function_name_desc",_("Function name"));
    $tpl->set_var("authorize",_("Authorize"));

    $value=$redirArray[$module_name];
    //print_r($value);
    foreach ($value as $subkey=> $subvalue) {

        //check if checked submodules
            if ($acl[$key][$subkey]["right"]) {
            $tpl->set_var("checkedsub","checked");
            } else {
            $tpl->set_var("checkedsub","");
            }
        $tpl->set_var("submodule_name",$subkey);


        foreach ($subvalue as $actionkey=> $actionvalue) {
            if ($rowNum%2) {
            $tr_class='class="alternate"';
            }
            else {
            $tr_class="";
            }
            $rowNum++;

            $tpl->set_var("tr_class",$tr_class);
            //check if checked action
            if ($acl[$key][$subkey][$actionkey]["right"]) {
            $tpl->set_var("checked","checked");
            } else {
            $tpl->set_var("checked","");
            }


            if ($descArray[$key][$subkey][$actionkey]) {
            $tpl->set_var("desc_action",$descArray[$key][$subkey][$actionkey]);
            } else {
            $tpl->set_var("desc_action",_("Warning no desc found in infoPackage.inc.php :").$actionkey);
            }

            $tpl->set_var("action_name", $actionkey);

            $tpl->parse('actions', 'action', true);
        }


        $tpl->parse('submodules', 'submodule', true);
        $tpl->set_var("actions","");



    }

    $bidule = $tpl->parse("bidule", "ptable");
    return $bidule;

}

$tpl = new Template('.', 'keep');
global $descArray;

$tpl->set_var("edit_acl",_("Edit ACL"));
$tpl->set_file("main", "modules/base/templates/editacl.html");
$tpl->set_block("main", "module", "modules");

foreach ($_SESSION["modulesList"] as $key) {

    $tpl->set_var("module_name",$key);

            //check if plugin have information in redirArray
            if ($redirArray[$key]) {
            $tpl->set_var("aclpage_template",createRedirectAclTemplate($key,$acl));
            } else {
            $tpl->set_var("aclpage_template",'');
            }

            $tpl->set_var("aclattr_template",createAclAttrTemplate($key,$aclattr));

    $tpl->parse('modules', 'module', true);

}
$tpl->pparse("out", "main");
?>
