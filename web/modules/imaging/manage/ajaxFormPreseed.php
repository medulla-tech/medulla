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
'#OS Debian [x86 and amd64]',
'#Preseed :',
'#',
'#date : <? echo $strin; ?>dateval<? echo $strou; ?>',
'#',
'#Installation Notes',
'#Location: <? echo $strin; ?>Location<? echo $strou; ?>',
'#Notes: <? echo $strin; ?>Comments<? echo $strou; ?>',
'#list parameters : @@listParameters@@',
'#________________________________',
'# LOCALIZATION',
'<?php echo $strin;?>CheckLocale<?php echo $strou;?>d-i debian-installer/locale string <?echo $strin;?>SelectLocale<?php echo $strou;?>',
'<? echo $strin;?>CheckLanguage<? echo $strou;?>d-i debian-installer/language string <? echo $strin;?>SelectLanguage<? echo $strou;?>',
'<? echo $strin;?>CheckCountry<? echo $strou;?>d-i debian-installer/country string <? echo $strin;?>SelectCountry<? echo $strou;?>',
'<? echo $strin;?>CheckSupportedLocales<? echo $strou;?>d-i localechooser/supported-locales multiselect <? echo $strin;?>SelectSupportedLocales<? echo $strou;?>, en_US.UTF-8',
'<? echo $strin;?>CheckKeyboardLayouts<? echo $strou;?>d-i keyboard-configuration/layoutcode string <? echo $strin;?>SelectKeyboardLayouts<? echo $strou;?>',
'<? echo $strin;?>CheckKeyboardToggle<? echo $strou;?>d-i keyboard-configuration/toggle select <? echo $strin;?>SelectKeyboardToggle<? echo $strou;?>',
'### NETWORK',
'<? echo $strin;?>CheckEnableNetwork<? echo $strou;?>d-i netcfg/enable boolean <? echo $strin;?>CheckEnableNetworkValue<? echo $strou;?>',
'#<? echo $strin;?>SelectInterface<? echo $strou;?>',
'<? echo $strin;?>CheckInterface<? echo $strou;?>d-i netcfg/choose_interface select <?echo $strin;?>InputInterface<? echo $strou;?>',
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
    new TrFormElement('<label for="check-locale">'._T("locale", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-language">'._T("language", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-country">'._T("country", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-supported-locales">'._T("Supported Locales", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-keyboard-layouts">'._T("Keyboard Layout", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-keyboard-toggle">'._T("Keyboard Toggle", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values]
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
    new TrFormElement('<label for="check-enable-network">'._T("Enable Network", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "title"=>["", $info_enable_network]]
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
    (isset($parameters) && $parameters['InputInterface'] != 'auto') ? $parameters['InputInterface'] : '',
];

$f->add(
    new TrFormElement('<label for="check-interface">'._T("Interface", "imaging").'</label>', new multifieldTpl($fields)), ["value"=>$values, "placeholder"=>["", "", "eth0"]]
);

$f->pop();


// $check_language = new CheckboxTpl("check-language");
// $input_language = new InputTplTitle("input-language");
// $fields = [
//     $check_language, $input_language
// ];

// $values = [
//     (isset($parameters)) ? $parameters['check-language'] : '',
//     (isset($parameters)) ? $parameters['input-language'] : '',
// ];

// $f->add(
//     new TrFormElement('<label for="check-language">'._T("language", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "placeholder" => ["", "fr"]]
// );




// ---- example for input
// $check_language = new CheckboxTpl("check-language");
// $input_language = new InputTplTitle("input-language");
// $fields = [
//     $check_language, $input_language
// ];

// $values = [
//     (isset($parameters)) ? $parameters['check-language'] : '',
//     (isset($parameters)) ? $parameters['input-language'] : '',
// ];

// $f->add(
//     new TrFormElement('<label for="check-language">'._T("language", "imaging").'</label>', new multifieldTpl($fields)), ["value" => $values, "placeholder" => ["", "fr"]]
// );




//==== NEW SECTION ====
// Os Settings
//=====================
// $f->add(new TitleElement(_T("Os Settings","imaging")));
// $f->add(new TrFormElement("",new Iconereply('General_Settings',$InfoBule_General_Settings)));
// $f->push(new Table());

//     //_____________
//     $key1 = new InputTplTitle('ProductKey1',$InfoBule_ProductKey);
//     $key1->setSize(5);
//     $key2 = new InputTplTitle('ProductKey2',$InfoBule_ProductKey);
//     $key2->setSize(5);
//     $key3 = new InputTplTitle('ProductKey3',$InfoBule_ProductKey);
//     $key3->setSize(5);
//     $key4 = new InputTplTitle('ProductKey4',$InfoBule_ProductKey);
//     $key4->setSize(5);
//     $key5 = new InputTplTitle('ProductKey5',$InfoBule_ProductKey);
//     $key5->setSize(5);
//     $fields =   array(
//         $key1,new SpanElement("-"),
//         $key2,new SpanElement("-"),
//         $key3,new SpanElement("-"),
//         $key4,new SpanElement("-"),
//         $key5
//     );
//     $values = array(
//         (isset($parameters)) ? $parameters['ProductKey1'] : "HYF8J","",
//         (isset($parameters)) ? $parameters['ProductKey2'] : "CVRMY","",
//         (isset($parameters)) ? $parameters['ProductKey3'] : "CM74G","",
//         (isset($parameters)) ? $parameters['ProductKey4'] : "RPHKF","",
//         (isset($parameters)) ? $parameters['ProductKey5'] : "PW487"
//     );
//     //_____________
//     $f->add(
//         new TrFormElement(_T('Product Key','imaging').":", new multifieldTpl($fields)),
//         array("value" => $values,"required" => True)
//     );
//     //_____________
//     $f->add(
//         new TrFormElement(_T('Organization Name','imaging').":", new InputTplTitle('OrginazationName',$InfoBule_OrginazationName)),
//         array("value" => (isset($parameters)) ? $parameters['OrginazationName'] : 'Medulla', "required" => True)
//     );

// $f->pop();
// $f->add( new SepTpl());


$f->pop();
$f->display();

echo "<pre id='codeTocopy2' style='width:100%;'></pre>";

// $table = new CTag("table", "", ["class"=>"listinfos"]);

// // Defin table column head
// $theader = [
//     new CTag("th", "tab1"), 
//     new CTag("th", "tab2"), 
//     new CTag("th", "tab3")
// ];


// $label = new CTag("label", "label for input", ["for"=>"input"]);

// $tbody = [
//     new CTag("td"),
//     new CTag("td"),
//     new CTag("td"),
// ];
// $tbody[0]->addChild($label->addChild(new OTag("input", ["type"=>"text", "name"=>"input", "placeholder"=>"My Input", "id"=>"input"])));
// $tbody[1]->addChild(new CTag("p", "coucou en rouge", ["style"=>"color:red;"]));
// $tbody[2]->addChild(new CTag("textarea", "message a ajouter", ['name'=>'textarea']),);

// $table->addChild(new CTag("thead"))->addChild(new CTag("tr"))->addChildren($theader);
// $table->addChild(new CTag("tbody"))->addChild(new CTag("tr"))->addChildren($tbody);
// echo $table->render();

?>
