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

<script type="text/javascript">
var template = [
'#________________________________',
'# OS Debian [x86 and amd64]',
'# Preseed :',
'#',
'# date : <? echo $strin; ?>dateval<? echo $strou; ?>',
'#',
'# Installation Notes',
'# Location: <? echo $strin; ?>Location<? echo $strou; ?>',
'# Notes: <? echo $strin; ?>Comments<? echo $strou; ?>',
'# list parameters : @@listParameters@@',
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
'<? echo $strin;?>CheckDisableDhcp<? echo $strou;?>d-i netcfg/dhcp_options boolean <? echo $strin;?>CheckDisableDhcpValue<? echo $strou;?>',
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
'### NETWORK CONSOLE',
'<? echo $strin;?>CheckNetworkConsole<? echo $strou;?>d-i anna/choose_modules <? echo $strin;?>CheckNetworkConsoleType<? echo $strou;?> <? echo $strin;?>CheckNetworkConsoleValue<? echo $strou;?>',
'<? echo $strin;?>CheckAuthorizedKeysUrl<? echo $strou;?>d-i network-console/authorized_keys_url string <? echo $strin;?>InputAuthorizedKeysUrl<? echo $strou;?>',
'',
'### MIRROR',
'<? echo $strin;?>CheckMirrorProtocol<? echo $strou;?>d-i mirror/protocol select <? echo $strin;?>SelectMirrorProtocol<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorProtocol<? echo $strou;?>d-i mirror/http/hostname string <? echo $strin;?>InputMirrorHostname<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorProtocol<? echo $strou;?>d-i mirror/http/directory string <? echo $strin;?>InputMirrorDirectory<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorProtocol<? echo $strou;?>d-i mirror/http/proxy string <? echo $strin;?>InputMirrorProxy<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorCountry<? echo $strou;?>d-i mirror/country string <? echo $strin;?>SelectMirrorCountry<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorSuite<? echo $strou;?>d-i mirror/suite string <? echo $strin;?>InputMirrorSuite<? echo $strou;?>',
'<? echo $strin;?>CheckMirrorSuiteComponents<? echo $strou;?>d-i mirror/udeb/suite string testing <? echo $strin;?>InputMirrorSuiteComponents<? echo $strou;?>',
'',
'### ACCOUNT',
'<?echo $strin;?>CheckSkipRootLogin<? echo $strou;?>d-i passwd/root-login boolean <?echo $strin;?>CheckSkipRootLoginValue<? echo $strou;?>',
'<?echo $strin;?>CheckRootPasswd<? echo $strou;?>d-i passwd/root-password <?echo $strin;?>InputRootPasswd<? echo $strou;?>',
'<? echo $strin;?>CheckMakeUser<? echo $strou;?>d-i passwd/make-user boolean <? echo $strin;?>CheckMakeUserValue<? echo $strou;?>',
'<? echo $strin;?>CheckUserFullname<? echo $strou;?>d-i passwd/user-fullname string <? echo $strin;?>InputUserFullname<? echo $strou;?>',
'<? echo $strin;?>CheckUsername<? echo $strou;?>d-i passwd/username string <? echo $strin;?>InputUsername<? echo $strou;?>',
'<? echo $strin;?>CheckUserPasswd<? echo $strou;?>d-i passwd/user-password password <? echo $strin;?>InputUserPasswd<? echo $strou;?>',
'<? echo $strin;?>CheckUserUid<? echo $strou;?>d-i passwd/user-uid number <? echo $strin;?>NumberUserUid<? echo $strou;?>',
'<? echo $strin;?>CheckUserGroup<? echo $strou;?>d-i passwd/user-default-groups string <? echo $strin;?>InputUserGroup<? echo $strou;?>',
'<? echo $strin;?>CheckUtc<? echo $strou;?>d-i clock-setup/utc boolean <? echo $strin;?>CheckUtcValue<? echo $strou;?>',
'<? echo $strin;?>CheckTimezone<? echo $strou;?>d-i time/zone string <? echo $strin;?>SelectTimezone<? echo $strou;?>',
'<? echo $strin;?>CheckInitPartition<? echo $strou;?>d-i partman-auto/init_automatically_partition select <? echo $strin;?>SelectInitPartition<? echo $strou;?>',
'<? echo $strin;?>CheckLvmSize<? echo $strou;?>d-i partman-auto-lvm/guided_size string <? echo $strin;?>InputLvmSize<? echo $strou;?>',
'<? echo $strin;?>CheckRemoveOldLvm<? echo $strou;?>d-i partman-lvm/device_remove_lvm boolean <? echo $strin;?>CheckRemoveOldLvmValue<? echo $strou;?>',
'<? echo $strin;?>CheckLvmConfirm<? echo $strou;?>d-i partman-lvm/confirm boolean <? echo $strin;?>CheckLvmConfirmValue<? echo $strou;?>',
'<? echo $strin;?>CheckLvmNoOverwrite<? echo $strou;?>d-i partman-lvm/confirm_nooverwrite boolean <? echo $strin;?>CheckLvmNoOverwriteValue<? echo $strou;?>',
'',
'### BASE SYSTEM INSTALLATION',
'<? echo $strin;?>CheckInstallRecommends<? echo $strou;?>d-i base-installer/install-recommends boolean <? echo $strin;?>CheckInstallRecommendsValue<? echo $strou;?>',
'<? echo $strin;?>CheckKernelImage<? echo $strou;?>d-i base-installer/kernel/image string <? echo $strin;?>InputKernelImage<? echo $strou;?>',
'',
'### APT SETUP',
'<? echo $strin;?>CheckSetFirst<? echo $strou;?>d-i apt-setup/cdrom/set-first boolean <? echo $strin;?>CheckSetFirstValue<? echo $strou;?>',
'<? echo $strin;?>CheckNonFreeFirmware<? echo $strou;?>d-i apt-setup/non-free-firmware boolean <? echo $strin;?>CheckNonFreeFirmwareValue<? echo $strou;?>',
'<? echo $strin;?>CheckNonFree<? echo $strou;?>d-i apt-setup/non-free boolean <? echo $strin;?>CheckNonFreeValue<? echo $strou;?>',
'<? echo $strin;?>CheckContrib<? echo $strou;?>d-i apt-setup/contrib boolean <? echo $strin;?>CheckContribValue<? echo $strou;?>',
'<? echo $strin;?>CheckDisableCdrom<? echo $strou;?>d-i apt-setup/disable-cdrom-entries boolean <? echo $strin;?>CheckDisableCdromValue<? echo $strou;?>',
'<? echo $strin;?>CheckUseMirror<? echo $strou;?>d-i apt-setup/use_mirror boolean <? echo $strin;?>CheckUseMirrorValue<? echo $strou;?>',
'<? echo $strin;?>CheckServicesSelect<? echo $strou;?>d-i apt-setup/services-select string <? echo $strin;?>InputServicesSelect<? echo $strou;?>',
'<? echo $strin;?>CheckSecurityHost<? echo $strou;?>d-i apt-setup/security_host string <? echo $strin;?>InputSecurityHost<? echo $strou;?>',
'<? echo $strin;?>CheckAddRepo<? echo $strou;?>d-i apt-setup/local0/repository string <? echo $strin;?>InputAddRepo<? echo $strou;?>',
'<? echo $strin;?>CheckAddComment<? echo $strou;?>d-i additional_comment string <? echo $strin;?>InputAddComment<? echo $strou;?>',
'<? echo $strin;?>CheckAddSource<? echo $strou;?>d-i apt-setup/local0/source boolean <? echo $strin;?>CheckAddSourceValue<? echo $strou;?>',
'<? echo $strin;?>CheckAddKey<? echo $strou;?>d-i apt-setup/local0/key string <? echo $strin;?>InputAddKey<? echo $strou;?>',
'<? echo $strin;?>CheckAllowUnauth<? echo $strou;?>d-i debian-installer/allow_unauthenticated boolean <? echo $strin;?>CheckAllowUnauthValue<? echo $strou;?>',
'<? echo $strin;?>CheckMultiArch<? echo $strou;?>d-i apt-setup/multiarch string <? echo $strin;?>InputMultiArch<? echo $strou;?>',
'',
'### PACKAGE SELECTION',
'<? echo $strin;?>CheckTasksel<? echo $strou;?>tasksel tasksel/first multiselect <? echo $strin;?>InputTasksel<? echo $strou;?>',
'<? echo $strin;?>CheckRunTasksel<? echo $strou;?>d-i pkgsel/run_tasksel string <? echo $strin;?>InputRunTasksel<? echo $strou;?>',
'<? echo $strin;?>CheckInclude<? echo $strou;?>d-i pkgsel/include string <? echo $strin;?>InputInclude<? echo $strou;?>',
'<? echo $strin;?>CheckUpgrade<? echo $strou;?>d-i pkgsel/upgrade select <? echo $strin;?>SelectUpgrade<? echo $strou;?>',
'<? echo $strin;?>CheckContest<? echo $strou;?>popularity-contest popularity-contest/participate boolean <? echo $strin;?>CheckContestValue<? echo $strou;?>',
'',
'### BOOT LOADER',
'<? echo $strin;?>CheckDebian<? echo $strou;?>d-i grub-installer/only_debian boolean <? echo $strin;?>CheckDebianValue<? echo $strou;?>',
'<? echo $strin;?>CheckMulti<? echo $strou;?>d-i grub-installer/with_other_os boolean <? echo $strin;?>CheckMultiValue<? echo $strou;?>',
'',
'### FINISHING',
'<? echo $strin;?>CheckKeepConsoles<? echo $strou;?>d-i finish-install/keep-consoles boolean <? echo $strin;?>CheckKeepConsolesValue<? echo $strou;?>',
'<? echo $strin;?>CheckRebootInProgress<? echo $strou;?>d-i finish-install/reboot_in_progress boolean <? echo $strin;?>CheckRebootInProgressValue<? echo $strou;?>',
'<? echo $strin;?>CheckEjectCdrom<? echo $strou;?>d-i cdrom-detect/eject boolean <? echo $strin;?>CheckEjectCdromValue<? echo $strou;?>',
'<? echo $strin;?>CheckReboot<? echo $strou;?>d-i debian-installer/exit/halt boolean <? echo $strin;?>CheckRebootValue<? echo $strou;?>',
'<? echo $strin;?>CheckPoweroff<? echo $strou;?>d-i debian-installer/exit/poweroff boolean <? echo $strin;?>CheckPoweroffValue<? echo $strou;?>',
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

// Try to retrieve parameters from somewhere
if(isset($_SESSION['parameters']))
{//If this session exists : editing file, else creating file
    $parameters = $_SESSION['parameters'];
}
else if(isset($_POST["Location"])){
    $parameters = $_POST;
}
else{
    // By default define $parameters as empty
    $parameters = [];
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
    array("required" => True,'value'=>(isset($parameters['Title'])) ? htmlentities($parameters['Title']) : '')
);
//_____________
$f->add(new TrFormElement("Notes".":", new OptTextareaTpl(array('name'=>'Comments','value'=>(isset($parameters['Notes'])) ? htmlentities($parameters['Notes']) : _T('Enter your comments here...','imaging')))));
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
$check = new CheckboxTpl("check-locale");
$select = new SelectItemtitle("select-locale", $info_locale_settings);
$select->setElements($locales_country);
$select->setElementsVal($locales_values);


$fields = [
    $check, $select
];

$values = [
    (isset($parameters['CheckLocale'])) ? ($parameters['CheckLocale'] == '' ? 'checked': '') : '',
    (isset($parameters['SelectLocale'])) ? $parameters['SelectLocale'] : '',
];

$f->add(
    new TrFormElement('<label for="check-locale">'._T("locale", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);

// ---- language
$check = new CheckboxTpl("check-language");
$select = new SelectItemtitle("select-language", $info_locale_settings);
$select->setElements($languages_country);
$select->setElementsVal($languages_values);

$fields = [
    $check, $select
];

$values = [
    (isset($parameters['CheckLanguage'])) ? ($parameters['CheckLanguage'] == '' ? 'checked' : '') : '',
    (isset($parameters['SelectLanguage'])) ? $parameters['SelectLanguage'] : '',
];

$f->add(
    new TrFormElement('<label for="check-language">'._T("language", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);


// ---- country
$check = new CheckboxTpl("check-country");
$select = new SelectItemtitle("select-country", $info_locale_settings);
$select->setElements($countries_country);
$select->setElementsVal($countries_values);


$fields = [
    $check, $select
];

$values = [
    (isset($parameters['CheckCountry'])) ? ($parameters['CheckCountry'] == '' ? 'checked' : '') : '',
    (isset($parameters['SelectCountry'])) ? $parameters['SelectCountry'] : '',
];

$f->add(
    new TrFormElement('<label for="check-country">'._T("Country", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);


// ---- supported locales
$check = new CheckboxTpl("check-supported-locales");
$select = new SelectItemtitle("select-supported-locales", $info_supported_locales);
$select->setElements($supported_locales);
$select->setElementsVal($supported_locales_values);

$fields = [
    $check, $select
];

$values = [
    (isset($parameters['CheckSupportedLocales'])) ? ($parameters['CheckSupportedLocales'] == '' ? 'checked' : '') : '',
    (isset($parameters['SelectSupportedLocales'])) ? $parameters['SelectSupportedLocales'] : '',
];

$f->add(
    new TrFormElement('<label for="check-supported-locales">'._T("Supported Locales", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);


// ---- keyboard layout
$check = new CheckboxTpl("check-keyboard-layouts");
$select = new SelectItemtitle("select-keyboard-layouts", "");
$select->setElements($keyboard_layouts);
$select->setElementsVal($keyboard_layouts_values);


$fields = [
    $check, $select
];

$values = [
    (isset($parameters['check-keyboard-layouts'])) ? ($parameters['check-keyboard-layouts'] == '' ? 'checked' : '') : '',
    (isset($parameters['select-keyboard-layouts'])) ? $parameters['select-keyboard-layouts'] : '',
];

$f->add(
    new TrFormElement('<label for="check-keyboard-layouts">'._T("Keyboard Layout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);


// ---- keyboard layout
$check = new CheckboxTpl("check-keyboard-toggle");
$select = new SelectItemtitle("select-keyboard-toggle", "");
$select->setElements($keyboard_toggles);
$select->setElementsVal($keyboard_toggles);

$fields = [
    $check, $select
];

$values = [
    (isset($parameters['CheckKeyboardToggle'])) ? ($parameters['CheckKeyboardToggle'] == '' ? 'checked' : '') : '',
    (isset($parameters['SelectKeyboardToggle'])) ? $parameters['SelectKeyboardToggle'] : '',
];

$f->add(
    new TrFormElement('<label for="check-keyboard-toggle">'._T("Keyboard Toggle", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select);
$f->pop();


// ==== New Section ====
// NETWORK
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Network","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Network', "imaging"),'')));
$f->push(new Table());

// ---- keyboard layout
$check = new CheckboxTpl("check-enable-network");
$checkValue = new CheckboxTpl("check-enable-network-value", "");

$fields = [
    $check, $checkValue
];

$values = [
    (isset($parameters['CheckEnableNetwork'])) ? ($parameters['CheckEnableNetwork'] == '' ? 'checked' : '') : '',
    (isset($parameters['CheckEnableNetworkValue'])) ? ($parameters['CheckEnableNetworkValue'] == 'true' ? 'checked' : '') : '',
];

$f->add(
    new TrFormElement('<label for="check-enable-network">'._T("Enable Network", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, $info_enable_network]]
);
unset($check, $checkValue);


// ---- Interface
$check = new CheckboxTpl("check-interface");
$select = new SelectItemtitle("select-interface", $info_interface);
$select->setElements($interface_choices);
$select->setElementsVal($interface_choices);

$input = new InputTplTItle("input-interface", $info_interface);

$fields = [
    $check, $select, $input
];

$values = [
    (isset($parameters['CheckInterface'])) ? ($parameters['CheckInterface'] == '' ? 'checked' : '') : '',
    (isset($parameters['SelectInterface'])) ? $parameters['SelectInterface'] : '',
    (isset($parameters['InputInterface']) && $parameters['InputInterface'] != 'auto') ? $parameters['InputInterface'] : 'eth0',
];

$f->add(
    new TrFormElement('<label for="check-interface">'._T("Interface", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "placeholder"=>["", "", "eth0"], "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $select, $input);



// ------ link wait timeout
$check = new CheckboxTpl("check-link-timeout");
$number = new NumberTplTitle("number-link-timeout", $info_link_timeout);
$number->setMin(0);
$fields = [
    $check, $number
];

$values = [
    (isset($parameters['CheckLinkTimeout'])) ? ($parameters['CheckLinkTimeout'] == '' ? 'checked' : '') : '',
    (isset($parameters['NumberLinkTimeout'])) ? $parameters['NumberLinkTimeout'] : 3,
];

$f->add(
    new TrFormElement('<label for="check-link-timeout">'._T("Link Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $number);

// ------ dhcp wait timeout
$check_dhcp_timeout = new CheckboxTpl("check-dhcp-timeout");
$number_dhcp_timeout = new NumberTplTitle("number-dhcp-timeout", $info_dhcp_timeout);
$number_dhcp_timeout->setMin(1);
$fields = [
    $check_dhcp_timeout, $number_dhcp_timeout
];

$values = [
    (isset($parameters['CheckDhcpTimeout'])) ? ($parameters['CheckDhcpTimeout'] == '' ? 'checked' : '') : '',
    (isset($parameters['NumberDhcpTimeout'])) ? $parameters['NumberDhcpTimeout'] : 15,
];

$f->add(
    new TrFormElement('<label for="check-dhcp-timeout">'._T("Dhcp Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);


// ------ dhcpV6 wait timeout
$check = new CheckboxTpl("check-dhcpv6-timeout");
$number = new NumberTplTitle("number-dhcpv6-timeout", $info_dhcp_timeout);
$number->setMin(1);
$fields = [
    $check, $number
];

$values = [
    (isset($parameters['CheckDhcpV6Timeout'])) ? ($parameters['CheckDhcpV6Timeout'] == '' ? 'checked' : '') : '',
    (isset($parameters['NumberDhcpV6Timeout'])) ? $parameters['NumberDhcpV6Timeout'] : 15,
];

$f->add(
    new TrFormElement('<label for="check-dhcpv6-timeout">'._T("Dhcpv6 Wait Timeout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, "", ""]]
);
unset($check, $number);


// ---- Disable autoconfig
$check = new CheckboxTpl("check-disable-autoconfig");
$checkValue = new CheckboxTpl("check-disable-autoconfig-value");


$fields = [
    $check, $checkValue
];

$values = [
    (isset($parameters['CheckDisableAutoconfig'])) ? ($parameters['CheckDisableAutoconfig'] == '' ? 'checked' : '') : '',
    (isset($parameters['CheckDisableAutoconfigValue'])) ? ($parameters['CheckDisableAutoconfigValue'] == 'true' ? 'checked' : '') : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-disable-autoconfig">'._T("Disable Autoconfig", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>[$info_comment_this_field, $info_disable_autoconfig]]
);
unset($check, $checkValue);

// ---- Disable dhcp
$check = new CheckboxTpl("check-disable-dhcp");
$checkValue = new CheckboxTpl("check-disable-dhcp-value");
$separator = new SpanElement("<br>");
$input_ipaddress = new InputTplTitle("input-get-ipaddress");
$input_netmask = new InputTplTitle("input-get-netmask");
$input_gateway = new InputTplTitle("input-get-gateway");
$input_nameservers = new InputTplTitle("input-get-nameservers");

$fields = [
    $check, $checkValue,
    new SpanElement('<br><label for="input-get-ipaddress">Get Ipaddress</label>'), $input_ipaddress,
    new SpanElement("<br><label for='input-get-netmask'>Get Netmask</label>"), $input_netmask,
    new SpanElement("<br><label for='input-get-gateway'>Gateway</label>"), $input_gateway,
    new SpanElement("<br><label for='input-get-nameservers'>Nameservers</label>"), $input_nameservers
];

$values = [
    (isset($parameters['CheckDisableDhcp'])) ? ($parameters['CheckDisableDhcp'] == '' ? 'checked' : '') : '',
    (isset($parameters['CheckDisableDhcpValue'])) ? ($parameters['CheckDisableDhcpValue'] == 'true' ? 'checked' : '') : '',
    '',
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
unset($check, $checkValue, $input_hostname, $separator, $input_ipaddress, $input_netmask, $input_gateway, $input_nameservers);


// ---- hostname
$check = new CheckboxTpl("check-hostname");
$input = new InputTplTitle("input-hostname", $info_hostname);
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckHostname'])) ? $parameters['CheckHostname'] : '',
    (isset($parameters['InputHostname'])) ? $parameters['InputHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-hostname">'._T("Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);
unset($check, $input);


// ---- domain
$check = new CheckboxTpl("check-domaine");
$input = new InputTplTitle("input-domaine", $info_hostname);
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckDomaine'])) ? ($parameters['CheckDomaine'] == '' ? 'checked' : '') : '',
    (isset($parameters['InputDomaine'])) ? $parameters['InputDomaine'] : '',
];

$f->add(
    new TrFormElement('<label for="check-domaine">'._T("Domaine", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);

// ---- force-hostname
$check = new CheckboxTpl("check-force-hostname");
$input = new InputTplTitle("input-force-hostname", $info_hostname);
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckForceHostname'])) ? ($parameters['CheckForceHostname'] == '' ? 'checked' : '') : '',
    (isset($parameters['InputForceHostname'])) ? $parameters['InputForceHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-force-hostname">'._T("Force Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);
unset($check, $input);

// ---- dhcp-hostname
$check = new CheckboxTpl("check-dhcp-hostname");
$input = new InputTplTitle("input-dhcp-hostname", $info_dhcp_hostname);
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckDhcpHostname'])) ? ($parameters['CheckDhcpHostname'] == '' ? 'checked' : '') : '',
    (isset($parameters['InputDhcpHostname'])) ? $parameters['InputDhcpHostname'] : '',
];

$f->add(
    new TrFormElement('<label for="check-dhcp-hostname">'._T("Dhcp Hostname", "imaging").'</label>', new multifieldTpl($fields)), ["title"=>[$info_comment_this_field, '' ], "value" => $values]
);
unset($check, $input);


// ---- Firmware Lookup
$check = new CheckboxTpl("check-load-firmware");
$input = new CheckboxTpl("check-load-firmware-value");
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckLoadFirmware'])) ? ($parameters['CheckLoadFirmware'] == '' ? 'checked' : '') : '',
    (isset($parameters['CheckLoadFirmwareValue'])) ? $parameters['CheckLoadFirmwareValue'] : '',
];

$f->add(
    new TrFormElement('<label for="check-load-firmware">'._T("Load Firmware", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_load_firmware]]
);
unset($check, $input);

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
$checkValue = new CheckboxTpl("check-network-console-value");
$fields = [
    $check, $checkValue
];

$values = [
    (isset($parameters['CheckNetworkConsole'])) ? ($parameters['CheckNetworkConsoleType'] == '' ? 'checked' : '') : '',
    (isset($parameters['CheckNetworkConsoleType'])) ? ($parameters['CheckNetworkConsoleType'] == 'true' ? 'checked' : '') : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-network-console">'._T("Network Console", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_network_console]]
);
unset($check, $checkValue);

// ---- authorized_keys_url
$check = new CheckboxTpl("check-authorized-keys-url");
$input = new InputTplTitle("input-authorized-keys-url");
$fields = [
    $check, $input
];

$values = [
    (isset($parameters['CheckAuthorizedKeysUrl'])) ? ($parameters['CheckAuthorizedKeysUrl'] == '' ? 'checked' : '') : '',
    (isset($parameters['InputAuthorizedKeysUrl'])) ? $parameters['InputAuthorizedKeysUrl'] : '',
];

$f->add(
    new TrFormElement('<label for="check-authorized-keys-url">'._T("Authorized Keys Url", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);
unset($check, $input);


$f->pop();


// ==== New Section ====
// Mirror
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Mirror","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Mirror', "imaging"),'')));
$f->push(new Table());


// ---- mirror protocol
$check = new CheckboxTpl("check-mirror-protocol");
$separator = new SpanElement("<br>");

$select = new SelectItemTitle("select-mirror-protocol", $info_mirror_protocol);
$select->setElements($mirror_protocol_values);
$select->setElementsVal($mirror_protocol_values);

$input_mirror_hostname = new InputTplTitle("input-mirror-hostname");
$input_mirror_directory = new InputTplTitle("input-mirror-directory");
$input_mirror_proxy = new InputTplTitle("input-mirror-proxy");

$fields = [
    $check,
    new SpanElement('<br><label for="select-mirror-protocol">Protocol</label>'), $select,
    new SpanElement("<br><label for='input-mirror-hostname'>Hostname</label>"), $input_mirror_hostname,
    new SpanElement("<br><label for='input-mirror-directory'>Directory</label>"), $input_mirror_directory,
    new SpanElement("<br><label for='input-mirror-proxy'>Proxy</label>"), $input_mirror_proxy
];

$values = [
    (isset($parameters['CheckMirrorProtocol'])) ? ($parameters['CheckMirrorProtocol'] == '' ? 'checked' : 'checked') : '',
    '',
    (isset($parameters['SelectMirrorProtocol'])) ? $parameters['SelectMirrorProtocol'] : 'html',
    '',
    (isset($parameters['InputMirrorHostname'])) ? $parameters['InputMirrorHostname'] : '',
    '',
    (isset($parameters['InputMirrorDirectory'])) ? $parameters['InputMirrorDirectory'] : '',
    '',
    (isset($parameters['InputMirrorProxy'])) ? $parameters['InputMirrorProxy'] : '',
];

$f->add(
    new TrFormElement('<label for="check-mirror-protocol">'._T("Mirror Protocol", "imaging").'</label>', new multifieldTpl($fields)), [
        "value"=>$values,
        "title"=>[$info_comment_this_field, '', '', '', '', '', '', '', '', '', ''],
        "placeholder"=>['', '', '', 'Ip Address', '', 'Netmask', '', 'Gateway', '', 'Nameservers']]
);
unset($check, $separator, $select, $input_mirror_hostname, $input_mirror_directory, $input_mirror_proxy);


// ---- mirror country
$check = new CheckboxTpl("check-mirror-country");
$select = new SelectItemtitle("select-mirror-country");
$select->setElements($mirror_countries);
$select->setElementsVal($mirror_countries_values);

$fields = [ $check, $select];
$values = [
    (isset($parameters["CheckMirrorCountry"])) ? ($parameters["CheckMirrorCountry"] == '' ? 'checked' : '') : '',
    (isset($parameters["SelectMirrorCountry"])) ? $parameters["SelectMirrorCountry"] : 'manual',
];

$f->add(
    new TrFormElement('<label for="check-mirror-country">'._T("Mirror Country", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);
unset($check, $select);

// ---- mirror suite
$check = new CheckboxTpl("check-mirror-suite");
$input = new InputTplTitle("input-mirror-suite", _T("Suite to install", "imaging"));


$fields = [ $check, $input];
$values = [
    (isset($parameters["CheckMirrorSuite"])) ? ($parameters["CheckMirrorSuite"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputMirrorSuite"])) ? $parameters["InputMirrorSuite"] : 'stable',
];

$f->add(
    new TrFormElement('<label for="check-mirror-suite">'._T("Mirror Suite", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);
unset($check, $input);

// ---- mirror suite components
$check = new CheckboxTpl("check-mirror-suite-components");
$input = new InputTplTitle("input-mirror-suite-components", _T("Suite to use for loading installer components (optional).", "imaging"));


$fields = [ $check, $input];
$values = [
    (isset($parameters["CheckMirrorSuiteComponents"])) ? ($parameters["CheckMirrorSuiteComponents"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputMirrorSuiteComponents"])) ? $parameters["InputMirrorSuiteComponents"] : 'stable',
];

$f->add(
    new TrFormElement('<label for="check-mirror-suite-components">'._T("Mirror Suite Components", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);
unset($check, $input);

$f->pop(); // End of Section


// ==== New Section ====
// Accounts
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Accounts","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Accounts', "imaging"),'')));
$f->push(new Table());

// ---- skip root login
$check = new CheckboxTpl("check-skip-root-login");
$checkValue = new CheckboxTpl("check-skip-root-login-value");


$fields = [ $check, $checkValue];
$values = [
    (isset($parameters["CheckSkipRootLogin"])) ? ($parameters["CheckSkipRootLogin"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckSkipRootLoginValue"])) ? ($parameters["CheckSkipRootLoginValue"] == 'true' ? 'checked' : '') : '',
];

$f->add(
    new TrFormElement('<label for="check-skip-root-login">'._T("Skip Root Login", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Skip creation of a root account (normal user account will be able to use sudo).", "imaging")]]
);
unset($check, $checkValue);

// ---- root password
$check = new CheckboxTpl("check-root-passwd");
$input = new InputTplTitle("input-root-passwd", "");
$input->fieldType = "password";

$fields = [ $check, $input];
$values = [
    (isset($parameters["CheckRootPasswd"])) ? ($parameters["CheckRootPasswd"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputRootPasswd"])) ? $parameters["InputRootPasswd"] : '',
];

$f->add(
    new TrFormElement('<label for="check-root-passwd">'._T("Root Password", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $input);


// ---- skip make user
$check = new CheckboxTpl("check-makeuser");
$input = new CheckboxTpl("check-makeuser-value");
$fields = [$check, $input];
$values = [
    (isset($parameters["CheckMakeuser"])) ? ($parameters["CheckMakeuserValue"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["CheckMakeuserValue"])) ? (($parameters["CheckMakeuserValue"] == 'true') ? 'checked' : '') : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-makeuser">'._T("Make user", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Skip creation of normal user account.", "imaging"), ]]
);
unset($check, $input);

// ---- user-fullname
$check = new CheckboxTpl("check-user-fullname");
$input = new InputTplTitle("input-user-fullname", "");
$fields = [$check, $input];
$values = [
    (isset($parameters["CheckUserFullname"])) ? ($parameters["CheckUserFullname"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputUserFullName"])) ? $parameters["InputUserFullName"] : '',
];

$f->add(
    new TrFormElement('<label for="check-user-fullname">'._T("User Fullname", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $input);

// ---- user-username
$check = new CheckboxTpl("check-username");
$input = new InputTplTitle("input-username", "");
$fields = [$check, $input];
$values = [
    (isset($parameters["CheckUsername"])) ? ($parameters["CheckUsername"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputUsername"])) ? $parameters["InputUsername"] : '',
];

$f->add(
    new TrFormElement('<label for="check-username">'._T("User Name", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $input);


// ---- user-password
$check = new CheckboxTpl("check-user-passwd");
$input = new InputTplTitle("input-user-passwd", "");
$fields = [$check, $input];
$values = [
    (isset($parameters["CheckUserPasswd"])) ? $parameters["CheckUserPasswd"] : '',
    (isset($parameters["InputUserPasswd"])) ? $parameters["InputUserPasswd"] : '',
];

$f->add(
    new TrFormElement('<label for="check-user-passwd">'._T("User Password", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $input);

// ---- user-uid
$check = new CheckboxTpl("check-user-uid");
$number = new NumberTplTitle("number-user-uid", _T("Create the first user with the specified UID instead of the default.", "imaging"));

$fields = [$check, $number];
$values = [
    (isset($parameters["CheckUserUid"])) ? $parameters["CheckUserUid"] : '',
    (isset($parameters["NumberUserUid"])) ? $parameters["NumberserUid"] : '',
];

$f->add(
    new TrFormElement('<label for="check-user-uid">'._T("User Uid", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $number);

// ---- user-default-group
$check = new CheckboxTpl("check-user-group");
$input = new InputTplTitle("input-user-group", _T("The user account will be added to some standard initial groups. To override that, use this.", "imaging"));

$fields = [$check, $input];
$values = [
    (isset($parameters["CheckUserGroup"])) ? ($parameters["CheckUserGroup"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputUserGroup"])) ? $parameters["InputUserGroup"] : '',
];

$f->add(
    new TrFormElement('<label for="check-user-group">'._T("User Group", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "", ]]
);
unset($check, $input);


$f->pop();

// ==== New Section ====
// Timezone
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Timezone","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Timezone', "imaging"),'')));
$f->push(new Table());


// ---- UTC
$check = new CheckboxTpl("check-utc");
$checkValue = new CheckboxTpl("check-utc-value");

$fields = [$check, $checkValue];
// $parameters['CheckUtcValue'] = 'true';
$values = [
    (isset($parameters["CheckUtc"])) ? ($parameters["CheckUtc"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckUtcValue"])) ? ($parameters['CheckUtcValue'] == 'true' ? 'checked' : '') : 'checked',
];

$f->add(
    new TrFormElement('<label for="check-utc">'._T("Utc", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Controls whether or not the hardware clock is set to UTC.", "imaging"), ]]
);
unset($check, $checkValue);

// ---- Timezone
$check = new CheckboxTpl("check-timezone");
$select = new SelectItemtitle("select-timezone");
$select->setElements($timezones);
$select->setElementsVal($timezones);

$fields = [$check, $select];
$values = [
    (isset($parameters["CheckTimezone"])) ? ($parameters["CheckTimezone"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["SelectTimezone"])) ? $parameters['SelectTimezone'] : date_default_timezone_get(),
];

$f->add(
    new TrFormElement('<label for="check-timezone">'._T("Timezone", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "" ]]
);
unset($check, $select);


$f->pop();

// ==== New Section ====
// Partitionning
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Partitionning","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Partitionning', "imaging"),'')));
$f->push(new Table());

// ---- init-partition
$check = new CheckboxTpl("check-init-partition");
$select = new SelectItemtitle("select-init-partition", $info_init_partition);
$select->setElements([_T("All", "imaging"), _T("True", "imaging"), _T("False", "imaging")]);
$select ->setElementsVal(["all", "true", "false"]);

$values = [
    (isset($parameters["CheckInitPartition"])) ? ($parameters["CheckInitPartition"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["SelectInitPartition"])) ? $parameters["SelectInitPartition"] : 'all',
];
$fields = [$check, $select];

$f->add(
    new TrFormElement('<label for="check-init-partition">'._T("Init automatically partition", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "" ]]
);
unset($check, $select);


// ---- lvm-size
$check = new CheckboxTpl("check-lvm-size");
$input = new InputTplTitle("input-lvm-size", $info_lvm_size);

$values = [
    (isset($parameters["CheckLvmSize"])) ? ($parameters["CheckLvmSize"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputLvmSize"])) ? $parameters["InputLvmSize"] : 'max',
];
$fields = [$check, $input];

$f->add(
    new TrFormElement('<label for="check-lvm-size">'._T("LVM size", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, "" ]]
);
unset($check, $input);

// ---- remove-old-lvm
$check = new CheckboxTpl("check-remove-old-lvm");
$checkValue = new CheckboxTpl("check-remove-old-lvm-value");

$values = [
    (isset($parameters["CheckRemoveOldLvm"])) ? ($parameters["CheckRemoveOldLvm"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckRemoveOldLvmValue"])) ? ($parameters["CheckRemoveOldLvmValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-remove-old-lvm">'._T("Remove Old LVM", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_remove_old_lvm]]
);
unset($check, $checkValue);

// ---- lvm-confirm
$check = new CheckboxTpl("check-lvm-confirm");
$checkValue = new CheckboxTpl("check-lvm-confirm-value");

$values = [
    (isset($parameters["CheckLvmConfirm"])) ? ($parameters["CheckLvmConfirm"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["CheckLvmConfirmValue"])) ? ($parameters["CheckLvmConfirmValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-lvm-confirm">'._T("Confirm LVM", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Confirm to write LVM partitions", "imaging")]]
);
unset($check, $checkValue);

// ---- lvm-nooverwrite
$check = new CheckboxTpl("check-lvm-nooverwrite");
$checkValue = new CheckboxTpl("check-lvm-nooverwrite-value");

$values = [
    (isset($parameters["CheckLvmNoOverwrite"])) ? ($parameters["CheckLvmNoOverwrite"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["CheckLvmNoOverwriteValue"])) ? ($parameters["CheckLvmNoOverwriteValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-lvm-nooverwrite">'._T("Confirm LVM no overwrite", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("And the same goes for the confirmation to write the lvm partitions.", "imaging")]]
);
unset($check, $checkValue);

$f->pop();



// ==== New Section ====
// Base System Installation
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Base system installation","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('BaseSystemInstallation', "imaging"),'')));
$f->push(new Table());


// ---- install-recommends
$check = new CheckboxTpl("check-install-recommends");
$checkValue = new CheckboxTpl("check-install-recommends-value");

$values = [
    (isset($parameters["CheckInstallRecommends"])) ? ($parameters["CheckInstallRecommends"] == '' ? 'checked' : '') : 'checked',
    (isset($parameters["CheckInstallRecommendsValue"])) ? ($parameters["CheckInstallRecommendsValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-install-recommends">'._T("Install Recommends", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_install_recommends]]
);
unset($check, $checkValue);


// ---- kernel-image
$check = new CheckboxTpl("check-kernel-image");
$input = new InputTplTitle("input-kernel-image", _T("The kernel image (meta) package to be installed; \"none\" can be used if no kernel is to be installed.", "imaging"));

$values = [
    (isset($parameters["CheckKernelImage"])) ? ($parameters["CheckKernelImage"] == '' ? 'checked' : '') : '',
    (isset($parameters["InputKernelImage"])) ? $parameters["InputKernelImage"] : '',
];
$fields = [$check, $input];

$f->add(
    new TrFormElement('<label for="check-kernel-image">'._T("Kernel image", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, '']]
);
unset($check, $input);
$f->pop();


// ==== New Section ====
// Apt Setup
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Apt Setup","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Aptsetup', "imaging"),'')));
$f->push(new Table());


// ---- set first
$check = new CheckboxTpl("check-set-first");
$checkValue = new CheckboxTpl("check-set-first-value");

$values = [
    (isset($parameters["CheckSetFirst"])) ? ($parameters["CheckSetFirst"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckSetFirstValue"])) ? ($parameters["CheckSetFirstValue"] == 'true' ? 'checked' : '') : '',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-set-first">'._T("Set First", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Choose, if you want to scan additional installation media (default: false).", "imaging")]]
);
unset($check, $checkValue);


// ---- non free firmware
$check = new CheckboxTpl("check-non-free-firmware");
$checkValue = new CheckboxTpl("check-non-free-firmware-value");

$values = [
    (isset($parameters["CheckNonFreeFirmware"])) ? ($parameters["CheckNonFreeFirmware"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckNonFreeFirmwareValue"])) ? ($parameters["CheckNonFreeFirmwareValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-non-free-firmware">'._T("Non Free Firmware", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("You can choose to install non-free firmware.", "imaging")]]
);
unset($check, $checkValue);

// ---- non free
$check = new CheckboxTpl("check-non-free");
$checkValue = new CheckboxTpl("check-non-free-value");

$values = [
    (isset($parameters["CheckNonFree"])) ? ($parameters["CheckNonFree"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckNonFreeValue"])) ? ($parameters["CheckNonFreeValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-non-free">'._T("Non Free", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("You can choose to install non-free software.", "imaging")]]
);
unset($check, $checkValue);


// ---- contrib
$check = new CheckboxTpl("check-contrib");
$checkValue = new CheckboxTpl("check-contrib-value");

$values = [
    (isset($parameters["CheckContrib"])) ? ($parameters["CheckContrib"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckContribValue"])) ? ($parameters["CheckContribValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-contrib">'._T("Contrib", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("You can choose to install contrib software.", "imaging")]]
);
unset($check, $checkValue);


// ---- disable cdrom entries
$check = new CheckboxTpl("check-disable-cdrom");
$checkValue = new CheckboxTpl("check-disable-cdrom-value");

$values = [
    (isset($parameters["CheckDisableCdrom"])) ? ($parameters["CheckDisableCdrom"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckDisableCdromValue"])) ? ($parameters["CheckDisableCdromValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-disable-cdrom">'._T("Disable Cdrom Entries", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_disable_cdrom]]
);
unset($check, $checkValue);



// ---- use mirror
$check = new CheckboxTpl("check-use-mirror");
$checkValue = new CheckboxTpl("check-use-mirror-value");

$values = [
    (isset($parameters["CheckUseMirror"])) ? ($parameters["CheckUseMirror"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckUseMirrorValue"])) ? ($parameters["CheckUseMirrorValue"] == 'true' ? 'checked' : '') : '',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-use-mirror">'._T("Use Mirror", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("If you don't want to use a network mirror", "imaging")]]
);
unset($check, $checkValue);


// ---- services-select
$check = new CheckboxTpl("check-services-select");
$input = new InputTplTitle("input-services-select", $info_services_select );

$values = [
    (isset($parameters["CheckServicesSelect"])) ? ($parameters["CheckServicesSelect"] == "" ? "checked" : "") : "",
    "multiselect security, updates"
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-services-select">'._T("Service Select", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $input);

// ---- security-host
$check = new CheckboxTpl("check-security-host");
$input = new InputTplTitle("input-security-host", "" );

$values = [
    (isset($parameters["CheckSecurityHost"])) ? ($parameters["CheckSecurityHost"] == "" ? "checked" : "") : "",
    "security.debian.org"
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-security-host">'._T("Security Host", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $input);

// ---- add-repo
$check = new CheckboxTpl("check-add-repo");
$input = new InputTplTitle("input-add-repo", "" );

$values = [
    (isset($parameters["CheckAddRepo"])) ? ($parameters["CheckAddRepo"] == "" ? "checked" : "") : "",
    ""
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-add-repo">'._T("Additionnal Repositories", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $input);


// ---- add-comment
$check = new CheckboxTpl("check-add-comment");
$input = new InputTplTitle("input-add-comment", "" );

$values = [
    (isset($parameters["CheckAddComment"])) ? ($parameters["CheckAddComment"] == "" ? "checked" : "") : "",
    ""
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-add-comment">'._T("Additionnal Comment", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $input);


// ---- add-source
$check = new CheckboxTpl("check-add-source");
$checkValue = new CheckboxTpl("check-add-source-value");

$values = [
    (isset($parameters["CheckAddSource"])) ? ($parameters["CheckAddSource"] == "" ? "checked" : "") : "",
    (isset($parameters["CheckAddSourceValue"])) ? ($parameters["CheckAddSourceValue"] == "true" ? "checked" : "") : "",
];
$fields = [$check, $checkValue];
$f->add(
    new TrFormElement('<label for="check-add-source">'._T("Additionnal Source", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, _T("Enable deb-src lines", "imaging")]]
);
unset($check, $checkValue);

// ---- add-key
$check = new CheckboxTpl("check-add-key");
$input = new InputTplTitle("input-add-key", $info_add_key);

$values = [
    (isset($parameters["CheckAddKey"])) ? ($parameters["CheckAddKey"] == "" ? "checked" : "") : "",
    (isset($parameters["InputAddKey"])) ? $parameters["InputAddKey"] : '',
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-add-key">'._T("Additionnal Key", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $checkValue);

// ---- allow-unauth
$check = new CheckboxTpl("check-allow-unauth");
$checkValue = new CheckboxTpl("check-allow-unauth-value");

$values = [
    (isset($parameters["CheckAllowUnauth"])) ? ($parameters["CheckAllowUnauth"] == "" ? "checked" : "") : "",
    (isset($parameters["CheckAllowUnauthValue"])) ? ($parameters["CheckAllowUnauthValue"] == "true" ? "checked" : "") : "",
];
$fields = [$check, $checkValue];
$f->add(
    new TrFormElement('<label for="check-allow-unauth">'._T("Allow Unauthenticated", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_allow_unauth]]
);
unset($check, $checkValue);


// ---- multi-arch
$check = new CheckboxTpl("check-multi-arch");
$input = new InputTplTitle("input-multi-arch", _T("To add multiarch configuration for i386", "imaging"));

$values = [
    (isset($parameters["CheckMultiArch"])) ? ($parameters["CheckMultiArch"] == "" ? "checked" : "") : "",
    (isset($parameters["InputMultiArch"])) ? $parameters["InputMultiArch"] : 'i386',
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-multi-arch">'._T("Multi Arch", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $checkValue);



$f->pop();


// ==== New Section ====
// Package Selection
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Package Selection","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('PackageSelection', "imaging"),'')));
$f->push(new Table());


// ---- tasksel
$check = new CheckboxTpl("check-tasksel");
$input = new InputTplTitle("input-tasksel", "");

$values = [
    (isset($parameters["CheckTasksel"])) ? ($parameters["CheckTasksel"] == "" ? "checked" : "") : "",
    (isset($parameters["InputTasksel"])) ? $parameters["InputTasksel"] : 'standard, web-server, kde-desktop',
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-tasksel">'._T("Tasksel", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $checkValue);

// ---- run-tasksel
$check = new CheckboxTpl("check-run-tasksel");
$input = new InputTplTitle("input-run-tasksel", $info_run_tasksel);

$values = [
    (isset($parameters["CheckRunTasksel"])) ? ($parameters["CheckRunTasksel"] == "" ? "checked" : "") : "",
    (isset($parameters["InputRunTasksel"])) ? $parameters["InputRunTasksel"] : '',
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-run-tasksel">'._T("Run Tasksel", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $checkValue);

// ---- include
$check = new CheckboxTpl("check-include");
$input = new InputTplTitle("input-include", _T("Individual additional packages to install", "imaging"));

$values = [
    (isset($parameters["CheckInclude"])) ? ($parameters["CheckInclude"] == "" ? "checked" : "") : "",
    (isset($parameters["InputInclude"])) ? $parameters["InputInclude"] : 'openssh-server build-essential',
];
$fields = [$check, $input];
$f->add(
    new TrFormElement('<label for="check-include">'._T("Include", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $input);

// ---- upgrade
$check = new CheckboxTpl("check-upgrade");
$select = new SelectItemtitle("select-upgrade", _T("Whether to upgrade packages after debootstrap.", "imaging"));
$_values = ["none", "safe-upgrade", "full-upgrade"];
$select->setElements($_values);
$select->setElementsVal($_values);

$values = [
    (isset($parameters["CheckUpgrade"])) ? ($parameters["CheckUpgrade"] == "" ? "checked" : "") : "",
    (isset($parameters["SelectUpgrade"])) ? $parameters["SelectUpgrade"] : 'none',
];
$fields = [$check, $select];
$f->add(
    new TrFormElement('<label for="check-upgrade">'._T("Upgrade", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, ""]]
);
unset($check, $select);


// ---- contest
$check = new CheckboxTpl("check-contest");
$checkValue = new CheckboxTpl("check-contest-value");

$values = [
    (isset($parameters["CheckContest"])) ? ($parameters["CheckContest"] == "" ? "checked" : "") : "",
    (isset($parameters["CheckContestValue"])) ? ($parameters["CheckContestValue"] == "true" ? "checked" : "") : "",
];
$fields = [$check, $checkValue];
$f->add(
    new TrFormElement('<label for="check-contest">'._T("Popularity contest", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_contest]]
);
unset($check, $checkValue);

$f->pop();




// ==== New Section ====
// Boot Loader
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Boot Loader","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('BootLoader', "imaging"),'')));
$f->push(new Table());


// ---- debian
$check = new CheckboxTpl("check-debian");
$checkValue = new CheckboxTpl("check-debian-value");

$values = [
    (isset($parameters["CheckDebian"])) ? ($parameters["CheckDebian"] == "" ? "checked" : "") : "",
    (isset($parameters["CheckDebianValue"])) ? ($parameters["CheckDebianValue"] == "true" ? "checked" : "") : "checked",
];
$fields = [$check, $checkValue];
$f->add(
    new TrFormElement('<label for="check-debian">'._T("Debian Only", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_debian]]
);
unset($check, $checkValue);


// ---- multi-os
$check = new CheckboxTpl("check-multi");
$checkValue = new CheckboxTpl("check-multi-value");

$values = [
    (isset($parameters["checkMulti"])) ? ($parameters["checkMulti"] == "" ? "checked" : "") : "",
    (isset($parameters["checkMultiValue"])) ? ($parameters["checkMultiValue"] == "true" ? "checked" : "") : "checked",
];
$fields = [$check, $checkValue];
$f->add(
    new TrFormElement('<label for="check-multi">'._T("With Multi OS", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_multi]]
);
unset($check, $checkValue);


$f->pop();









// ==== New Section ====
// Finishing
// =====================
// ---- Toggle button ----
$f->add(new TitleElement(_T("Finishing","imaging")));
$f->add(new TrFormElement("", new Iconereply(_T('Finishing', "imaging"),'')));
$f->push(new Table());


// ---- keep-consoles
$check = new CheckboxTpl("check-keep-consoles");
$checkValue = new CheckboxTpl("check-keep-consoles-value");

$values = [
    (isset($parameters["CheckKeepConsoles"])) ? ($parameters["CheckKeepConsoles"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckKeepConsolesValue"])) ? ($parameters["CheckKeepConsolesValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-keep-consoles">'._T("Keep Consoles", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_keep_consoles]]
);
unset($check, $checkValue);


// ---- reboot-in-progress
$check = new CheckboxTpl("check-reboot-in-progress");
// ---- reboot-in-prok-reboot-in-progress");
$checkValue = new CheckboxTpl("check-reboot-in-progress-value");

$values = [
    (isset($parameters["CheckRebootInProgress"])) ? ($parameters["CheckRebootInProgress"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckRebootInProgressValue"])) ? ($parameters["CheckRebootInProgressValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-reboot-in-progress">'._T("Reboot In Progress", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_keep_consoles]]
);
unset($check, $checkValue);


// ---- eject-cdrom
$check = new CheckboxTpl("check-eject-cdrom");
$checkValue = new CheckboxTpl("check-eject-cdrom-value");

$values = [
    (isset($parameters["CheckEjectCdrom"])) ? ($parameters["CheckEjectCdrom"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckEjectCdromValue"])) ? ($parameters["CheckEjectCdromValue"] == 'true' ? 'checked' : '') : '',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-eject-cdrom">'._T("Eject cdrom", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_eject_cdrom]]
);
unset($check, $checkValue);

// ---- reboot
$check = new CheckboxTpl("check-reboot");
$checkValue = new CheckboxTpl("check-reboot-value");

$values = [
    (isset($parameters["CheckReboot"])) ? ($parameters["CheckReboot"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckRebootValue"])) ? ($parameters["CheckRebootValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-reboot">'._T("Reboot", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_reboot]]
);
unset($check, $checkValue);

// ---- poweroff


$check = new CheckboxTpl("check-poweroff");
$checkValue = new CheckboxTpl("check-poweroff-value");

$values = [
    (isset($parameters["CheckPoweroff"])) ? ($parameters["CheckPoweroff"] == '' ? 'checked' : '') : '',
    (isset($parameters["CheckPoweroffValue"])) ? ($parameters["CheckPoweroffValue"] == 'true' ? 'checked' : '') : 'checked',
];
$fields = [$check, $checkValue];

$f->add(
    new TrFormElement('<label for="check-poweroff">'._T("Poweroff", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "title"=>[$info_comment_this_field, $info_poweroff]]
);
unset($check, $checkValue);



//=============
$bo = new buttonTpl('bvalid', _T("Validate",'imaging'),'btnPrimary',_T("Create Preseed linux file", "imaging"));
$rr = new TrFormElementcollapse($bo);
$rr->setstyle("text-align: center;");
$f->add(
        $rr
);
$f->add(
    new TrFormElement("",   new multifieldTpl(
            array(  new SpanElementtitle(_T("Preseed file", "imaging"),Null, _T("Show preseed content", "imaging")),
                new Iconereply('Validate',_T("Show preseed content", "imaging"))
            )
        )
    )
);

$f->pop();

$f->pop();
$f->display();
echo "<pre id='codeTocopy2' style='width:100%;'></pre>";
?>
