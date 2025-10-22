<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
 $strin='<?';
 $strou='?>';
 ?>
<style type="text/css">
    #ProductKey1, #ProductKey2, #ProductKey3, #ProductKey4, #ProductKey5{
        width:50px;
    }
    #codeToCopy{
        width:400px;
    }
</style>
<script type="text/javascript">
var template = [
'#',
'#________________________________',
'# OS Debian [x86 and amd64]',
'# Preseed :',
'#',
'# date : <? echo $strin; ?>dateval<? echo $strou; ?>',
'#',
'#Installation Notes',
'#Location: <? echo $strin; ?>Location<? echo $strou; ?>',
'#Notes: <? echo $strin; ?>Comments<? echo $strou; ?>',
'#list parameters : @@listParameters@@',
'#________________________________',
'',
'# LOCALIZATION',
'<?php echo $strin;?>CheckLocale<?php echo $strou;?>d-i debian-installer/locale string <?echo $strin;?>SelectLocale<?php echo $strou;?>',
'<? echo $strin;?>CheckLanguage<? echo $strou;?>d-i debian-installer/language string <? echo $strin;?>SelectLanguage<? echo $strou;?>',
'<? echo $strin;?>CheckCountry<? echo $strou;?>d-i debian-installer/country string <? echo $strin;?>SelectCountry<? echo $strou;?>',
'<? echo $strin;?>CheckSupportedLocales<? echo $strou;?>d-i localechooser/supported-locales multiselect <? echo $strin;?>SelectSupportedLocales<? echo $strou;?>, en_US.UTF-8',
'<? echo $strin;?>CheckKeyboardLayouts<? echo $strou;?>d-i keyboard-configuration/layoutcode string <? echo $strin;?>SelectKeyboardLayouts<? echo $strou;?>',
'<? echo $strin;?>CheckKeyboardToggle<? echo $strou;?>d-i keyboard-configuration/toggle select <? echo $strin;?>SelectKeyboardToggle<? echo $strou;?>',
'',
'### NETWORK',
'<? echo $strin;?>CheckEnableNetwork<? echo $strou;?>d-i netcfg/enable boolean <? echo $strin;?>CheckEnableNetworkValue<? echo $strou;?>',
'# METAPARAM for netcfg/choose_interface <? echo $strin;?>SelectInterface<? echo $strou;?>',
'<? echo $strin;?>CheckInterface<? echo $strou;?>d-i netcfg/choose_interface select <?echo $strin;?>InputInterface<? echo $strou;?>',
'<? echo $strin;?>CheckLinkTimeout<?echo $strou;?>d-i netcfg/link_wait_timeout number <?echo $strin;?>NumberLinkTimeout<? echo $strou;?>',
'<? echo $strin;?>CheckDhcpTimeout<?echo $strou;?>d-i netcfg/dhcp_timeout number <?echo $strin;?>NumberDhcpTimeout<? echo $strou;?>',
'<? echo $strin;?>CheckDhcpV6Timeout<?echo $strou;?>d-i netcfg/dhcpv6_timeout number <?echo $strin;?>NumberDhcpV6Timeout<? echo $strou;?>',
'<? echo $strin;?>CheckDisableAutoconfig<? echo $strou;?>d-i netcfg/disable_autoconfig boolean <? echo $strin;?>CheckDisableAutoconfigValue<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?> d-i netcfg/dhcp_options boolean <? echo $strin;?>CheckDisableDhcpValue<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?><? echo $strin;?>CheckDisableDhcpCombine<? echo $strou;?>d-i netcfg/get_ipaddress string <? echo $strin;?>InputGetIpaddress<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?><? echo $strin;?>CheckDisableDhcpCombine<? echo $strou;?>d-i netcfg/get_netmask string <? echo $strin;?>InputGetNetmask<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?><? echo $strin;?>CheckDisableDhcpCombine<? echo $strou;?>d-i netcfg/get_gateway string <? echo $strin;?>InputGetGateway<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?><? echo $strin;?>CheckDisableDhcpCombine<? echo $strou;?>d-i netcfg/get_nameservers string <? echo $strin;?>InputGetNameservers<? echo $strou;?>',
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?><? echo $strin;?>CheckDisableDhcpCombine<? echo $strou;?>d-i netcfg/confirm_static boolean true',
'<? echo $strin;?>CheckHostname<? echo $strou;?>d-i netcfg/get_hostname string <? echo $strin;?>InputHostname<? echo $strou;?>',
'<? echo $strin;?>CheckDomaine<? echo $strou;?>d-i netcfg/get_Domaine string <? echo $strin;?>InputDomaine<? echo $strou;?>',
'<? echo $strin;?>CheckForceHostname<? echo $strou;?>d-i netcfg/hostname string <? echo $strin;?>InputForceHostname<? echo $strou;?>',
'<? echo $strin;?>CheckDhcpHostname<? echo $strou;?>d-i netcfg/dhcp_hostname string <? echo $strin;?>InputDhcpHostname<? echo $strou;?>',
'<? echo $strin;?>CheckLoadFirmware<? echo $strou;?>d-i hw-detect/load_firmware boolean <? echo $strin;?>CheckLoadFirmwareValue<? echo $strou;?>',
'',
'### NETWORK CONSOLE'
'<? echo $strin;?>CheckNetworkConsole<? echo $strou;?>d-i anna/choose_modules <? echo $strin;?>CheckNetworkConsoleType<? echo $strou;?> <? echo $strin;?>CheckNetworkConsoleValue<? echo $strou;?>',
'<? echo $strin;?>CheckAuthorizedKeysUrl<? echo $strou;?>d-i network-console/authorized_keys_url string <? echo $strin;?>InputAuthorizedKeysUrl<? echo $strou;?>',
'',
'### MIRROR',
'',
].join('\r\n');
</script>

