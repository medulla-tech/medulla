<?php
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
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
'<? echo $strin;?>xml version="1.0" encoding="utf-8"<? echo $strou;?>',
'<unattend xmlns="urn:schemas-microsoft-com:unattend">',
'<!--',
'________________________________',
'OS Windows 7 [x86 and amd64]',
'Windows Answer File Generator :',
'',
'date : <? echo $strin; ?>dateval<? echo $strou; ?>',
'',
'Installation Notes',
'Location: <? echo $strin; ?>Location<? echo $strou; ?>',
'Notes: <? echo $strin; ?>Comments<? echo $strou; ?>',
'list parameters : @@listParameters@@',
'________________________________',
'-->',
'',
'',
'<settings pass="specialize">',
'<component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'<Extend><? echo $strin;?>ExtendOSPartition<? echo $strou;?></Extend>',
'</ExtendOSPartition>',
'</component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin;?>ComputerName<? echo $strou;?></ComputerName>',
'<ShowWindowsLive><? echo $strin;?>ShowWindowsLive<? echo $strou;?></ShowWindowsLive>',
'<TimeZone><? echo $strin;?>TimeZone<? echo $strou;?></TimeZone>',
'<RegisteredOrganization><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOrganization>',
'<RegisteredOwner><? echo $strin;?>FullName<? echo $strou;?></RegisteredOwner>',
'<ProductKey><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></ProductKey>',
'<CopyProfile><? echo $strin; ?>CopyProfile<? echo $strou; ?></CopyProfile>',
'</component>',
'<component name="Microsoft-Windows-UnattendedJoin" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<Identification>',
'<Credentials>',
'<Domain><? echo $strin; ?>Domain<? echo $strou; ?></Domain>',
'<Password><? echo $strin; ?>DomainPassword<? echo $strou; ?></Password>',
'<Username><? echo $strin; ?>DomainUser<? echo $strou; ?></Username>',
'</Credentials>',
'<JoinDomain><? echo $strin; ?>JoinDomain<? echo $strou; ?></JoinDomain>',
'<MachineObjectOU><? echo $strin; ?>MachineObjectOU<? echo $strou; ?></MachineObjectOU>',
'</Identification>',
'</component>',
'<component name="Microsoft-Windows-Deployment" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'<Extend><? echo $strin;?>ExtendOSPartition<? echo $strou;?></Extend>',
'</ExtendOSPartition>',
'</component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin;?>ComputerName<? echo $strou;?></ComputerName>',
'<ShowWindowsLive><? echo $strin;?>ShowWindowsLive<? echo $strou;?></ShowWindowsLive>',
'<TimeZone><? echo $strin;?>TimeZone<? echo $strou;?></TimeZone>',
'<RegisteredOrganization><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOrganization>',
'<RegisteredOwner><? echo $strin;?>FullName<? echo $strou;?></RegisteredOwner>',
'<ProductKey><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></ProductKey>',
'<CopyProfile><? echo $strin; ?>CopyProfile<? echo $strou; ?></CopyProfile>',
'</component>',
'<component name="Microsoft-Windows-UnattendedJoin" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<Identification>',
'<Credentials>',
'<Domain><? echo $strin; ?>Domain<? echo $strou; ?></Domain>',
'<Password><? echo $strin; ?>DomainPassword<? echo $strou; ?></Password>',
'<Username><? echo $strin; ?>DomainUser<? echo $strou; ?></Username>',
'</Credentials>',
'<JoinDomain><? echo $strin; ?>JoinDomain<? echo $strou; ?></JoinDomain>',
'<MachineObjectOU><? echo $strin; ?>MachineObjectOU<? echo $strou; ?></MachineObjectOU>',
'</Identification>',
'</component>',
'</settings>',
'<settings pass="oobeSystem">',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<OOBE>',
'<HideEULAPage><? echo $strin;?>HideEULA<? echo $strou;?></HideEULAPage>',
'<NetworkLocation><?echo $strin; ?>NetworkLocation<? echo $strou; ?></NetworkLocation>',
'<ProtectYourPC><? echo $strin;?>ProtectComputer<? echo $strou;?></ProtectYourPC>',
'<SkipUserOOBE>true</SkipUserOOBE>',
'<SkipMachineOOBE>true</SkipMachineOOBE>',
'</OOBE>',
'<UserAccounts>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
'<Password>',
'<Value><? echo $strin;?>Password<? echo $strou;?></Value>',
'<PlainText>true</PlainText>',
'</Password>',
'<Description><? echo $strin;?>Description<? echo $strou;?></Description>',
'<DisplayName><? echo $strin;?>FullName<? echo $strou;?></DisplayName>',
'<Group><? echo $strin;?>Group<? echo $strou;?></Group>',
'<Name><? echo $strin;?>FullName<? echo $strou;?></Name>',
'</LocalAccount>',
'</LocalAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin; ?>PasswordAdmin<? echo $strou; ?></Value>',
'<PlainText>true</PlainText>',
'</AdministratorPassword>',
'</UserAccounts>',
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<RequiresUserInput>false</RequiresUserInput>',
'<Order>1</Order>',
'<Description>Disable auto-update</Description>',
'<CommandLine>reg add &quot;HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update&quot; /v AUOptions /t REG_DWORD /d <? echo $strin; ?>Updates<? echo $strou; ?>/f</CommandLine>',
'</SynchronousCommand>',
'</FirstLogonCommands>',
'</component>',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?></InputLocale>',
'<SystemLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?></SystemLocale>',
'<UILanguage><? echo $strin;?>UILanguage<? echo $strou;?></UILanguage>',
'<UserLocale><? echo $strin;?>UserLocale<? echo $strou;?></UserLocale>',
'</component>',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?></InputLocale>',
'<SystemLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?></SystemLocale>',
'<UILanguage><? echo $strin;?>UILanguage<? echo $strou;?></UILanguage>',
'<UserLocale><? echo $strin;?>UserLocale<? echo $strou;?></UserLocale>',
'</component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<OOBE>',
'<HideEULAPage><? echo $strin;?>HideEULA<? echo $strou;?></HideEULAPage>',
'<NetworkLocation><?echo $strin; ?>NetworkLocation<? echo $strou; ?></NetworkLocation>',
'<ProtectYourPC><? echo $strin;?>ProtectComputer<? echo $strou;?></ProtectYourPC>',
'<SkipUserOOBE>true</SkipUserOOBE>',
'<SkipMachineOOBE>true</SkipMachineOOBE>',
'</OOBE>',
'<UserAccounts>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
'<Password>',
'<Value><? echo $strin;?>Password<? echo $strou;?></Value>',
'<PlainText>true</PlainText>',
'</Password>',
'<Description><? echo $strin;?>Description<? echo $strou;?></Description>',
'<DisplayName><? echo $strin;?>FullName<? echo $strou;?></DisplayName>',
'<Group><? echo $strin;?>Group<? echo $strou;?></Group>',
'<Name><? echo $strin;?>FullName<? echo $strou;?></Name>',
'</LocalAccount>',
'</LocalAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin; ?>PasswordAdmin<? echo $strou; ?></Value>',
'<PlainText>true</PlainText>',
'</AdministratorPassword>',
'</UserAccounts>',
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<RequiresUserInput>false</RequiresUserInput>',
'<Order>1</Order>',
'<Description>Disable auto-update</Description>',
'<CommandLine>reg add &quot;HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update&quot; /v AUOptions /t REG_DWORD /d <? echo $strin; ?>Updates<? echo $strou; ?>/f</CommandLine>',
'</SynchronousCommand>',
'</FirstLogonCommands>',
'</component>',
'</settings>',
'<cpi:offlineImage cpi:source="catalog:d:/sources/install_windows 7 ultimate.clg" xmlns:cpi="urn:schemas-microsoft-com:cpi" />',
'</unattend>',
].join('\r\n');
</script> 

