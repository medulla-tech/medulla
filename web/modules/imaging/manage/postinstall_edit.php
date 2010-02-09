<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 */
 
/*
 * Edit/Duplicate page for post-installation script
 */
 
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

// id of the script
$script_id = $_GET['itemid'];
// get script values for $script_id
$script = array("id" => "1", "name" => "Sysprep", "value" => "Mount 1\ncp sysprep.inf c:\\\nreboot");

// if task is not defined, we are in edit mode
if(!isset($task)) {
    $task = "edit";
}

if($task == "edit") {
    $name = $script["name"];
    $id = $script["id"];
    $title = "Edit post-installation script";
    $action = "updated";
}
else if($task == "duplicate") {
    $name = "";
    $id = "";
    $title = "Duplicate post-installation script";
    $action = "created";
}

// create page
$p = new PageGenerator(_T($title, "imaging"));
$sidemenu->setBackgroundImage("modules/imaging/graph/images/section_large.png");
$sidemenu->forceActiveItem("postinstall");
$p->setSideMenu($sidemenu);
$p->display();

// form has been posted
if(count($_POST) > 0) {
    
    // get the script values
    $script_id = $_GET["itemid"];
    $script_name = trim($_POST["postinstall_name"]);
    $script_value = $_POST["postinstall_value"];
    
    if ($task == "edit"){
        // store new values for script
        // FIXME
        $ret = 1;
    }
    else if ($task == "duplicate") {
        // create new script
        // FIXME
        $ret = 1;
    }
    // check result
    if ($ret) {
        $str = sprintf(_T("<strong>%s</strong> script $action", "imaging"), $script_name);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/postinstall"));
    } else {
        $str = sprintf(_T("<strong>%s</strong> script wasn't $action", "imaging"), $script_name);
        new NotifyWidgetFailure($str);
    }   
}

// Display the script edit form
$f = new ValidatingForm();
$textarea = new TextareaTpl("postinstall_value");
$textarea->setRows(15);
$textarea->setCols(50);
$f->push(new Table());
$f->add(
    new TrFormElement("Script name", new InputTpl("postinstall_name")), 
    array("value" => $name, "required" => True)
);
$f->add(
    new TrFormElement(_T("Script value"), $textarea), 
    array("value" => $script['value'], "required" => True)
);
$f->pop();
$f->addButton("bvalid", _T("Validate"));
$f->display();

?>
