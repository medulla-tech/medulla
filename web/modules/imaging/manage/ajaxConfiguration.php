<?php

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

/* common ajax includes */
require("../includes/ajaxcommon.inc.php");

$t = new TitleElement(_T("Imaging server configuration", "imaging"), 3);
$t->display();

$config = xmlrpc_getImagingServerConfig($location);
$imaging_server = $config[0];
$default_menu = $config[1];

$f = new ValidatingForm(array("action" => urlStrRedirect("imaging/manage/save_configuration"),));

$f->add(new HiddenTpl("is_uuid"), array("value" => $imaging_server['imaging_uuid'], "hide" => True));
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
  $f->pop(); */

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

$pxe_password_label = _T('PXE Password', 'imaging');
$pxe_password_label_desc = _T('Leave this field empty to unset PXE Password', 'imaging');
$pxe_password_label = <<<EOS
<a href="#" class="tooltip">
    $pxe_password_label
    <span><p>
        $pxe_password_label_desc
    </p></span>

</a>
EOS;

$f->add(
        new TrFormElement($pxe_password_label, new PasswordTpl('pxe_password')), array("value" => xmlrpc_getPXEPasswordHash($location) == '' ? '' : '.......')
);
$f->pop();

$f->push(new DivExpertMode());


$f->add(new TitleElement(_T("Default menu parameters", "imaging")));
$f->push(new Table());

$f->add(
        new TrFormElement(_T('Default menu label', 'imaging'), new InputTpl("default_m_label")), array("value" => $default_menu['default_name'])
);
$f->add(
        new TrFormElement(_T('Default menu timeout', 'imaging'), new InputTpl("default_m_timeout")), array("value" => $default_menu['timeout'])
);
if ($default_menu["hidden_menu"]) {
    $hidden_menu_value = 'CHECKED';
} else {
    $hidden_menu_value = '';
}
$f->add(
        new TrFormElement(_T('Hide menu', 'imaging'), new CheckBoxTpl("default_m_hidden_menu")), array("value" => $hidden_menu_value)
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
            $p['label'] = _T($p['label'], 'imaging') . ' ' . _T('(default)', 'imaging');
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
        new TrFormElement(_T("Restoration: MTFTP maximum waiting (in sec)", "imaging"), new InputTpl("rest_wait")), array("value" => $default_menu['mtftp_restore_timeout'])
);
$f->pop();

$f->add(new TitleElement(_T("Boot options", "imaging")));
$f->push(new Table());
$f->add(
        new TrFormElement(_T("Full path to the XPM displayed at boot", "imaging"), new InputTpl("boot_xpm")), array("value" => $default_menu['background_uri'])
);
$f->add(
        new TrFormElement(_T("Message displayed during backup/restoration", "imaging"), new TextareaTpl("boot_msg")), array("value" => $default_menu['message']) //"Warning ! Your PC is being backed up or restored. Do not reboot !")
);

$f->pop();

$f->pop(); /* Closes expert mode div */

/* $f->add(
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
  $f->pop(); */

$_GET["action"] = "save_configuration";
$f->addButton("bvalid", _T("Validate"));
$f->pop();
$f->display();

require("../includes/ajaxcommon_bottom.inc.php");
?>