<?php
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/data_Windows_Answer_File_Generator.inc.php");
require("../includes/class_form.php");
?>
<!--Click on to validate disposed of the response file
.on smb: // ipPulse / postinst / sysprep /-->
<?php
if(isset($_SESSION['parameters']))
{//If this session exists : editing file, else creating file
	$parameters = $_SESSION['parameters'];
}

$f = new ValidatingForm(array("id" => "formxml"));
$f->add(new HiddenTpl("codeToCopy"), array("value" => "", "hide" => True));
$f->add(new HiddenTpl("infobulexml"),array("value" => '', "hide" => True));


//==== NEW SECTION ====
// Installation Notes
//=====================
//Add section title
$f->add(new TitleElement(_T("Installation Notes", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Installation_Notes',$InfoBule_Installation_Notes)));
$f->push(new Table());

	//_____________
	$f->add(
		new TrFormElement(_T('Title','imaging'), new InputTplTitle('Location',"name file xml")),
		array("required" => True,'value'=>(isset($parameters)) ? $parameters['Title'] : '')
	);

	//_____________
	$f->add(new TrFormElement("Notes".":", new OptTextareaTpl(array('name'=>'Comments','value'=>(isset($parameters)) ? htmlentities($parameters['Notes']) : 'Enter your comments here...'))));
$f->pop();

//Add empty line for separation
$f->add( new SepTpl());

//==== NEW SECTION ====
// General Settings
//=====================
$f->add(new TitleElement(_T("General Settings","imaging")));
$f->add(new TrFormElement("",new Iconereply('General_Settings',$InfoBule_General_Settings)));
$f->push(new Table());

    //_____________
    $key1 = new InputTplTitle('ProductKey1',$InfoBule_ProductKey);
    $key1->setSize(5);
    $key2 = new InputTplTitle('ProductKey2',$InfoBule_ProductKey);
    $key2->setSize(5);
    $key3 = new InputTplTitle('ProductKey3',$InfoBule_ProductKey);
    $key3->setSize(5);
    $key4 = new InputTplTitle('ProductKey4',$InfoBule_ProductKey);
    $key4->setSize(5);
    $key5 = new InputTplTitle('ProductKey5',$InfoBule_ProductKey);
    $key5->setSize(5);
    $fields =   array(
                        $key1,new SpanElement("-"),
                        $key2,new SpanElement("-"),
                        $key3,new SpanElement("-"),
                        $key4,new SpanElement("-"),
                        $key5
                );
    $values = array(
                        (isset($parameters)) ? $parameters['ProductKey1'] : "HYF8J","",
                        (isset($parameters)) ? $parameters['ProductKey2'] : "CVRMY","",
                        (isset($parameters)) ? $parameters['ProductKey3'] : "CM74G","",
                        (isset($parameters)) ? $parameters['ProductKey4'] : "RPHKF","",
                        (isset($parameters)) ? $parameters['ProductKey5'] : "PW487"

    );
    //_____________    
    $f->add(
        new TrFormElement(_T('Product Key','imaging').":", new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Organization Name','imaging').":", new InputTplTitle('OrginazationName',$InfoBule_OrginazationName)),
        array("value" => (isset($parameters)) ? $parameters['OrginazationName'] : 'Siveo', "required" => True)
    );
    //_____________
    $SetupUILanguage = new SelectItemtitle("SetupUILanguage",$InfoBule_SetupUILanguage);
    $SetupUILanguage->setElements($eleUILanguage);
    $SetupUILanguage->setElementsVal($valUILanguage);
     //_____________
    $f->add(
        new TrFormElement(_T('Setup Language','imaging').":", $SetupUILanguage),
        array("value" => (isset($parameters)) ? $parameters['SetupUILanguage'] : "fr-FR","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Computer Name','imaging').":", new InputTplTitle('ComputerName',$Infobule_ComputerName)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['ComputerName'] : 'windows7-PC')
    );
$f->pop();
$f->add( new SepTpl());

//==== NEW SECTION ====
// Specialize Settings
//=====================
$f->add(new TitleElement(_T("Specialize Settings","imaging")));
$f->add(new Iconereply('Specialize_Settings',_T("Configure Specialize Settings", "imaging")));
$f->push(new Table());

    //_____________
    $CopyProfile = new SelectItemtitle("CopyProfile", $InfoBule_CopyProfile);
    $CopyProfile->setElements($yes_no);
    $CopyProfile->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Copy Profile','imaging').":", $CopyProfile),
        array("value" => (isset($parameters)) ? $parameters['CopyProfile'] : "true","required" => True)
    );
    //_____________
    $ExtendOSPartition = new SelectItemtitle("ExtendOSPartition",$InfoBule_ExtendOSPartition);
    $ExtendOSPartition->setElements($yes_no);
    $ExtendOSPartition->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Extend OS Partition','imaging').":", $ExtendOSPartition),
        array("value" => (isset($parameters)) ? $parameters['ExtendOSPartition'] : "true","required" => True)
    );
    //_____________
    $ShowWindowsLive = new SelectItemtitle("ShowWindowsLive", $InfoBule_ShowWindowsLive);
    $ShowWindowsLive->setElements($yes_no);
    $ShowWindowsLive->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Show Windows Live','imaging').":", $ShowWindowsLive),
        array("value" => (isset($parameters)) ? $parameters['ShowWindowsLive'] : "false","required" => True)
    );
	 $f->add(
        new TrFormElement(_T('Domain','imaging').":", new InputTplTitle('Domain',$InfoBule_Domain)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['Domain'] : '')
    );
	$f->add(
        new TrFormElement(_T('Domain User','imaging').":", new InputTplTitle('DomainUser',$InfoBule_DomainUser)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['DomainUser'] : '')
    );
	$f->add(
        new TrFormElement(_T('Domain Password','imaging').":", new InputTplTitle('DomainPassword',$InfoBule_DomainPassword)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['DomainPassword'] : '')
    );
	$f->add(
        new TrFormElement(_T('Join Domain','imaging').":", new InputTplTitle('JoinDomain',$InfoBule_JoinDomain)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['JoinDomain'] : '')
    );
	$f->add(
        new TrFormElement(_T('MachineObjectOU','imaging').":", new InputTplTitle('MachineObjectOU',$InfoBule_MachineObjectOU)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['MachineObjectOU'] : '')
    );
$f->pop();
$f->add( new SepTpl());


//==== NEW SECTION ====
// Regional Settings
//=====================
$f->add(new TitleElement(_T("Regional Settings","imaging")));
$f->push(new Table());
$f->add(new Iconereply('Regional_Settings',_T("Configure International Settings in Windows", "imaging")));

	//_____________
    $InputLocale = new SelectItemtitle("InputLocale",$Infobule_InputLocale);
    $InputLocale->setElements($elementInputarray);
    $InputLocale->setElementsVal($valeurInputarray);
    $f->add(
        new TrFormElement(_T('Keyboard or input method','imaging').":", $InputLocale),
        array("value" =>(isset($parameters)) ? $parameters['InputLocale'] : '1036:0000040c' ,"required" => True)
    );
    //_____________
    $UserLocale = new SelectItemtitle("UserLocale",$InfoBule_UserLocale);
    $UserLocale->setElements($eleUILanguage);
    $UserLocale->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('Currency and Date format','imaging').":", $UserLocale),
        array("value" =>(isset($parameters)) ? $parameters['UserLocale'] : "fr-FR","required" => True)
    ); 
    //_____________
    $TimeZone = new SelectItemtitle("TimeZone",$InfoBule_TimeZone);
    $TimeZone->setElements($element_timezone);
    $TimeZone->setElementsVal($val_timezone);
    $f->add(
        new TrFormElement(_T('Time Zone','imaging').":", $TimeZone),
        array("value" => (isset($parameters)) ? $parameters['TimeZone'] : "Romance Standard Time","required" => True)
    );// $val_timezone[$timezoneprobable[0]]
    //_____________
    $UILanguage = new SelectItemtitle("UILanguage",$InfoBule_UILanguage);
    $UILanguage->setElements($eleUILanguage);
    $UILanguage->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('UI Language','imaging').":", $UILanguage),
        array("value" =>(isset($parameters)) ? $parameters['UILanguage'] : 'fr-FR' ,"required" => True)
    );
