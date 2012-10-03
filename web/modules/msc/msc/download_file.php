<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

require('modules/msc/includes/machines.inc.php');
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

$p = new PageGenerator(_T("Download file page", "msc"));
$p->setSideMenu($sidemenu);
$p->display();

if (isset($_POST["bconfirm"])) {
    $ret = msc_download_file($_GET['objectUUID']);
    if (is_array($ret) && ($ret[0] === True)) {
        new NotifyWidgetSuccess(_T('The download is in progress.', 'msc'));
    } else {
        if ($ret[1] == 1) {
            new NotifyWidgetFailure(_T("A file is already being downloaded.", "msc"));
        } else {
            new NotifyWidgetFailure(_T("The download has failed.", "msc"));
        }
    }
}

$ajax = new AjaxFilter(urlStrRedirect('base/computers/ajaxDownloadFile', array('objectUUID' => $_GET['objectUUID'])));
$ajax->setRefresh(web_def_refresh_time());
$ajax->display();

$f = new Form(array('id' => 'dl'));
$f->addSummary(_T('Click below to start downloading file from this computer. Warning: the download may last a long time', 'msc'));
$computer = getMachine(array('uuid'=>$_GET['objectUUID']), $ping = False);
$f->addButton('bconfirm', sprintf(_T('Start download from computer %s', 'msc'), $computer->hostname));
$f->display();

print '<br />';

$ajax->displayDivToUpdate();

?>
