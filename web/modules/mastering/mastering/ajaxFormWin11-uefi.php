<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

// require_once("../../../includes/config.inc.php");
if(is_file("includes/session.inc.php")){
    require_once("includes/session.inc.php");
}
else{
    require_once("../../../includes/session.inc.php");
}

if(is_file("includes/i18n.inc.php")){
    require_once("includes/i18n.inc.php");
}
else{
    require_once("../../../includes/i18n.inc.php");
    // require_once("../../../includes/session.inc.php");
}


if(is_file("includes/acl.inc.php")){
    require_once("includes/acl.inc.php");
}
else{
    require_once("../../../includes/acl.inc.php");
}

if(is_file("includes/PageGenerator.php")){
    require_once("includes/PageGenerator.php");
}
else{
    require_once("../../../includes/PageGenerator.php");
}


if(is_file("modules/mastering/includes/data_Windows_Answer_File_Generator.inc.php")){
    require_once("modules/mastering/includes/data_Windows_Answer_File_Generator.inc.php");
}
else{
    require("../includes/data_Windows_Answer_File_Generator.inc.php");

}
// require_once("../includes/class_form.php");
if(is_file("modules/mastering/includes/class_form.php")){
    require_once("modules/mastering/includes/class_form.php");
}
else{
    require_once("../includes/class_form.php");
}
if(is_file("modules/mastering/includes/templates_integration.php")){
    require_once("modules/mastering/includes/templates_integration.php");
}
else{
    require_once("../includes/templates_integration.php");
}

if(is_file("modules/mastering/includes/xmlrpc.php")){
    require_once("modules/mastering/includes/xmlrpc.php");
}
else{
    require_once("../includes/xmlrpc.php");
}


$scriptType = "sysprep";

$entity = (isset($_POST['entity'])) ? htmlentities($_POST["entity"]) : (isset($_GET["entity"]) ? $_GET["entity"] : "");
$server = (isset($_POST['server'])) ? htmlentities($_POST["server"]) : (isset($_GET["server"]) ? $_GET["server"] : "");
$mode = (isset($_GET["mode"])) ? htmlentities($_GET["mode"]) : "new";
if(!in_array($mode, ["new", "edit"])){
    $mode = "new";
}

$id = (isset($_GET["id"])) ? htmlentities($_GET["id"]) : 0;

$scriptName = "Win11-uefi";

if(isset($_SESSION['parameters']))
{
	$parameters = $_SESSION['parameters'];
    $parameters["mode"] = $mode;
    unset($_SESSION["parameters"]);

}
echo '<pre>';
print_r($parameters);
echo '</pre>';
$f = new ValidatingForm(["action" => urlStrRedirect("mastering/mastering/".$mode."Script")]);

$f->add(new HiddenTpl("entity"), array("value" => $entity, "hide" => True));
$f->add(new HiddenTpl("server"), array("value" => $server, "hide" => True));
$f->add(new HiddenTpl("type"), array("value" => $scriptType, "hide" => True));
$f->add(new HiddenTpl("script"), array("value" => $scriptName, "hide" => True));
$f->add(new HiddenTpl("mode"), array("value" => $mode, "hide" => True));
if($mode == "edit"){
    $f->add(new HiddenTpl("id"), array("value" => $id, "hide" => True));
}

//==== NEW SECTION ====
// Installation Notes
//=====================
$f->add(new TitleElement(_T("Script attributes", "imaging")));
$f->push(new Table());
    $name = (isset($parameters["name"])) ? htmlentities($parameters["name"]) : "";
    $f->add(new TrFormElement("Name", new InputTpl("name")), ["value"=>$name, "required"=>True, "placeholder"=>_T("Sysprep Name", "mastering")]);

    $description = (isset($parameters["description"])) ? htmlentities($parameters["description"]) : "";
    $f->add(new TrFormElement("Description", new InputTpl("description")), ["placeholder"=>_T("Description", "mastering"), "value"=>$description]);

    $defaultTemplate = (isset($parameters["content"])) ? $parameters["content"] : get_template_integration($scriptName);
    $f->add(new TrFormElement("Integration", new OptTextareaTpl(["name"=>"content", "value"=>$defaultTemplate])));