$f->pop();
$f->add( new SepTpl());

//==== NEW SECTION ====
// OOBE
//=====================
$f->add(new TitleElement(_T("Out Of Box Experience","imaging")));
$f->add(new Iconereply('Out_Of_Box_Experience',$InfoBule_Out_Of_Box_Experience));
$f->push(new Table());

    //_____________
    $ProtectComputer = new SelectItemtitle("ProtectComputer",$InfoBule_ProtectComputer);
    $ProtectComputer->setElements($ProtectComputerTabElement);
    $ProtectComputer->setElementsVal(array('1','2','3'));
    $f->add(
        new TrFormElement(_T('Protect Your Computer','imaging').":", $ProtectComputer),
        array("value" => "1","required" => True)
    );
    //_____________
    $Updates = new SelectItemtitle("Updates",$InfoBule_Updates);
    $Updates->setElements($UpdatesTabElement);
    $Updates->setElementsVal(array('1','2','3','4'));
    $f->add(
        new TrFormElement(_T('System Updates','imaging').":", $Updates),
        array("value" => (isset($parameters)) ? $parameters['Updates'] : "3","required" => True)
    );
    //_____________
    $NetworkLocation = new SelectItemtitle("NetworkLocation",$InfoBule_NetworkLocation );
    $NetworkLocation->setElements(array('Home','Work','Other'));
    $NetworkLocation->setElementsVal(array('Home','Work','Other'));
    $f->add(
        new TrFormElement(_T('Network Location','imaging').":", $NetworkLocation),
        array("value" => (isset($parameters)) ? $parameters['NetworkLocation'] : "Work","required" => True)
    );
    //_____________
    $HideEULA = new SelectItemtitle("HideEULA",$InfoBule_HideEULA); 
    $HideEULA->setElements($yes_no);
    $HideEULA->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Hide EULA page','imaging').":", $HideEULA),
        array("value" => (isset($parameters)) ? $parameters['HideEULA'] : "true","required" => True)
    );
