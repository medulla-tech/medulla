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


require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');

// get entities
require("modules/pulse2/includes/xmlrpc.inc.php");
require("modules/pulse2/includes/locations_xmlrpc.inc.php");


$location = getCurrentLocation();

if (isset($_POST["bconfirm"])) {
    $from = $_POST['from'];
    $loc_id = $_POST['loc_id'];
    $loc_name = $_POST['loc_name'];
    $item_uuid = $_POST['itemid'];
    
    $label = urldecode($_POST['itemlabel']);
    
    //$params = getParams();
    /*$params['default_name'] = $_POST['default_m_label'];
    $params['timeout'] = $_POST['timeout'];
    $params['background_uri'] = $_POST['background_uri'];
    $params['message'] = $_POST['message'];
    $params['protocol'] = $_POST['protocol'];
    $params['loc_name'] = $_POST['loc_name'];
    */

    $ret = xmlrpc_linkImagingServerToLocation($item_uuid, $loc_id, $loc_name);

    // goto images list 
    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Link between imaging server <strong>%s</strong> and the entity <strong>%s</strong> succeeded.", "imaging"), $label, $loc_id);
        new NotifyWidgetSuccess($str);
        // Synchronize boot menu
        $ret = xmlrpc_synchroLocation($location);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for package server: %s", "imaging"), implode(', ', $ret[1])));
        }
        header("Location: " . urlStrRedirect("imaging/manage/configuration", $params));
        exit;
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/$from", $params));
        exit;
    } else {
        new NotifyWidgetFailure($ret[1]);
        header("Location: " . urlStrRedirect("imaging/manage/$from", $params));
        exit;
    }
}


$locations = getUserLocations();
foreach ($locations as $loc) {
    if ($location == $loc['uuid']) {
        $loc_name = $loc['name'];
    }
}

$params = getParams();

$item_uuid = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);
$loc_id = $_GET['loc_id'];
$from  = $_GET['from'];

$f = new PopupForm(sprintf(_T("Do you really want to link the Imaging Server '<b>%s</b>' to the entity '<b>%s</b>'", "imaging"), $label, $loc_name));

// form preseeding*/
$f->add(new HiddenTpl("location"),                      array("value" => $location,                      "hide" => True));
$f->add(new HiddenTpl("loc_id"),                        array("value" => $loc_id,                        "hide" => True));
$f->add(new HiddenTpl("loc_name"),                      array("value" => $loc_name,                      "hide" => True));
$f->add(new HiddenTpl("itemlabel"),                     array("value" => $label,                         "hide" => True));
$f->add(new HiddenTpl("itemid"),                        array("value" => $item_uuid,                     "hide" => True));
$f->add(new HiddenTpl("from"),                          array("value" => $from,                          "hide" => True));
/*
$input = new TrFormElement(_T('Default menu label', 'imaging'),        new InputTpl("default_m_label"));
$f->add($input,                                         array("value" => ''));

$input = new TrFormElement(_T('timeout', 'imaging'),        new InputTpl("timeout"));
$f->add($input,                                             array("value" => web_def_menu_timeout()));
        
$input = new TrFormElement(_T('Background URI', 'imaging'), new InputTpl("background_uri"));
$f->add($input,                                             array("value" => ''));
        
$input = new TrFormElement(_T('Message', 'imaging'),        new InputTpl("message"));
$f->add($input,                                             array("value" => web_def_menu_message()));
        
$input = new TrFormElement(_T('protocol', 'imaging'),       new InputTpl("protocol"));
$f->add($input,                                             array("value" => ''));
# TODO NEED TO GET THE POSSIBLE protocol AND ASK AS A LIST
        
*/
$f->addValidateButton("bconfirm");
//$f->addButton("bconfig", _T("Confirm and configure", "imaging"));
$f->addCancelButton("bback");
$f->display();
    

?>
