<?php
/**
 * (c) 2022 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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

require_once("modules/kiosk/includes/xmlrpc.php");

if(isset($_POST['bvalidate'])){

    $id = htmlentities($_POST['id']);
    $acknowledgedbyuser = htmlentities($_POST['acknowledgedbyuser']);
    $askuser = htmlentities($_POST['askuser']);
    $startdate = htmlentities($_POST['startdate']);
    $enddate = htmlentities($_POST['enddate']);
    $status = htmlentities($_POST['status']);
    $package_name = htmlentities($_POST['package_name']);
    $profile_name = htmlentities($_POST['profile_name']);

    if(!in_array($status, ['waiting', 'allowed', 'rejected'])){
        $status = 'rejected';
    }

    $result = xmlrpc_update_acknowledgement($id, $acknowledgedbyuser, $startdate, $enddate, $status);
    $enddatestr = ($enddate == '') ? 'unlimited time' : $enddate;

    if($result){
        $str = sprintf(_T("%s has the right %s on package %s (%s) from %s to %s.", "updates"), $askuser, $status, $package_name, $profile_name, $startdate, $enddatestr);
        new NotifyWidgetSuccess($str);
    }
    else{
        $str = sprintf(_T("Error during editing the acnowledgement", "updates"), $title, $updateid);
        new NotifyWidgetFailure($str);
    }
    header('location: '.urlStrRedirect("kiosk/kiosk/acknowledges"));
    exit;
}

$id = (isset($_GET['id'])) ? htmlentities($_GET['id']) : false;
$status = (isset($_GET['status'])) ? htmlentities($_GET['status']) : false;
$startdate = (isset($_GET['startdate'])) ? htmlentities($_GET['startdate']) : false;
$package_uuid = (isset($_GET['package_uuid'])) ? htmlentities($_GET['package_uuid']) : false;
$profile_name = (isset($_GET['profile_name'])) ? htmlentities($_GET['profile_name']) : false;
$enddate = (isset($_GET['enddate'])) ? htmlentities($_GET['enddate']) : "";
$package_name = (isset($_GET['package_name'])) ? htmlentities($_GET['package_name']) : false;
$askdate = (isset($_GET['askdate'])) ? htmlentities($_GET['askdate']) : false;
$askuser = (isset($_GET['askuser'])) ? htmlentities($_GET['askuser']) : false;

$acknowledgedbyuser = (isset($_GET['acknowledgedbyuser'])) ? htmlentities($_GET['acknowledgedbyuser']) : "";
$newacknowledgedbyuser = $_SESSION['login'];


if(!$id || !$status || !$startdate || !$package_uuid || !$profile_name || !$package_name || !$askdate || ! $askuser){
    $f = new PopupWindowForm(_T("Modify Acknowledge", "kiosk"));
    $f->add(new textTpl(_T("This acknowledge can't be edited (missing parameter)", "kiosk")));
    $f->addCancelButton("bback");
}

else{
    $f = new PopupWindowForm(sprintf(_T("%s asked acknowledge for package %s (profile %s)", "kiosk"), $askuser, $package_name, $profile_name));

    $f->add(new HiddenTpl("id", ["visible"=>false]), ["value" => $id, "hide"=>false]);
    $f->add(new HiddenTpl("acknowledgedbyuser", ["visible"=>false]), ["value" => $newacknowledgedbyuser, "hide"=>false]);
    $f->add(new HiddenTpl("askuser", ["visible"=>false]), ["value" => $askuser, "hide"=>false]);
    $f->add(new HiddenTpl("profile_name", ["visible"=>false]), ["value" => $profile_name, "hide"=>false]);
    $f->add(new HiddenTpl("package_name", ["visible"=>false]), ["value" => $package_name, "hide"=>false]);
    $f->add(new textTpl(_T("Start Date", "kiosk")));
    $date_startdate = new DynamicDateTpl("startdate");
    $date_startdate->setReadOnly(true);
    $f->add($date_startdate, ['value'=>$startdate]);
    $f->add(new textTpl('<br>'._T("End Date", "kiosk")));
    $date_enddate = new DynamicDateTpl("enddate");
    $date_enddate->setReadOnly(false);
    $f->add($date_enddate, ['value'=>$enddate]);
    
    $select_status = new SelectItem('status');
    $select_status->setElements(['waiting','allowed','rejected']);
    $select_status->setElementsVal(['waiting','allowed','rejected']);
    $select_status->setSelected($status);
    $f->add(new textTpl('<br>'._T("Status", "kiosk").' '));
    $f->add($select_status);
    
    
    $f->addValidateButton("bvalidate");
    $f->addCancelButton("bback");
}
$f->display();
?>
