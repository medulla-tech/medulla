<?
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');
require("../../base/includes/edit.inc.php");
require("../../pulse2/includes/locations_xmlrpc.inc.php");

$location = getCurrentLocation();
if ($location == "UUID1")
    $location_name = _T("root", "pulse2");
else
    $location_name = xmlrpc_getLocationName($location);

// Store the location in the session
$_SESSION['imaging_location'] = array(
    "current" => $location,
    "current_name" => $location_name
);

// Check if the entity can be manage by an imaging server
$hasImaging = false;
if (!xmlrpc_doesLocationHasImagingServer($location)) {
    // Try to find the first parent imaging server
    $parents = xmlrpc_getLocationParentPath($location);
    if (is_array($parents) && count($parents) > 0) {
        foreach($parents as $parent_uuid) {
            if (xmlrpc_doesLocationHasImagingServer($parent_uuid)) {
                $location = $parent_uuid;
                if ($location == "UUID1")
                    $location_name = _T("root", "pulse2");
                else
                    $location_name = xmlrpc_getLocationName($location);
                $hasImaging = true;
                break;
            }
        }
    }
}
else {
    $hasImaging = true;
}

if ($hasImaging) {
    // Store the imaging server used for this location
    $_SESSION['imaging_location']['used'] = $location;
    $_SESSION['imaging_location']['used_name'] = $location_name;
}
else {
    // No imaging server associated
    // Display the association list
    $_SESSION['imaging_location']['used'] = -1;
    $_SESSION['imaging_location']['used_name'] = -1;
    require("ajaxcommon_bottom.inc.php");
    exit();
}

$t = new TitleElement(sprintf(_T("Imaging server of entity %s", "imaging"), $location_name), 2);
$t->display();

$ret = xmlrpc_getLocationSynchroState($location);
# result is an array of dicts
# each dict contains 3 keys :
# item: the element id
# id : the sync id
# label : the sync label
#
# first item is the entity status ("item" key is empty)

$running_on = array();
$initerror_on = array();
$todo_on = array();

foreach ($ret as $r) {
    $item = $r['item'];
    if ($item == '') {
        $item = _T("the entity itself", "imaging");
    }
    
    if ($r['id'] == $SYNCHROSTATE_RUNNING) {
        array_push($running_on, $item);
    }
    if ($r['id'] == $SYNCHROSTATE_INIT_ERROR) {
        array_push($initerror_on, $item);
    }
    if ($r['id'] == $SYNCHROSTATE_TODO) {
        array_push($todo_on, $item);
    }
}

if (count($running_on) > 0) {
    $a_href_open = "<a href=''>";
    print "<p>";
    print sprintf(_T("Boot menu generation is still in progress for the following items : %s. Please wait or reload the page %shere%s.", "imaging"), join($running_on, ', '), $a_href_open, '</a>');
    print "</p>";
}

if (count($initerror_on) > 0) {
    print "<p>";
    print _T("The registering in the imaging server has failed.", "imaging");
    print "</p>";
    exit();
}

if (count($todo_on) > 0) {
    # DISPLAY the sync link

    print "<table><tr><td><b>";
    print sprintf(_T('You have modified the boot menu for the following items : %s. If you are done please click on "Generate Menu" to update the computer boot menu.', 'imaging'), join($todo_on, ', '));
    print "</b></font></td><td>";

    $f = new ValidatingForm();
    $f->add(new HiddenTpl("location_uuid"),                        array("value" => $location,  "hide" => True));

    $f->addButton("bsync", _T("Generate Menu", "imaging"));
    $f->display();
    print "</td></tr></table>";
} elseif (isExpertMode()) {
    print "<table><tr><td>";
    print _T('Click on "Force Generation" if you want to force the update of the boot menu', 'imaging');
    print "</td><td>";

    $f = new ValidatingForm();
    $f->add(new HiddenTpl("location_uuid"),                        array("value" => $location,  "hide" => True));

    $f->addButton("bsync", _T("Force Generation", "imaging"));
    $f->display();
    print "</td></tr></table>";
}

?>
