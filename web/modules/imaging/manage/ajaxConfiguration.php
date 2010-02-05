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
require("../includes/xmlrpc.inc.php");

$location = getCurrentLocation();
 
$t = new TitleElement(_T("Imaging server configuration", "imaging"));
$t->display();

if (xmlrpc_doesLocationHasImagingServer($location)) {
    $f = new ValidatingForm();
    
    $f->add(new TitleElement(_T("Traffic control", "imaging")));
    $f->push(new Table());
    $interfaces = array("eth0" => "eth0", "eth1" => "eth1");
    $ifaces = new SelectItem("net_int");
    $ifaces->setElements($interfaces);
    $ifaces->setElementsVal($interfaces);
    $f->add(
        new TrFormElement(_T("Network interface on which traffic shaping is done", "imaging"), 
        $ifaces)
    );
    $f->add(
        new TrFormElement(_T("Network interface theorical throughput (Mbit)", "imaging"), 
        new InputTpl("net_output")), array("value" => "1000")
    );
    $f->add(
        new TrFormElement(_T("Max. throughput for TFTP restoration (Mbit)", "imaging"), 
        new InputTpl("net_tftp")), array("value" => "1000")
    );
    $f->add(
        new TrFormElement(_T("Max. throughput for NFS restoration (Mbit)", "imaging"), 
        new InputTpl("net_nfs")), array("value" => "1000")
    );
    $f->pop();
    
    $f->add(new TitleElement(_T("Restoration options", "imaging")));
    $f->push(new Table());
    $rest_selected = "nfs";
    $rest_type = new RadioTpl("rest_type");
    $rest_type->setChoices(array("nfs" => "NFS (Standard)", "mtftp" => "MTFTP (Multicast)"));
    $rest_type->setValues(array("nfs" => "nfs", "mtftp" => "mtftp"));
    $rest_type->setSelected($rest_selected);
    $f->add(
        new TrFormElement(_T("Restoration type", "imaging"), $rest_type)
    );
    $f->add(
        new TrFormElement(_T("Restoration: MTFTP maximum waiting (in sec)", "imaging"), 
        new InputTpl("rest_wait")), array("value" => "5")
    );
    $f->pop();
    
    $f->add(new TitleElement(_T("Boot options", "imaging")));
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Full path to the XPM displayed at boot", "imaging"), 
        new InputTpl("boot_xpm")), array("value" => "")
    );
    $f->add(
        new TrFormElement(_T("Message displayed during backup/restoration", "imaging"), 
        new TextareaTpl("boot_msg")), array("value" => "Warning ! Your PC is being backed up or restored. Do not reboot !")
    );
    $f->add(
        new TrFormElement(_T("Keyboard mapping (empty/fr)", "imaging"), 
        new InputTpl("boot_keyboard")), array("value" => "")
    );
    $f->pop();
    
    $f->add(new TitleElement(_T("Administration options", "imaging")));
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Password for adding a new client", "imaging"), 
        new InputTpl("misc_passwd")), array("value" => "")
    );
    $f->pop();
    
    $f->addButton("bvalid", _T("Validate"));
    $f->pop();
    $f->display();
} else {
    # choose the imaging server we want to associate to that entity
    xmlrpc_getAllNonLinkedImagingServer();

}
 
 ?>
