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

/* Get MMC includes */
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/includes.php");
require('../includes/xmlrpc.inc.php');
require("../../base/includes/edit.inc.php");

$location = getCurrentLocation();

if (!xmlrpc_doesLocationHasImagingServer($location)) {
    # choose the imaging server we want to associate to that entity
    $ajax = new AjaxFilter(urlStrRedirect("imaging/manage/ajaxAvailableImagingServer"), "container", array('from'=>$_GET['from']));
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
    exit();
}
    
$ret = xmlrpc_getLocationSynchroState($location);

if ($ret['id'] == $SYNCHROSTATE_RUNNING) {
    $a_href_open = "<a href=''>";
    print sprintf(_T("The synchro is running, please wait or reload the page %shere%s", "imaging"), $a_href_open, '</a>');
    exit();
}

if ($ret['id'] == $SYNCHROSTATE_INIT_ERROR) {
    print _T("The registering in the imaging server has failed.", "imaging");
    exit();
}

if ($ret['id'] == $SYNCHROSTATE_TODO) {
    # DISPLAY the sync link

    print "<table><tr><td><font color='red'><b>";
    print _T('This location has been modified, when you are done, please press on "Synchronize" so that modifications are updated on the Imaging server.', 'imaging');
    print "</b></font></td><td>";

    $f = new ValidatingForm();
    $f->add(new HiddenTpl("location_uuid"),                        array("value" => $location,  "hide" => True));

    $f->addButton("bsync", _T("Synchronize", "imaging"));
    $f->display();
    print "</td></tr></table>";
} elseif (isExpertMode()) {
    print "<table><tr><td>";
    print _T('Click on "Force synchronize" if you want to force the synchronization', 'imaging');
    print "</td><td>";

    $f = new ValidatingForm();
    $f->add(new HiddenTpl("location_uuid"),                        array("value" => $location,  "hide" => True));

    $f->addButton("bsync", _T("Force synchronize", "imaging"));
    $f->display();
    print "</td></tr></table>";
}

    $t = new TitleElement(_T("Available post-installation scripts", "imaging"));
    $t->display();

    if (! isset($params) ) {
        $params = array();
    }
    $ajax = new AjaxFilter("modules/imaging/manage/ajaxPostInstallLevel2.php", "Level2", $params, "formLevel2");
    //$ajax->setRefresh(10000);
    $ajax->display();
    echo '<br/><br/><br/>';
    $ajax->displayDivToUpdate();

?>
