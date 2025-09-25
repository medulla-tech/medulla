<?php
/**
 * (c) 2022 Siveo, http://siveo.net/
 *
 * $Id$
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

require_once("modules/updates/includes/xmlrpc.php");
$updateid = htmlentities($_GET['updateid']);
$title = htmlentities($_GET['title']);

if(isset($_POST['bconfirm'])){
    $result = xmlrpc_approve_update($updateid, $_GET['entityid']);
    if($result){
        $str = sprintf(_T("The update %s (%s) has been approved.", "updates"), $title, $updateid);
        new NotifyWidgetSuccess($str);
    }
    else{
        $str = sprintf(_T("The update %s (%s) hasn't been approved", "updates"), $title, $updateid);
        new NotifyWidgetFailure($str);
    }
    header('location: '.urlStrRedirect("updates/updates/updatesListWin", getFilteredGetParams()));
    exit;
}
else{
    $f = new PopupForm(sprintf(_T("<b>Approve update</b><br>%s<br>(package: %s) ?", "update"), $title,
    $updateid));
    $hidden = new HiddenTpl("updateid");
    $f->add($hidden, array("value" =>$updateid, "hide" => True));
    $f->add(new HiddenTpl("from"), array("value" => $from, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}
?>