$f->pop();
$f->add( new SepTpl());

//==== NEW SECTION ====
// Administrators Accounts
//=====================
$f->add(new TitleElement(_T("Administrator Account", "imaging")));
$f->push(new Table());

	//_____________   
    $f->add(
        new TrFormElement(_T('Password','imaging'), new InputTplTitle('PasswordAdmin',$InfoBule_PasswordAdmin)),
        array(  "required" => True,
                "value" => (isset($parameters)) ? $parameters['PasswordAdmin'] : "")
    );
$f->pop();
$f->add( new SepTpl());

//==== NEW SECTION ====
// Users Accounts
//=====================
$f->add(new TitleElement(_T("User Account", "imaging")));
$f->add(new Iconereply('User_Account', $InfoBule_User_Account ));
$f->push(new Table());

    //_____________
    $f->add(
        new TrFormElement(_T('User Name','imaging'), new InputTplTitle('FullName',$InfoBule_FullName)),
        array("value" => (isset($parameters)) ? $parameters['FullName'] : "Temp","required" => True)
    );
    //_____________
    $Group = new SelectItemtitle("Group",$InfoBule_Group);
    $Group->setElements($GroupTabElement);
    $Group->setElementsVal($GroupTabValue);
    $f->add(
        new TrFormElement(_T('Group','imaging').":", $Group),
        array("value" => (isset($parameters)) ? $parameters['Group'] : "Users","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Description','imaging'), new InputTplTitle('Description',$InfoBule_Description)),
        array("value" => (isset($parameters)) ? $parameters['Description'] : "Temp","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Password: (Optional)','imaging'), new InputTplTitle('Password',$InfoBule_Password)),
        array("value" => (isset($parameters)) ? $parameters['Password'] : ""));
 
    $bo = new buttonTpl('bvalid', _T("Validate",'imaging'),'btnPrimary',_T("Create Xml Windows Answer File Generator", "imaging"));
    $rr = new TrFormElementcollapse($bo);
    $rr->setstyle("text-align: center;");
    $f->add(
            $rr
    );
    //------------------
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElementtitle(_T("Xml Windows Answer File Generator", "imaging"),Null, 'To have the file on smb://ipPulse/postinst/sysprep/'."\n".
                                                    'click on Validation',"spanxml"),// $InfoBule_showxml
                                                        new Iconereply('awfg_show',$InfoBule_showxml)
                                                )
                                )
        )
    );
    $f->display();

echo "<div id='sysprepCreated'></div>";
echo "<div title= 'jffffffffffffffffffffffffffffffffffffffffffffjjj'>";
    echo "<pre  id='codeTocopy2' style='width:100%;'></pre>";
echo "</div>";
?>
