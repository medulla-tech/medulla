<?php
/*
 * (c) 2015 Siveo, http://http://www.siveo.net
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
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/post_install_script.php');

$location = getCurrentLocation();
list($list, $values) = getEntitiesSelectableElements();
foreach($list as $key => $value ){
    if (xmlrpc_doesLocationHasImagingServer($key) != 1) {
        unset($list[$key]);
        unset($values[$key]);
    }
    if($key == $location){
        unset($list[$key]);
        unset($values[$key]);
    }
}

isset($_GET['itemid'])?$id = $_GET['itemid']:$id = $_POST['itemid'];

isset($_GET['itemlabel'])?$itemlabel = $_GET['itemlabel']:$itemlabel = $_POST['itemlabel'];

$masters = xmlrpc_getLocationMastersByUUID($location, array($id));
$id = $_GET['itemid'];
$master = $masters[$id];
$label = $master['name'];
$desc = $master['desc'];
$master_uuid = $master['uuid'];
$process1 = array();
$process  = xmlrpc_checkProcessCloneMasterToLocation("pulse2-synch-masters");

$index = 0;
foreach($process as $d ){
    $process1['my_var'.$index]= $d;
    $index++;
}
$process1['label']= $label;
$process1['desc']= $desc;
$process1['master_uuid']= $master_uuid;
$process1['id']= $id;
$process1['master']= $master;
//echo http_build_query($process, 'myvar_');
//exit;
if (count($process) > 0){
    // afficher progression des copys
    header("Location: " . urlStrRedirect("imaging/manage/synchromaster",$process1));
    exit;
}
else{
    if(count($list) == 0){
        $msg = sprintf (_T("il n'y a pas de server d'imaging pour cloner le master ")."%s",$label );
        new NotifyWidgetWarning($msg);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    }else
    {// peu cloner
        if(count($_POST) == 0) {
            $p = new PageGenerator(_T("Clone master : ", "imaging").$label);
        }else{
            $_SESSION['processclone']=$process1;
            xmlrpc_startProcessClone($_POST);
            header("Location: " . urlStrRedirect("imaging/manage/synchromaster",$process1));
            exit;
            //$p = new PageGenerator(_T("Clone master progression : ", "imaging").$label);
        }
        $sidemenu->forceActiveItem("master");
        $p->setSideMenu($sidemenu);
        $p->display();
        echo "$desc";
        $f = new ValidatingForm();//array("action" => urlStrRedirect("imaging/manage/clone_master_action"),));
        $f->add(new TitleElement(_T("Master", "imaging")));
        $f->add(new HiddenTpl("id"), array("value" => $id, "hide" => True));
        $f->add(new HiddenTpl("itemlabel"), array("value" => $itemlabel, "hide" => True));
        $f->add(new HiddenTpl("location"), array("value" => $location, "hide" => True));
        $f->add(new HiddenTpl("masteruuid"), array("value" => $master_uuid, "hide" => True));
        $f->push(new Table());
        $index=0;
        foreach($list as $key => $value ){
            $val=array_pop(explode('>',$value));
            $f->add(
                new TrFormElement("clone Master [<strong>" . $label . "</strong>]  to "._T('Imaging Server', 'imaging').' : [<strong>'.$val.'</strong>]', new CheckBoxTpl('server_imaging['.$key.']')),
                array("value" => 1)
        );
        }
        $f->pop();
        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    }
}
?>
