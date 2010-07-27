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
require("../../base/includes/edit.inc.php");

$location = getCurrentLocation();

$t = new TitleElement(_T("Imaging server configuration", "imaging"));
$t->display();

if (xmlrpc_doesLocationHasImagingServer($location)) {
    $ret = xmlrpc_getLocationSynchroState($location);

    if ($ret['id'] == $SYNCHROSTATE_RUNNING) {
        $a_href_open = "<a href=''>";
        print sprintf(_T("The synchro is running, please wait or reload the page %shere%s", "imaging"), $a_href_open, '</a>');
    } elseif ($ret['id'] == $SYNCHROSTATE_INIT_ERROR) {
        print _T("The registering in the imaging server has failed.", "imaging");
    } else {
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

        $config = xmlrpc_getImagingServerConfig($location);
        $imaging_server = $config[0];
        $default_menu = $config[1];

        $f = new ValidatingForm(array("action"=>urlStrRedirect("imaging/manage/save_configuration"),));

        $f->add(new HiddenTpl("is_uuid"),                       array("value" => $imaging_server['imaging_uuid'], "hide" => True));
        /* We dont have this information right now in the database schema

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
        $f->pop();*/

        $lang = xmlrpc_getAllKnownLanguages();
        $lang_choices = array();
        $lang_values = array();

        $lang_id2uuid = array();
        foreach ($lang as $l) {
            $lang_choices[$l['imaging_uuid']] = $l['label'];
            $lang_values[$l['imaging_uuid']] = $l['imaging_uuid'];
            $lang_id2uuid[$l['id']] = $l['imaging_uuid'];
        }

        $language = new SelectItem("language");

        $language->setElements($lang_choices);
        $language->setElementsVal($lang_values);
        if ($imaging_server['fk_language']) {
            $language->setSelected($lang_id2uuid[$imaging_server['fk_language']]);
        }
        $f->push(new Table());
        $f->add(
            new TrFormElement(_T("Menu language", "imaging"), $language)
        );
        $f->pop();

        $f->push(new DivExpertMode());


        $f->add(new TitleElement(_T("Default menu parameters", "imaging")));
        $f->push(new Table());

        $f->add(
            new TrFormElement(_T('Default menu label', 'imaging'),
                              new InputTpl("default_m_label")),
            array("value" => $default_menu['default_name'])
        );
        $f->add(
                new TrFormElement(_T('Default menu timeout', 'imaging'),
                                  new InputTpl("default_m_timeout")),
                array("value" => $default_menu['timeout'])
        );
        $f->pop();


        $f->add(new TitleElement(_T("Restoration options", "imaging")));
        $f->push(new Table());
        $possible_protocols = web_def_possible_protocols();
        $default_protocol = web_def_default_protocol();
        $protocols_choices = array();
        $protocols_values = array();

        /* translate possibles protocols */
        _T('nfs', 'imaging');
        _T('mtftp', 'imaging');
        foreach ($possible_protocols as $p) {
            if ($p['label']) {
                if ($p['label'] == $default_menu['protocol']) {
                    $rest_selected = $p['imaging_uuid'];
                }
                if ($p['label'] == $default_protocol) {
                    $p['label'] = _T($p['label'], 'imaging').' '._T('(default)', 'imaging');
                }
                $protocols_choices[$p['imaging_uuid']] = $p['label'];
                $protocols_values[$p['imaging_uuid']] = $p['imaging_uuid'];
            }
        }

        $rest_type = new RadioTpl("rest_type");

        $rest_type->setChoices($protocols_choices);
        $rest_type->setValues($protocols_values);
        $rest_type->setSelected($rest_selected);
        $f->add(
            new TrFormElement(_T("Restoration type", "imaging"), $rest_type)
        );
        $f->add(
            new TrFormElement(_T("Restoration: MTFTP maximum waiting (in sec)", "imaging"),
            new InputTpl("rest_wait")), array("value" => $default_menu['timeout'])
        );
        $f->pop();

        $f->add(new TitleElement(_T("Boot options", "imaging")));
        $f->push(new Table());
        $f->add(
            new TrFormElement(_T("Full path to the XPM displayed at boot", "imaging"),
            new InputTpl("boot_xpm")), array("value" => $default_menu['background_uri'])
        );
        $f->add(
            new TrFormElement(_T("Message displayed during backup/restoration", "imaging"),
            new TextareaTpl("boot_msg")), array("value" => $default_menu['message']) //"Warning ! Your PC is being backed up or restored. Do not reboot !")
        );

        $f->pop();

        $f->pop(); /* Closes expert mode div */

        /*$f->add(
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
        $f->pop();*/

        $_GET["action"] = "save_configuration";
        $f->addButton("bvalid", _T("Validate"));
        $f->pop();
        $f->display();
    }
} else {
    # choose the imaging server we want to associate to that entity
    $ajax = new AjaxFilter(urlStrRedirect("imaging/manage/ajaxAvailableImagingServer"), "container", array('from'=>$_GET['from']));
    $ajax->display();
    print "<br/><br/><br/>";
    $ajax->displayDivToUpdate();
}

 ?>