<?php
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/PageGenerator.php");
require("../../../includes/tag.php");
require("../includes/data_linux_file_generator.inc.php");
require("../includes/class_form.php");
?>
<!--Click on to validate disposed of the response file
.on smb: // ipPulse / postinst / sysprep /-->
<?php
if(isset($_SESSION['parameters']))
{//If this session exists : editing file, else creating file
    $parameters = $_SESSION['parameters'];
}
else if(isset($_POST["Location"])){
    $parameters = $_POST;
}

$f = new ValidatingForm(array("id" => "formxml"));
$f->add(new HiddenTpl("codeToCopy"), array("value" => "", "hide" => True));
$f->add(new HiddenTpl("infobulexml"),array("value" => '', "hide" => True));


//==== NEW SECTION ====
// Installation Notes
//=====================
$f->add(new TitleElement(_T("Installation Notes", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Installation_Notes',$info_installation_note)));
$f->push(new Table());

    //_____________
    $f->add(
        new TrFormElement(_T('Title','imaging'), new InputTplTitle('Location',"name file xml")),
        array("required" => True,'value'=>(isset($parameters)) ? $parameters['Title'] : '')
    );
    //_____________
    $f->add(new TrFormElement("Notes".":", new OptTextareaTpl(array('name'=>'Comments','value'=>(isset($parameters)) ? htmlentities($parameters['Notes']) : _T('Enter your comments here...','imaging')))));
$f->pop();
$f->add( new SepTpl());


//==== NEW SECTION ====
// Locale
//=====================

// ---- toggle button
$f->add(new TitleElement(_T("Locales","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Locale', "imaging"),'')));
$f->push(new Table());

// ---- locale
$check_locale = new CheckboxTpl("check-locale");
$select_locale = new SelectItemtitle("select-locale", $info_locale_settings);
$select_locale->setElements($locales_country);
$select_locale->setElementsVal($locales_values);


$fields = [
    $check_locale, $select_locale
];

$values = [
    (isset($parameters)) ? $parameters['CheckLocale'] : '',
    (isset($parameters)) ? $parameters['SelectLocale'] : '',
];

$f->add(
    new TrFormElement('<label for="check-locale">'._T("locale", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);


// ---- language
$check_language = new CheckboxTpl("check-language");
$select_language = new SelectItemtitle("select-language", $info_locale_settings);
$select_language->setElements($languages_country);
$select_language->setElementsVal($languages_values);


$fields = [
    $check_language, $select_language
];

$values = [
    (isset($parameters)) ? $parameters['CheckLanguage'] : '',
    (isset($parameters)) ? $parameters['SelectLanguage'] : '',
];

$f->add(
    new TrFormElement('<label for="check-language">'._T("language", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);


// ---- country
$check_country = new CheckboxTpl("check-country");
$select_country = new SelectItemtitle("select-country", $info_locale_settings);
$select_country->setElements($countries_country);
$select_country->setElementsVal($countries_values);


$fields = [
    $check_country, $select_country
];

$values = [
    (isset($parameters)) ? $parameters['CheckCountry'] : '',
    (isset($parameters)) ? $parameters['SelectCountry'] : '',
];

$f->add(
    new TrFormElement('<label for="check-country">'._T("Country", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);

// ---- supported locales
$check_supportedlocales = new CheckboxTpl("check-supported-locales");
$select_supportedlocales = new SelectItemtitle("select-supported-locales", $info_supported_locales);
$select_supportedlocales->setElements($supported_locales);
$select_supportedlocales->setElementsVal($supported_locales_values);


$fields = [
    $check_supportedlocales, $select_supportedlocales
];

$values = [
    (isset($parameters)) ? $parameters['CheckSupportedLocales'] : '',
    (isset($parameters)) ? $parameters['SelectSupportedLocales'] : '',
];

$f->add(
    new TrFormElement('<label for="check-supported-locales">'._T("Supported Locales", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);


// ---- keyboard layout
$check_keyboardlayouts = new CheckboxTpl("check-keyboard-layouts");
$select_keyboardlayouts = new SelectItemtitle("select-keyboard-layouts", "");
$select_keyboardlayouts->setElements($keyboard_layouts);
$select_keyboardlayouts->setElementsVal($keyboard_layouts_values);


$fields = [
    $check_keyboardlayouts, $select_keyboardlayouts
];

$values = [
    (isset($parameters)) ? $parameters['check-keyboard-layouts'] : '',
    (isset($parameters)) ? $parameters['select-keyboard-layouts'] : '',
];

$f->add(
    new TrFormElement('<label for="check-keyboard-layouts">'._T("Keyboard Layout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);



// ---- keyboard layout
$check_keyboardtoggles = new CheckboxTpl("check-keyboard-toggle");
$select_keyboardtoggles = new SelectItemtitle("select-keyboard-toggle", "");
$select_keyboardtoggles->setElements($keyboard_toggles);
$select_keyboardtoggles->setElementsVal($keyboard_toggles);


$fields = [
    $check_keyboardtoggles, $select_keyboardtoggles
];

$values = [
    (isset($parameters)) ? $parameters['CheckKeyboardToggle'] : '',
    (isset($parameters)) ? $parameters['SelectKeyboardToggle'] : '',
];

$f->add(
    new TrFormElement('<label for="check-keyboard-toggle">'._T("Keyboard Toggle", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
$f->pop();


// ==== New Section ====
// NETWORK
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Network","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Network', "imaging"),'')));
$f->push(new Table());

// ---- keyboard layout
$check_enablenetwork = new CheckboxTpl("check-enable-network");
$check_enablenetworkvalue = new CheckboxTpl("check-enable-network-value", "");


$fields = [
    $check_enablenetwork, $check_enablenetworkvalue
];

$values = [
    (isset($parameters)) ? $parameters['CheckEnableNetwork'] : '',
    (isset($parameters)) ? $parameters['CheckEnableNetworkValue'] : '',
];

$f->add(
    new TrFormElement('<label for="check-enable-network">'._T("Enable Network", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, $info_enable_network]]
);



// ---- Interface
$check_interface = new CheckboxTpl("check-interface");
$select_interface = new SelectItemtitle("select-interface", $info_interface);
$select_interface->setElements($interface_choices);
$select_interface->setElementsVal($interface_choices);

$input_interface = new InputTplTItle("input-interface", $info_interface);

$fields = [
    $check_interface, $select_interface, $input_interface
];

$values = [
    (isset($parameters)) ? $parameters['CheckInterface'] : '',
    (isset($parameters)) ? $parameters['SelectInterface'] : '',
    (isset($parameters) && $parameters['InputInterface'] != 'auto') ? $parameters['InputInterface'] : 'eth0',
];

$f->add(
    new TrFormElement('<label for="check-interface">'._T("Interface", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "placeholder"=>["", "", "eth0"], "title"=>[$info_comment_this_field, "", ""]]
);



// ------ link wait timeout
$check_link_timeout = new CheckboxTpl("check-link-timeout");
$number_link_timeout = new NumberTplTitle("number-link-timeout", $info_link_timeout);
$number_link_timeout->setMin(0);
$fields = [
    $check_link_timeout, $number_link_timeout
];

$values = [
    (isset($parameters)) ? $parameters['CheckLinkTimeout'] : '',
    (isset($parameters)) ? $parameters['NumberLinkTimeout'] : 3,
];

$f->add(
    new TrFormElement('<label for="check-link-timeout">'._T("Link Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);

// ------ dhcp wait timeout
$check_dhcp_timeout = new CheckboxTpl("check-dhcp-timeout");
$number_dhcp_timeout = new NumberTplTitle("number-dhcp-timeout", $info_dhcp_timeout);
$number_dhcp_timeout->setMin(1);
$fields = [
    $check_dhcp_timeout, $number_dhcp_timeout
];

$values = [
    (isset($parameters)) ? $parameters['CheckDhcpTimeout'] : '',
    (isset($parameters)) ? $parameters['NumberDhcpTimeout'] : 15,
];

$f->add(
    new TrFormElement('<label for="check-dhcp-timeout">'._T("Dhcp Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);


// ------ dhcpV6 wait timeout
$check_dhcpv6_timeout = new CheckboxTpl("check-dhcpv6-timeout");
$number_dhcpv6_timeout = new NumberTplTitle("number-dhcpv6-timeout", $info_dhcp_timeout);
$number_dhcpv6_timeout->setMin(1);
$fields = [
    $check_dhcpv6_timeout, $number_dhcpv6_timeout
];

$values = [
    (isset($parameters)) ? $parameters['CheckDhcpV6Timeout'] : '',
    (isset($parameters)) ? $parameters['NumberDhcpV6Timeout'] : 15,
];

$f->add(
    new TrFormElement('<label for="check-dhcpv6-timeout">'._T("Dhcpv6 Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);



// ---- Disable autoconfig
$check_disable_autoconfig = new CheckboxTpl("check-disable-autoconfig");
$check_disable_autoconfig_value = new CheckboxTpl("check-disable-autoconfig-value");


$fields = [
    $check_disable_autoconfig, $check_disable_autoconfig_value
];

$values = [
    (isset($parameters)) ? $parameters['CheckDisableAutoconfig'] : '',
    (isset($parameters)) ? $parameters['CheckDisableAutoconfigValue'] : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-disable-autoconfig">'._T("Disable Autoconfig", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, $info_disable_autoconfig]]
);


// ---- Disable dhcp
$check_disable_dhcp = new CheckboxTpl("check-disable-dhcp");
$check_disable_dhcp_value = new CheckboxTpl("check-disable-dhcp-value");
$separator = new SpanElement("<br>");
$input_ipaddress = new InputTplTitle("input-get-ipaddress");
$input_netmask = new InputTplTitle("input-get-netmask");
$input_gateway = new InputTplTitle("input-get-gateway");
$input_nameservers = new InputTplTitle("input-get-nameservers");

$fields = [
    $check_disable_dhcp, $check_disable_dhcp_value,
    new SpanElement('<br><label for="input-get-ipaddress">Get Ipaddress</label>'), $input_ipaddress,
    new SpanElement("<br><label for='input-netmask'>Get Netmask</label>"), $input_netmask,
    new SpanElement("<br><label for='input-get-gateway'>Gateway</label>"), $input_gateway,
    new SpanElement("<br><label for='input-get- nameservers'>Nameservers</label>"), $input_nameservers
];

$values = [
    (isset($parameters['CheckDisableDhcp'])) ? $parameters['CheckDisableDhcp'] : '',
    (isset($parameters['CheckDisableDhcpValue'])) ? $parameters['CheckDisableDhcpValue'] : '',
    'input',
    (isset($parameters['InputGetIpaddress'])) ? $parameters['InputGetIpaddress'] : '',
    '',
    (isset($parameters['InputGetNetmask'])) ? $parameters['InputGetNetmask'] : '',
    '',
    (isset($parameters['InputGetGateway'])) ? $parameters['InputGetGateway'] : '',
    '',
    (isset($parameters['InputGetNameservers'])) ? $parameters['InputGetNameservers'] : '',
];

$f->add(
    new TrFormElement('<label for="check-disable-dhcp">'._T("Disable Dhcp", "imaging").'</label>', new multifieldTpl($fields)), [
        "value"=>$values,
        "title"=>[$info_comment_this_field, $info_disable_dhcp, '', '', '', '', '', '', '', '', ''],
        "placeholder"=>['', '', '', 'Ip Address', '', 'Netmask', '', 'Gateway', '', 'Nameservers']]
);



// ---- hostname
$check_hostname = new CheckboxTpl("check-hostname");
$input_hostname = new InputTplTitle("input-hostname", $info_hostname);
$fields = [
    $check_hostname, $input_hostname
];

$values = [
    (isset($parameters)) ? $parameters['CheckHostname'] : '',
    (isset($parameters)) ? $parameters['InputHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-hostname">'._T("Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);



// ---- domain
$check_domain = new CheckboxTpl("check-domaine");
$input_domain = new InputTplTitle("input-domaine", $info_hostname);
$fields = [
    $check_domain, $input_domain
];

$values = [
    (isset($parameters)) ? $parameters['CheckDomaine'] : '',
    (isset($parameters)) ? $parameters['InputDomaine'] : '',
];

$f->add(
    new TrFormElement('<label for="check-domaine">'._T("Domaine", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);

// ---- force-hostname
$check_force_hostname = new CheckboxTpl("check-force-hostname");
$input_force_hostname = new InputTplTitle("input-force-hostname", $info_hostname);
$fields = [
    $check_force_hostname, $input_force_hostname
];

$values = [
    (isset($parameters)) ? $parameters['CheckForceHostname'] : '',
    (isset($parameters)) ? $parameters['InputForceHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-force-hostname">'._T("Force Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);




// ---- dhcp-hostname
$check_dhcp_hostname = new CheckboxTpl("check-dhcp-hostname");
$input_dhcp_hostname = new InputTplTitle("input-dhcp-hostname", $info_dhcp_hostname);
$fields = [
    $check_dhcp_hostname, $input_dhcp_hostname
];

$values = [
    (isset($parameters)) ? $parameters['CheckDhcpHostname'] : '',
    (isset($parameters)) ? $parameters['InputDhcpHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-dhcp-hostname">'._T("Dhcp Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);


// ---- Firmware Lookup
$check = new CheckboxTpl("check-load-firmware");
$input = new CheckboxTpl("check-load-firmware-value");
$fields = [
    $check, $input
];

$values = [
    (isset($parameters)) ? $parameters['CheckLoadFirmware'] : '',
    (isset($parameters)) ? $parameters['CheckLoadFirmwareValue'] : '',
];

$f->add(
    new TrFormElement('<label for="check-load-firmware">'._T("Load Firmware", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_load_firmware]]
);

$f->pop();



// ==== New Section ====
// NETWORK Console
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Network Console","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('NetworkConsole', "imaging"),'')));
$f->push(new Table());


// ---- Network Console
$check = new CheckboxTpl("check-network-console");
$input = new CheckboxTpl("check-network-console-value");
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckNetworkConsole'])) ? $parameters['CheckNetworkConsoleType'] : '',
    (isset($parameters['CheckNetworkConsoleType']) && $parameters['CheckNetworkConsoleType'] == 'false') ? 'checked' : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-network-console">'._T("Network Console", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_network_console]]
);

// ---- authorized_keys_url
$check = new CheckboxTpl("check-authorized-keys-url");
$input = new InputTplTitle("input-authorized-keys-url");
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckAuthorizedKeysUrl'])) ? $parameters['CheckAuthorizedKeysUrl'] : '',
    (isset($parameters['InputAuthorizedKeysUrl'])) ? $parameters['InputAuthorizedKeysUrl'] : '',
];

$f->add(
    new TrFormElement('<label for="check-authorized-keys-url">'._T("Authorized Keys Url", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);


$f->pop();

$f->pop();
$f->display();

echo "<pre id='codeTocopy2' style='width:100%;'></pre>";

?>