$f->pop();
$f->add(new SepTpl());

//==== NEW SECTION ====
// Os Settings
//=====================
$f->add(new TitleElement(_T("Os Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('General_Settings', $InfoBule_General_Settings)));
$f->push(new Table());

//_____________
$key1 = new InputTplTitle('ProductKey1', $InfoBule_ProductKey);
$key1->setSize(5);
$key2 = new InputTplTitle('ProductKey2', $InfoBule_ProductKey);
$key2->setSize(5);
$key3 = new InputTplTitle('ProductKey3', $InfoBule_ProductKey);
$key3->setSize(5);
$key4 = new InputTplTitle('ProductKey4', $InfoBule_ProductKey);
$key4->setSize(5);
$key5 = new InputTplTitle('ProductKey5', $InfoBule_ProductKey);
$key5->setSize(5);
$fields =   array(
    $key1,new SpanElement("-"),
    $key2,new SpanElement("-"),
    $key3,new SpanElement("-"),
    $key4,new SpanElement("-"),
    $key5
);
$values = array(
    (isset($parameters['ProductKey1'])) ? $parameters['ProductKey1'] : "W269N","",
    (isset($parameters['ProductKey2'])) ? $parameters['ProductKey2'] : "WFGWX","",
    (isset($parameters['ProductKey3'])) ? $parameters['ProductKey3'] : "YVC9B","",
    (isset($parameters['ProductKey4'])) ? $parameters['ProductKey4'] : "4J6C9","",
    (isset($parameters['ProductKey5'])) ? $parameters['ProductKey5'] : "T83GX"
);
//_____________
$f->add(
    new TrFormElement(_T('Product Key', 'imaging').":", new multifieldTpl($fields)),
    array("value" => $values,"required" => true)
);
//_____________
$f->add(
    new TrFormElement(_T('Organization Name', 'imaging').":", new InputTplTitle('OrganizationName', $InfoBulle_OrganizationName)),
    array('value' => (isset($parameters['OrganizationName'])) ? $parameters['OrganizationName'] : 'Medulla', "required" => true)
);
//_____________
$EULA = new SelectItemtitle("AcceptEULA", $InfoBule_AcceptEULA);
$EULA->setElements($yes_no);
$EULA->setElementsVal(array('true', 'false'));
$f->add(
    new TrFormElement(_T('Accept EULA', 'imaging').":", $EULA),
    array("value" => (isset($parameters['AcceptEULA'])) ? $parameters['AcceptEULA'] : "true","required" => true)
);
//_____________
$Skipactivation = new SelectItemtitle("SkipAutoActivation", $InfoBule_SkipAutoActivation);
$Skipactivation->setElements($yes_no);
$Skipactivation->setElementsVal(array('true', 'false'));
$f->add(
    new TrFormElement(_T('Skip automatic activation', 'imaging').":", $Skipactivation),
    array("value" => (isset($parameters['SkipAutoActivation'])) ? $parameters['SkipAutoActivation'] : "true","required" => true)
);
//_____________
$SkipLicense = new SelectItemtitle("SkipRearm", $InfoBule_SkipRearm);
$SkipLicense->setElements($yes_no);
$SkipLicense->setElementsVal(array('1', '0'));
$f->add(
    new TrFormElement(_T('Skip License Rearm', 'imaging').":", $SkipLicense),
    array("value" => (isset($parameters['SkipRearm'])) ? $parameters['SkipRearm'] : "1","required" => true)
);
//_____________
$SetupUILanguage = new SelectItemtitle("SetupUILanguage", $InfoBule_SetupUILanguage);
$SetupUILanguage->setElements($eleUILanguage);
$SetupUILanguage->setElementsVal($valUILanguage);
//_____________
$f->add(
    new TrFormElement(_T('Setup Language', 'imaging').":", $SetupUILanguage),
    array("value" => (isset($parameters['SetupUILanguage'])) ? $parameters['SetupUILanguage'] : "fr-FR","required" => true)
);
//_____________
$f->add(
    new TrFormElement(_T('Computer Name', 'imaging').":", new InputTplTitle('ComputerName', $Infobule_ComputerName)),
    array("required" => true,"value" =>(isset($parameters['ComputerName'])) ? $parameters['ComputerName'] : 'windows10-PC')
);
//_____________
$InputLocale = new SelectItemtitle("InputLocale", $Infobule_InputLocale);
$InputLocale->setElements($elementInputarray);
$InputLocale->setElementsVal($valeurInputarray);
$f->add(
    new TrFormElement(_T('Keyboard or input method', 'imaging').":", $InputLocale),
    array("value" => (isset($parameters['InputLocale'])) ? $parameters['InputLocale'] : '1036:0000040c',"required" => true)
);
//_____________
$UserLocale = new SelectItemtitle("UserLocale", $InfoBule_UserLocale);
$UserLocale->setElements($eleUILanguage);
$UserLocale->setElementsVal($valUILanguage);
$f->add(
    new TrFormElement(_T('Currency and Date format', 'imaging').":", $UserLocale),
    array("value" =>(isset($parameters['UserLocale'])) ? $parameters['UserLocale'] : "fr-FR","required" => true)
);
//_____________
$TimeZone = new SelectItemtitle("TimeZone", $InfoBule_TimeZone);
$TimeZone->setElements($element_timezone);
$TimeZone->setElementsVal($val_timezone);
$f->add(
    new TrFormElement(_T('Time Zone', 'imaging').":", $TimeZone),
    array("value" =>  (isset($parameters['TimeZone'])) ? $parameters['TimeZone'] : "Romance Standard Time","required" => true)
);
//_____________
$UILanguage = new SelectItemtitle("UILanguage", $InfoBule_UILanguage);
$UILanguage->setElements($eleUILanguage);
$UILanguage->setElementsVal($valUILanguage);
$f->add(
    new TrFormElement(_T('UI Language', 'imaging').":", $UILanguage),
    array("value" => (isset($parameters['UILanguage'])) ? $parameters['UILanguage'] : 'fr-FR' ,"required" => true)
);

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// Partition Settings
//=====================
$f->add(new TitleElement(_T("Partition Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Partition_Settings', $Infobule_Partition_Settings)));
$f->push(new Table());

//_____________
$WipeDisk = new SelectItemtitle("WipeDisk", $InfoBule_WipeDisk);
$WipeDisk->setElements($yes_no);
$WipeDisk->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Wipe Disk', 'imaging').":", $WipeDisk),
    array("value" => (isset($parameters['WipeDisk'])) ? $parameters['WipeDisk'] : "false","required" => true)
);
//_____________
$InstallDisk = new SelectItemtitle("InstallDisk", $InfoBule_InstallDisk);
$InstallDisk->setElements($suite0_5);
$InstallDisk->setElementsVal($suite0_5);
$f->add(
    new TrFormElement(_T('Install to disk', 'imaging').":", $InstallDisk),
    array("value" => (isset($parameters['InstallDisk'])) ? $parameters['InstallDisk'] : "0","required" => true)
);
//_____________
$PartitionOrder = new SelectItemtitle("PartitionOrder", $InfoBule_PartitionOrder);
$PartitionOrder->setElements($suite4_7);
$PartitionOrder->setElementsVal($suite4_7);
$f->add(
    new TrFormElement(_T('Partition Order', 'imaging').":", $PartitionOrder),
    array("value" => (isset($parameters['PartitionOrder'])) ? $parameters['PartitionOrder'] : "2","required" => true)
);
//_____________
$ExtendOSPartition = new SelectItemtitle("ExtendOSPartition", $InfoBule_ExtendOSPartition);
$ExtendOSPartition->setElements($yes_no);
$ExtendOSPartition->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Extend OS Partition', 'imaging').":", $ExtendOSPartition),
    array("value" => (isset($parameters['ExtendOSPartition'])) ? $parameters['ExtendOSPartition'] : "true","required" => true)
);
//_____________
$Format = new SelectItemtitle("Format", $InfoBule_Format);
$Format->setElements(array('NTFS','FAT32'));
$Format->setElementsVal(array('NTFS','FAT32'));
$f->add(
    new TrFormElement(_T('Main Partition Format', 'imaging').":", $Format),
    array("value" => (isset($parameters['Format'])) ? $parameters['Format'] : "NTFS","required" => true)
);
//_____________
$f->add(
    new TrFormElement($InfoBule_Label, new InputTplTitle('Label', $InfoBule_Label)),
    array("required" => true,'value' => (isset($parameters['Label'])) ? $parameters['Label'] : 'OS')
);
//_____________
$DriveLetter = new SelectItemtitle("DriveLetter", $InfoBule_DriveLetter);
$DriveLetter->setElements($DriveLetterTabElement);
$DriveLetter->setElementsVal($DriveLetterTabElement);
$f->add(
    new TrFormElement(_T('Main Partition Letter', 'imaging').":", $DriveLetter),
    array("value" => (isset($parameters['DriveLetter'])) ? $parameters['DriveLetter'] : "C","required" => true)
);

$f->pop();
$f->add(new SepTpl());

// ==== NEW SECTION ====
// Bloat
//======================


$f->add(new TitleElement(_T("Remove Bloatware", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Bloatwares', $InfoBule_Bloatware)));

$str = '<table>';

$blatsFlag = false;
if(isset($parameters['bloats'])){
    $blatsFlag = true;
}

foreach($bloats as $bloatName=>$bloat){
    $checked = '';
    if($blatsFlag && in_array($bloat["value"], $parameters['bloats'])){
        $checked = 'checked';
    }

    $str .= '<tr>
        <td>
            <label for="'.$bloat['id'].'">'.$bloatName.'</label>
        </td>
        <td>
            <input type="checkbox" id="'.$bloat['id'].'" name="'.$bloat['name'].'" value="'.$bloatName.'" '.$checked.'/>
        </td>
    </tr>';
}
$str .= '</table>';

$f->add(new TrFormElement("", new SpanElement($str)));

//==== NEW SECTION ====
// Security Settings
//=====================
$f->add(new TitleElement(_T("Security Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Out_Of_Box_Experience', $InfoBule_Out_Of_Box_Experience)));
$f->push(new Table());

//_____________
$ProtectComputer = new SelectItemtitle("ProtectComputer", $InfoBule_ProtectComputer);
$ProtectComputer->setElements($ProtectComputerTabElement);
$ProtectComputer->setElementsVal(array('1','2','3'));
$f->add(
    new TrFormElement(_T('Protect Your Computer', 'imaging').":", $ProtectComputer),
    array("value" => (isset($parameters['ProtectComputer'])) ? $parameters['ProtectComputer'] : "1","required" => true)
);
//_____________
/*$Updates = new SelectItemtitle("Updates",$InfoBule_Updates);
$Updates->setElements($UpdatesTabElement);
$Updates->setElementsVal(array('1','2','3','4'));
$f->add(
    new TrFormElement(_T('System Updates','imaging').":", $Updates),
    array("value" => (isset($parameters)) ? $parameters['Updates'] : "3","required" => True)
);*/
//_____________
$NetworkLocation = new SelectItemtitle("NetworkLocation", $InfoBule_NetworkLocation);
$NetworkLocation->setElements(array('Home','Work','Other'));
$NetworkLocation->setElementsVal(array('Home','Work','Other'));
$f->add(
    new TrFormElement(_T('Network Location', 'imaging').":", $NetworkLocation),
    array("value" => (isset($parameters['NetworkLocation'])) ? $parameters['NetworkLocation'] : "Work","required" => true)
);
//_____________
$HideEULA = new SelectItemtitle("HideEULA", $InfoBule_HideEULA);
$HideEULA->setElements($yes_no);
$HideEULA->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Hide EULA page', 'imaging').":", $HideEULA),
    array("value" => (isset($parameters['HideEULA'])) ? $parameters['HideEULA'] : "true","required" => true)
);
//_____________
$EnableFirewall = new SelectItemtitle("EnableFirewall", $InfoBule_EnableFirewall);
$EnableFirewall->setElements($EnableDisabled);
$EnableFirewall->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Enable Firewall', 'imaging').":", $EnableFirewall),
    array("value" => (isset($parameters['EnableFirewall'])) ? $parameters['EnableFirewall'] : "true","required" => true)
);
//_____________
$DaylightSettings = new SelectItemtitle("DaylightSettings", $InfoBule_DaylightSettings);
$DaylightSettings->setElements($yes_no);
$DaylightSettings->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Disable auto daylight timeset', 'imaging').":", $DaylightSettings),
    array("value" => (isset($parameters['DaylightSettings'])) ? $parameters['DaylightSettings'] : "true","required" => true)
);
//_____________
$HideWireless = new SelectItemtitle("HideWireless", $Infobule_HideWireless);
$HideWireless->setElements($yes_no);
$HideWireless->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Hide wireless setup in OOBE', 'imaging').":", $HideWireless),
    array("value" => (isset($parameters['HideWireless'])) ? $parameters['HideWireless'] : "true","required" => true)
);
//_____________
$ControlPanelView = new SelectItemtitle("ControlPanelView", $InfoBule_ControlPanelView);
$ControlPanelView->setElements(array(_T('Category View', "imaging"),_T('Classic View', "imaging")));
$ControlPanelView->setElementsVal(array('0','1'));
$f->add(
    new TrFormElement(_T('Control Panel View', 'imaging').":", $ControlPanelView),
    array("value" => (isset($parameters['ControlPanelView'])) ? $parameters['ControlPanelView'] : "1","required" => true)
);
//_____________
$ControlPanelIconSize = new SelectItemtitle("ControlPanelIconSize", $InfoBule_ControlPanelIconSize);
$ControlPanelIconSize->setElements(array(_T('Large', "imaging"),_T('Small', "imaging")));
$ControlPanelIconSize->setElementsVal(array('0','1'));
$f->add(
    new TrFormElement(_T('Control Panel Icon Size', 'imaging').":", $ControlPanelIconSize),
    array("value" => (isset($parameters['ControlPanelIconSize'])) ? $parameters['ControlPanelIconSize'] : "0","required" => true)
);

$f->pop();
$f->add(new SepTpl());

//==== NEW SECTION ====
// Domain Settings
//=====================
$f->add(new TitleElement(_T("Domain Settings", "imaging")));
$f->push(new Table());

$f->add(
    new TrFormElement(_T('Domain', 'imaging').":", new InputTplTitle('Domain', $InfoBule_Domain)),
    array("required" => true,"value" =>(isset($parameters['Domain'])) ? $parameters['Domain'] : '')
);
$f->add(
    new TrFormElement(_T('Domain User', 'imaging').":", new InputTplTitle('DomainUser', $InfoBule_DomainUser)),
    array("required" => true,"value" =>(isset($parameters['DomainUser'])) ? $parameters['DomainUser'] : '')
);
$f->add(
    new TrFormElement(_T('Domain Password', 'imaging').":", new InputTplTitle('DomainPassword', $InfoBule_DomainPassword)),
    array("required" => true,"value" =>(isset($parameters['DomainPassword'])) ? $parameters['DomainPassword'] : '')
);
$f->add(
    new TrFormElement(_T('Join Domain', 'imaging').":", new InputTplTitle('JoinDomain', $InfoBule_JoinDomain)),
    array("required" => true,"value" =>(isset($parameters['JoinDomain'])) ? $parameters['JoinDomain'] : '')
);
$f->add(
    new TrFormElement(_T('MachineObjectOU', 'imaging').":", new InputTplTitle('MachineObjectOU', $InfoBule_MachineObjectOU)),
    array("required" => true,"value" =>(isset($parameters['MachineObjectOU'])) ? $parameters['MachineObjectOU'] : '')
);

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// Administrators Accounts
//=====================
$f->add(new TitleElement(_T("Administrator Account", "imaging")));
$f->push(new Table());

//_____________
$f->add(
    new TrFormElement(_T('Password', 'imaging'), new InputTplTitle('PasswordAdmin', $InfoBule_PasswordAdmin)),
    array(  "required" => true,
            "value" => (isset($parameters['PasswordAdmin'])) ? $parameters['PasswordAdmin'] : "")
);

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// User Account
//=====================
$f->add(new TitleElement(_T("User Account", "imaging")));
$f->add(new TrFormElement("", new Iconereply('User_Account', $InfoBule_User_Account)));
$f->push(new Table());

//_____________
$CEIPEnabled = new SelectItemtitle("CEIPEnabled", $InfoBule_CEIPEnabled);
$CEIPEnabled->setElements($EnableDisabled);
$CEIPEnabled->setElementsVal(array('1','0'));
$f->add(
    new TrFormElement(_T('Customer Experience Improvement Program (CEIP)', 'imaging').":", $CEIPEnabled),
    array("value" => (isset($parameters['CEIPEnabled'])) ? $parameters['CEIPEnabled'] : "0","required" => true)
);
//_____________
$CopyProfile = new SelectItemtitle("CopyProfile", $InfoBule_CopyProfile);
$CopyProfile->setElements($yes_no);
$CopyProfile->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('Copy Profile', 'imaging').":", $CopyProfile),
    array("value" => (isset($parameters['CopyProfile'])) ? $parameters['CopyProfile'] : "true","required" => true)
);
//_____________
$f->add(
    new TrFormElement(_T('User Name', 'imaging'), new InputTplTitle('FullName', $InfoBule_FullName)),
    array("value" => (isset($parameters['FullName'])) ? $parameters['FullName'] : "Temp","required" => true)
);
//_____________
$Group = new SelectItemtitle("Group", $InfoBule_Group);
$Group->setElements($GroupTabElement);
$Group->setElementsVal($GroupTabValue);
$f->add(
    new TrFormElement(_T('Group', 'imaging').":", $Group),
    array("value" => (isset($parameters['Group'])) ? $parameters['Group'] : "Users","required" => true)
);
//_____________
$f->add(
    new TrFormElement(_T('Description', 'imaging'), new InputTplTitle('Description', $InfoBule_Description)),
    array("value" => (isset($parameters['Description'])) ? $parameters['Description'] : "Temp","required" => true)
);
//_____________
$f->add(
    new TrFormElement(_T('Password: (Optional)', 'imaging'), new InputTplTitle('Password', $InfoBule_Password)),
    array("value" => (isset($parameters['Password'])) ? $parameters['Password'] : "")
);
//_____________
$EnableUAC = new SelectItemtitle("EnableUAC", $InfoBule_EnableUAC);
$EnableUAC->setElements($EnableDisabled);
$EnableUAC->setElementsVal($truefalse);
$f->add(
    new TrFormElement(_T('UAC', 'imaging').":", $EnableUAC),
    array("value" => (isset($parameters['EnableUAC'])) ? $parameters['EnableUAC'] : "false","required" => true)
);

//=============

$f->pop();
$f->addValidateButton("bconfirm", _T("Confirm", "mastering"));

$f->display();

?>
