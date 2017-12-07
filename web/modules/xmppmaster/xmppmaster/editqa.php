<?php
/**
 *  (c) 2015-2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * file editqa.php
 */
?>
<?php
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
    $os  = isset($_POST['os'])?$_POST['os']:(isset($_GET['os'])?$_GET['os']:'windows');
    $namecmd  = isset($_POST['namecmd'])?$_POST['namecmd']:(isset($_GET['namecmd'])?$_GET['namecmd']:'');
    $customcmd  = isset($_POST['customcmd'])?$_POST['customcmd']:(isset($_GET['customcmd'])?$_GET['customcmd']:'');
    $description  = isset($_POST['description']) ? $_POST['description'] : (isset($_GET['description'])?$_GET['description']:'');
    $user  = isset($_POST['user'])?$_POST['user']:(isset($_GET['user'])?$_GET['user']:'');
    $editcreate = isset($_POST['editcreate'])?$_POST['editcreate']:(isset($_GET['editcreate'])?$_GET['editcreate']:'createqa');
if (isset($_POST["bcreate"])){
    //creation ou update
    switch($editcreate){
        case 'createqa':
            $response = xmlrpc_create_Qa_custom_command($_SESSION['login'], $os, $namecmd, $customcmd, $description );
            if ($response== -1) {
                new NotifyWidgetFailure("Error creating custom Quick Action");
            }
            else{
                new NotifyWidgetSuccess(sprintf("Custom Quick Action %s created successfully",$namecmd));
            }
            header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/customQA", array()));
        break;
        case 'editeqa':
            $response = xmlrpc_updateName_Qa_custom_command($user, $os, $namecmd, $customcmd, $description);
            if ($response== -1) {
                new NotifyWidgetFailure(sprintf("Error updating custom Quick Action %s",$namecmd));
            }
            else{
                new NotifyWidgetSuccess(sprintf("Custom Quick Action %s updated successfully",$namecmd));
            }
            header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/customQA", array()));
        break;
    }
}
else{
    if ($editcreate == 'editeqa'){
        $p = new PageGenerator(sprintf (_T("Edit Custom Quick action : %s", 'xmppmaster'), $namecmd));
    }else{
        $p = new PageGenerator(sprintf (_T("Create Custom Quick action", 'xmppmaster')));
    }
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm(array("onchange"=>"getJSON()","onclick"=>"getJSON()"));
    $f->push(new Table());

    $oslist = new SelectItem('os');
    $oslist->setElements(array("Linux","Windows","MacOs"));
    $oslist->setElementsVal(array("linux","windows","macos"));
    $oslist->setSelected($os);

    $f->add( new TrFormElement(_T('Operating System', 'xmppmaster'), $oslist), array());
    if ($editcreate == 'createqa'){
        $f->add( new TrFormElement(_T("Command name", "xmpmaster"), new InputTpl('namecmd')), array("value" => $namecmd, "required" => True));
    }
    $f->add( new TrFormElement(_T("Command", "xmpmaster"), new InputTpl('customcmd')), array("value" => $customcmd, "required" => True));

    $f->add( new TrFormElement(_T("Command description", "xmpmaster"), new InputTpl('description')), array("value" => $description,"required" => True));

    $f->add(new HiddenTpl("user"), array("value" => $user, "hide" => True));
    if ($editcreate == 'editeqa'){
        $f->add(new HiddenTpl("namecmd"), array("value" => $namecmd, "hide" => True));
    }
    $f->add(new HiddenTpl("editcreate"), array("value" => $editcreate, "hide" => True));
    $f->addValidateButton("bcreate");

    $f->display();
}

?>
