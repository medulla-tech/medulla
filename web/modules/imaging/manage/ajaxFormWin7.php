<?php
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
//x86
'<settings pass="windowsPE">',
'<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SetupUILanguage>',
'<UILanguage><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UILanguage>',
'<\/SetupUILanguage>',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?><\/InputLocale>',
'<SystemLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/SystemLocale>',
'<UILanguage><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UILanguage>',
'<UserLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UserLocale>',          
'<\/component>',
'<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SetupUILanguage>',
'<UILanguage><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UILanguage>',
'<\/SetupUILanguage>',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?><\/InputLocale>',
'<SystemLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/SystemLocale>',
'<UILanguage><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UILanguage>',
'<UserLocale><? echo $strin;?>SetupUILanguage<? echo $strou;?><\/UserLocale>',          
'<\/component>',
'<component name="Microsoft-Windows-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<Diagnostics>',
'<OptIn>false<\/OptIn>',
'<\/Diagnostics>',
'<DiskConfiguration>',
'<WillShowUI>OnError<\/WillShowUI>',
'<Disk wcm:action="add">',
'<DiskID><? echo $strin;?>InstallDisk<? echo $strou;?><\/DiskID>',
'<WillWipeDisk><? echo $strin;?>WipeDisk<? echo $strou;?><\/WillWipeDisk>',
'<CreatePartitions>',
//System Reserved partition
'<CreatePartition wcm:action="add">',
'<Order>1<\/Order>',
'<Type>Primary<\/Type>',
'<Size>100<\/Size>',
'<\/CreatePartition>',
//OS partition
'<CreatePartition wcm:action="add">',
'<Order><? echo $strin;?>PartitionOrder<? echo $strou;?><\/Order>',
'<Type>Primary<\/Type>',
'<Extend>true<\/Extend>',
'<\/CreatePartition>',
'<\/CreatePartitions>',
//Modify the partition attributes
'<ModifyPartitions>',
//Settings for system reserved partition
'<ModifyPartition wcm:action="add">',
'<Format>NTFS<\/Format>',
'<Label>System Reserved<\/Label>',
'<Order>1<\/Order>',
'<Active>true<\/Active>',
'<PartitionID>1<\/PartitionID>',
'<TypeID>0x27<\/TypeID>',
'<\/ModifyPartition>',
//Settings for OS partition
'<ModifyPartition wcm:action="add">',
'<Active>true<\/Active>',
'<Format><? echo $strin;?>Format<? echo $strou;?><\/Format>',
'<Label><? echo $strin;?>Label<? echo $strou;?><\/Label>',
'<Letter><? echo $strin;?>DriveLetter<? echo $strou;?><\/Letter>',
'<Order><? echo $strin;?>PartitionOrder<? echo $strou;?><\/Order>',
'<PartitionID><? echo $strin;?>PartitionOrder<? echo $strou;?><\/PartitionID>',
'<\/ModifyPartition>',
'<\/ModifyPartitions>',
'<\/Disk>',
'<\/DiskConfiguration>',
//Install OS to disk and partition
'<ImageInstall>',
'<OSImage>',
'<InstallTo>',
'<DiskID><? echo $strin;?>InstallDisk<? echo $strou;?><\/DiskID>',
'<PartitionID><? echo $strin;?>PartitionOrder<? echo $strou;?><\/PartitionID>',
'<\/InstallTo>',
'<WillShowUI>OnError<\/WillShowUI>',
'<InstallToAvailablePartition>false<\/InstallToAvailablePartition>',
'<\/OSImage>',
'<\/ImageInstall>',
'<UserData>',
'<AcceptEula><? echo $strin;?>AcceptEULA<? echo $strou;?><\/AcceptEula>',
'<FullName><? echo $strin;?>FullName<? echo $strou;?><\/FullName>',
'<Organization><? echo $strin;?>OrginazationName<? echo $strou;?><\/Organization>',
'<ProductKey>',
'<Key><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></Key>',
'</ProductKey>',
'<\/UserData>',
'<EnableFirewall><? echo $strin;?>EnableFirewall<? echo $strou;?><\/EnableFirewall>',
'<\/component>',
'<component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<Diagnostics>',
'<OptIn>false<\/OptIn>',
'<\/Diagnostics>',
'<DiskConfiguration>',
'<WillShowUI>OnError<\/WillShowUI>',
'<Disk wcm:action="add">',
'<DiskID><? echo $strin;?>InstallDisk<? echo $strou;?><\/DiskID>',
'<WillWipeDisk><? echo $strin;?>WipeDisk<? echo $strou;?><\/WillWipeDisk>',
'<CreatePartitions>',
//System Reserved partition
'<CreatePartition wcm:action="add">',
'<Order>1<\/Order>',
'<Type>Primary<\/Type>',
'<Size>100<\/Size>',
'<\/CreatePartition>',
//OS partition
'<CreatePartition wcm:action="add">',
'<Order><? echo $strin;?>PartitionOrder<? echo $strou;?><\/Order>',
'<Type>Primary<\/Type>',
'<Extend>true<\/Extend>',
'<\/CreatePartition>',
'<\/CreatePartitions>',
//Modify the partition attributes
'<ModifyPartitions>',
//Settings for system reserved partition
'<ModifyPartition wcm:action="add">',
'<Format>NTFS<\/Format>',
'<Label>System Reserved<\/Label>',
'<Order>1<\/Order>',
'<Active>true<\/Active>',
'<PartitionID>1<\/PartitionID>',
'<TypeID>0x27<\/TypeID>',
'<\/ModifyPartition>',
//Settings for OS partition
'<ModifyPartition wcm:action="add">',
'<Active>true<\/Active>',
'<Format><? echo $strin;?>Format<? echo $strou;?><\/Format>',
'<Label><? echo $strin;?>Label<? echo $strou;?><\/Label>',
'<Letter><? echo $strin;?>DriveLetter<? echo $strou;?><\/Letter>',
'<Order><? echo $strin;?>PartitionOrder<? echo $strou;?><\/Order>',
'<PartitionID><? echo $strin;?>PartitionOrder<? echo $strou;?><\/PartitionID>',
'<\/ModifyPartition>',
'<\/ModifyPartitions>',
'<\/Disk>',
'<\/DiskConfiguration>',
//Install OS to disk and partition
'<ImageInstall>',
'<OSImage>',
'<InstallTo>',
'<DiskID><? echo $strin;?>InstallDisk<? echo $strou;?><\/DiskID>',
'<PartitionID><? echo $strin;?>PartitionOrder<? echo $strou;?><\/PartitionID>',
'<\/InstallTo>',
'<WillShowUI>OnError<\/WillShowUI>',
'<InstallToAvailablePartition>false<\/InstallToAvailablePartition>',
'<\/OSImage>',
'<\/ImageInstall>',
'<UserData>',
'<AcceptEula><? echo $strin;?>AcceptEULA<? echo $strou;?><\/AcceptEula>',
'<FullName><? echo $strin;?>FullName<? echo $strou;?><\/FullName>',
'<Organization><? echo $strin;?>OrginazationName<? echo $strou;?><\/Organization>',
'<ProductKey>',
'<Key><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></Key>',
'</ProductKey>',
'<\/UserData>',
'<EnableFirewall>true<\/EnableFirewall>',
'<\/component>',
'<\/settings>',

'<settings pass="generalize">',
'<component name="Microsoft-Windows-Security-SPP" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//Skip rearm
'<SkipRearm><? echo $strin;?>SkipRearm<? echo $strou;?><\/SkipRearm>',
'<\/component>',
'<\/settings>',

'<settings pass="generalize">',
'<component name="Microsoft-Windows-Security-SPP" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//Skip rearm
'<SkipRearm><? echo $strin;?>SkipRearm<? echo $strou;?><\/SkipRearm>',
'<\/component>',
'<\/settings>',





'<!-- ******SETTING SPECIALIZE****** -->', 
'<settings pass="specialize">',

'<component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'   <Extend>',
'      <? echo $strin;?>ExtendOSPartition<? echo $strou;?>',
'   </Extend>',
'</ExtendOSPartition>',
'            <RunSynchronous>',
'                <RunSynchronousCommand wcm:action="add">',
'                    <Order>1</Order>',
'                    <Path>net user administrator /active:yes</Path>',
'                </RunSynchronousCommand>',
'            </RunSynchronous>',
'</component>',
'<component name="Microsoft-Windows-Deployment" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'   <Extend>',
'      <? echo $strin;?>ExtendOSPartition<? echo $strou;?>',
'   </Extend>',
'</ExtendOSPartition>',
'            <RunSynchronous>',
'                <RunSynchronousCommand wcm:action="add">',
'                    <Order>1</Order>',
'                    <Path>net user administrator /active:yes</Path>',
'                </RunSynchronousCommand>',
'            </RunSynchronous>',
'</component>',
'<component name="Microsoft-Windows-Security-SPP-UX" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//Skip windows auto activation
'<SkipAutoActivation><? echo $strin;?>SkipAutoActivation<? echo $strou;?><\/SkipAutoActivation>',
'<\/component>',

'<component name="Microsoft-Windows-Security-SPP-UX" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//Skip windows auto activation
'<SkipAutoActivation><? echo $strin;?>SkipAutoActivation<? echo $strou;?><\/SkipAutoActivation>',
'<\/component>',

'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin;?>ComputerName<? echo $strou;?><\/ComputerName>',
//Timezone settings
'<TimeZone><? echo $strin;?>TimeZone<? echo $strou;?><\/TimeZone>',
'<ProductKey>',
'<Key><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></Key>',
'</ProductKey>',
'<RegisteredOwner><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOwner>',
'<RegisteredOrganization><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOrganization>',
'<CopyProfile><? echo $strin;?>CopyProfile<? echo $strou;?></CopyProfile>',
'<ShowWindowsLive><? echo $strin;?>ShowWindowsLive<? echo $strou;?></ShowWindowsLive>',
'<\/component>',

'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin;?>ComputerName<? echo $strou;?><\/ComputerName>',
//Timezone settings
'<TimeZone><? echo $strin;?>TimeZone<? echo $strou;?><\/TimeZone>',
'<ProductKey>',
'<Key><? echo $strin;?>ProductKey1<? echo $strou;?>-<? echo $strin;?>ProductKey2<? echo $strou;?>-<? echo $strin;?>ProductKey3<? echo $strou;?>-<? echo $strin;?>ProductKey4<? echo $strou;?>-<? echo $strin;?>ProductKey5<? echo $strou;?></Key>',
'</ProductKey>',
'<RegisteredOwner><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOwner>',
'<RegisteredOrganization><? echo $strin;?>OrginazationName<? echo $strou;?></RegisteredOrganization>',
'<CopyProfile><? echo $strin;?>CopyProfile<? echo $strou;?></CopyProfile>',
'<ShowWindowsLive><? echo $strin;?>ShowWindowsLive<? echo $strou;?></ShowWindowsLive>',
'<\/component>',
'<\/settings>',
'<!-- ****************************** -->', 
'<settings pass="oobeSystem">',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?><\/InputLocale>',
'<UILanguage><? echo $strin;?>UILanguage<? echo $strou;?><\/UILanguage>',
'<UserLocale><? echo $strin;?>UILanguage<? echo $strou;?><\/UserLocale>', 
'<\/component>',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin;?>InputLocale<? echo $strou;?><\/InputLocale>',
'<UILanguage><? echo $strin;?>UILanguage<? echo $strou;?><\/UILanguage>',
'<UserLocale><? echo $strin;?>UILanguage<? echo $strou;?><\/UserLocale>', 
'<\/component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//Product key
'<RegisteredOwner><? echo $strin;?>FullName<? echo $strou;?><\/RegisteredOwner>',
'<OOBE>',
//Hide EULA page
'<HideEULAPage><? echo $strin;?>HideEULA<? echo $strou;?><\/HideEULAPage>',
//Network location
'<NetworkLocation><? echo $strin;?>NetworkLocation<? echo $strou;?><\/NetworkLocation>',
//System updates
'<ProtectYourPC><? echo $strin;?>ProtectComputer<? echo $strou;?><\/ProtectYourPC>',
//Hide wireless setup
'<HideWirelessSetupInOOBE><? echo $strin;?>HideWireless<? echo $strou;?><\/HideWirelessSetupInOOBE>',
//Skip Machine OOBE
'<SkipMachineOOBE><? echo $strin;?>MachineOOBE<? echo $strou;?><\/SkipMachineOOBE>',
//Skip User OOBE
'<SkipUserOOBE><? echo $strin;?>UserOOBE<? echo $strou;?><\/SkipUserOOBE>',
'<\/OOBE>',
//Disable automatic daylight savings mode
'<DisableAutoDaylightTimeSet><? echo $strin;?>DaylightSettings<? echo $strou;?><\/DisableAutoDaylightTimeSet>',
//Windows Update settings
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<RequiresUserInput>false<\/RequiresUserInput>',
'<Order>1<\/Order>',
'<Description>Disable Auto Updates<\/Description>',
'<CommandLine>reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update" /v AUOptions /t REG_DWORD /d <? echo $strin;?>Updates<? echo $strou;?> /f<\/CommandLine>',
'<\/SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Description>Control Panel View</Description>',
'<Order>2</Order>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v StartupPage /t REG_DWORD /d <? echo $strin;?>ControlPanelView<? echo $strou;?> /f</CommandLine>',
'<RequiresUserInput>true</RequiresUserInput>',
'</SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Order>3</Order>',
'<Description>Control Panel Icon Size</Description>',
'<RequiresUserInput>false</RequiresUserInput>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v AllItemsIconView /t REG_DWORD /d <? echo $strin;?>ControlPanelIconSize<? echo $strou;?> /f</CommandLine>',
'</SynchronousCommand>',
'<\/FirstLogonCommands>',
'<AutoLogon>',
'<Password>',
'<Value><? echo $strin;?>Password<? echo $strou;?><\/Value>',
'<PlainText>true<\/PlainText>',
'<\/Password>',
//Autologon enabled/disabled
'<Enabled><? echo $strin;?>Autologon<? echo $strou;?><\/Enabled>',
'<Username><? echo $strin;?>FullName<? echo $strou;?><\/Username>',
'<\/AutoLogon>',
'<UserAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin;?>PasswordAdmin<? echo $strou;?></Value>',
'<!-- PlainText true  : Specifies that the password appears in plain text in the answer file -->',
'<!-- PlainText false : Specifies that the password is hidden in the answer file -->',
'<PlainText>false</PlainText>',
'</AdministratorPassword>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
'<Password>',
//User password
'<Value><? echo $strin;?>Password<? echo $strou;?><\/Value>',
'<PlainText>true<\/PlainText>',
'<\/Password>',
//Description
'<Description><? echo $strin;?>Description<? echo $strou;?><\/Description>',
//User name
'<DisplayName><? echo $strin;?>FullName<? echo $strou;?><\/DisplayName>',
//User group settings
'<Group><? echo $strin;?>Group<? echo $strou;?><\/Group>',
//User name
'<Name><? echo $strin;?>FullName<? echo $strou;?><\/Name>',
'<\/LocalAccount>',
'<\/LocalAccounts>',
'<\/UserAccounts>',
'<\/component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<RegisteredOwner><? echo $strin;?>FullName<? echo $strou;?><\/RegisteredOwner>',
'<OOBE>',
//Hide EULA page
'<HideEULAPage><? echo $strin;?>HideEULA<? echo $strou;?><\/HideEULAPage>',
//Network location
'<NetworkLocation><? echo $strin;?>NetworkLocation<? echo $strou;?><\/NetworkLocation>',
//System updates
'<ProtectYourPC><? echo $strin;?>ProtectComputer<? echo $strou;?><\/ProtectYourPC>',
//Hide wireless setup
'<HideWirelessSetupInOOBE><? echo $strin;?>HideWireless<? echo $strou;?><\/HideWirelessSetupInOOBE>',
//Skip Machine OOBE
'<SkipMachineOOBE><? echo $strin;?>MachineOOBE<? echo $strou;?><\/SkipMachineOOBE>',
//Skip User OOBE
'<SkipUserOOBE><? echo $strin;?>UserOOBE<? echo $strou;?><\/SkipUserOOBE>',
'<\/OOBE>',
//Disable automatic daylight savings mode
'<DisableAutoDaylightTimeSet><? echo $strin;?>DaylightSettings<? echo $strou;?><\/DisableAutoDaylightTimeSet>',
//Windows Update settings
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<RequiresUserInput>false<\/RequiresUserInput>',
'<Order>1<\/Order>',
'<Description>Disable Auto Updates<\/Description>',
'<CommandLine>reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update" /v AUOptions /t REG_DWORD /d <? echo $strin;?>Updates<? echo $strou;?> /f<\/CommandLine>',
'<\/SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Description>Control Panel View</Description>',
'<Order>2</Order>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v StartupPage /t REG_DWORD /d <? echo $strin;?>ControlPanelView<? echo $strou;?> /f</CommandLine>',
'<RequiresUserInput>true</RequiresUserInput>',
'</SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Order>3</Order>',
'<Description>Control Panel Icon Size</Description>',
'<RequiresUserInput>false</RequiresUserInput>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v AllItemsIconView /t REG_DWORD /d <? echo $strin;?>ControlPanelIconSize<? echo $strou;?> /f</CommandLine>',
'</SynchronousCommand>',
'<\/FirstLogonCommands>',
'<AutoLogon>',
'<Password>',
'<Value><? echo $strin;?>Password<? echo $strou;?><\/Value>',
'<PlainText>true<\/PlainText>',
'<\/Password>',
//Autologon enabled/disabled
'<Enabled><? echo $strin;?>Autologon<? echo $strou;?><\/Enabled>',
'<Username><? echo $strin;?>FullName<? echo $strou;?><\/Username>',
'<\/AutoLogon>',
'<UserAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin;?>PasswordAdmin<? echo $strou;?></Value>',
'<!-- PlainText true  : Specifies that the password appears in plain text in the answer file -->',
'<!-- PlainText false : Specifies that the password is hidden in the answer file -->',
'<PlainText>false</PlainText>',
'</AdministratorPassword>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
'<Password>',
//User password
'<Value><? echo $strin;?>Password<? echo $strou;?><\/Value>',
'<PlainText>true<\/PlainText>',
'<\/Password>',
//Description
'<Description><? echo $strin;?>Description<? echo $strou;?><\/Description>',
//User name
'<DisplayName><? echo $strin;?>FullName<? echo $strou;?><\/DisplayName>',
//User group settings
'<Group><? echo $strin;?>Group<? echo $strou;?><\/Group>',
//User name
'<Name><? echo $strin;?>FullName<? echo $strou;?><\/Name>',
'<\/LocalAccount>',
'<\/LocalAccounts>',
'<\/UserAccounts>',
'<\/component>',
'<\/settings>',
//Disable UAC
'<settings pass="offlineServicing">',
'<component name="Microsoft-Windows-LUA-Settings" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<EnableLUA><? echo $strin;?>EnableUAC<? echo $strou;?><\/EnableLUA>',
'<\/component>',
'<\/settings>',
'<settings pass="offlineServicing">',
'<component name="Microsoft-Windows-LUA-Settings" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<EnableLUA><? echo $strin;?>EnableUAC<? echo $strou;?><\/EnableLUA>',
'<\/component>',
'<\/settings>',
'<cpi:offlineImage cpi:source="catalog:d:/sources/install_windows 7 ultimate.clg" xmlns:cpi="urn:schemas-microsoft-com:cpi" />',
'<\/unattend>',
].join('\r\n');
</script> 

<?php
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/data_Windows_Answer_File_Generator.inc.php");
?>
<!--Click on to validate disposed of the response file
.on smb: // ipPulse / postinst / sysprep /-->
<?php
//array('enctype'=>"text/xml")
    $f = new ValidatingForm(array("id" => "formxml"));
    $f->add(new HiddenTpl("codeToCopy"), array("value" => "", "hide" => True));
    $f->add(new HiddenTpl("infobulexml"),array("value" => '', "hide" => True));
    $f->push(new Table());
    //------------------jQuery('input[name=codeToCopy]').val(newXml);
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Installation Notes", "imaging")),
                                                        new Iconereply('Installation_Notes',$InfoBule_Installation_Notes)
                                                )
                                )
        )
    );
    //_____________
    $f->add(//
        new TrFormElement(_T('Title','imaging'), new InputTplTitle('Location',"name file xml")),
        array("required" => true )
    );
    //_____________     
    $f->add(new TrFormElement("Notes".":", new TextareaTpl('Comments')));
    //------------------
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("General Settings", "imaging")),
                                                        new Iconereply('General_Settings',$InfoBule_General_Settings))
                                                )
                                )
        );
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
                        "FJ82H","",
                        "XT6CR","",
                        "J8D7P","",
                        "XQJJ2","",
                        "GPDD4"
    );
    //_____________    
    $f->add(
        new TrFormElement(_T('Product Key:','imaging').":", new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
    //_____________
    $EULA = new SelectItemtitle("AcceptEULA",$InfoBule_AcceptEULA);
    $EULA->setElements($yes_no);
    $EULA->setElementsVal(array('true', 'false'));
    $f->add(
        new TrFormElement(_T('Accept EULA','imaging').":", $EULA),
        array("value" => "true","required" => True)
    );
    //_____________
    $Skipactivation = new SelectItemtitle("SkipAutoActivation",$InfoBule_SkipAutoActivation);
    $Skipactivation->setElements($yes_no);
    $Skipactivation->setElementsVal(array('true', 'false'));
    $f->add(
        new TrFormElement(_T('Skip automatic activation','imaging').":", $Skipactivation),
        array("value" => "true","required" => True)
    );
    //_____________
    $SkipLicense = new SelectItemtitle("SkipRearm",$InfoBule_SkipRearm);
    $SkipLicense->setElements($yes_no);
    $SkipLicense->setElementsVal(array('1', '0'));
    $f->add(
        new TrFormElement(_T('Skip License Rearm','imaging').":", $SkipLicense),
        array("value" => "1","required" => True)
    );
    //_____________
    $SetupUILanguage = new SelectItemtitle("SetupUILanguage",$InfoBule_SetupUILanguage);
    $SetupUILanguage->setElements($eleUILanguage);
    $SetupUILanguage->setElementsVal($valUILanguage);
     //_____________
    $f->add(
        new TrFormElement(_T('Setup Language','imaging').":", $SetupUILanguage),
        array("value" => "fr-FR","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Computer Name','imaging').":", new InputTplTitle('ComputerName',$Infobule_ComputerName)),
        array("required" => True,"value" =>'windows7-PC')
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Organization Name','imaging').":", new InputTplTitle('OrginazationName',$InfoBule_OrginazationName)),
        array("value" => 'Mandriva', "required" => True)
    );
    //------------------
    //------------------
    //specialize
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Specialize Settings", "imaging")),
                                                        new Iconereply('Specialize_Settings',_T("Configure Specialize Settings", "imaging"))
                                                )
                                )
        )
    );
    //_____________
    $ExtendOSPartition = new SelectItemtitle("ExtendOSPartition",$InfoBule_ExtendOSPartition);
    $ExtendOSPartition->setElements($yes_no);
    $ExtendOSPartition->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Extend OS Partition','imaging').":", $ExtendOSPartition),
        array("value" => "true","required" => True)
    );
    //_____________
    $CopyProfile = new SelectItemtitle("CopyProfile", $InfoBule_CopyProfile);
    $CopyProfile->setElements($yes_no);
    $CopyProfile->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Copy Profile','imaging').":", $CopyProfile),
        array("value" => "true","required" => True)
    );
    //_____________
    $ShowWindowsLive = new SelectItemtitle("ShowWindowsLive", $InfoBule_ShowWindowsLive);
    $ShowWindowsLive->setElements($yes_no);
    $ShowWindowsLive->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Show Windows Live','imaging').":", $ShowWindowsLive),
        array("value" => "false","required" => True)
    );
    //------------------
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Regional Settings", "imaging")),
                                                        new Iconereply('Regional_Settings',_T("Configure International Settings in Windows", "imaging"))
                                                )
                                )
        )
    );
    //_____________
    $InputLocale = new SelectItemtitle("InputLocale",$Infobule_InputLocale);
    $InputLocale->setElements($elementInputarray);
    $InputLocale->setElementsVal($valeurInputarray);
    $f->add(
        new TrFormElement(_T('Keyboard or input method','imaging').":", $InputLocale),
        array("value" =>'1036:0000040c' ,"required" => True)
    );
    //_____________
    $UserLocale = new SelectItemtitle("UserLocale",$InfoBule_UserLocale);
    $UserLocale->setElements($eleUILanguage);
    $UserLocale->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('Currency and Date format','imaging').":", $UserLocale),
        array("value" =>"fr-FR","required" => True)
    ); 
    //_____________
    $TimeZone = new SelectItemtitle("TimeZone",$InfoBule_TimeZone);
    $TimeZone->setElements($element_timezone);
    $TimeZone->setElementsVal($val_timezone);
    $f->add(
        new TrFormElement(_T('Time Zone','imaging').":", $TimeZone),
        array("value" => "Romance Standard Time","required" => True)
    );// $val_timezone[$timezoneprobable[0]]
    //_____________
    $UILanguage = new SelectItemtitle("UILanguage",$InfoBule_UILanguage);
    $UILanguage->setElements($eleUILanguage);
    $UILanguage->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('UI Language','imaging').":", $UILanguage),
        array("value" =>'fr-FR' ,"required" => True)
    );
    //---------------------
    //---------------------
     $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Out Of Box Experience", "imaging")),
                                                        new Iconereply('Out_Of_Box_Experience',$InfoBule_Out_Of_Box_Experience)
                                                )
                                )
        )
    );
    //_____________
    $NetworkLocation = new SelectItemtitle("NetworkLocation",$InfoBule_NetworkLocation );
    $NetworkLocation->setElements(array('Home','Work','Other'));
    $NetworkLocation->setElementsVal(array('Home','Work','Other'));
    $f->add(
        new TrFormElement(_T('Network Location','imaging').":", $NetworkLocation),
        array("value" => "Work","required" => True)
    );
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
        array("value" => "3","required" => True)
    );
    //_____________
    $HideEULA = new SelectItemtitle("HideEULA",$InfoBule_HideEULA); 
    $HideEULA->setElements($yes_no);
    $HideEULA->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Hide EULA page','imaging').":", $HideEULA),
        array("value" => "true","required" => True)
    );
    //_____________
    $DaylightSettings = new SelectItemtitle("DaylightSettings",$InfoBule_DaylightSettings); 
    $DaylightSettings->setElements($yes_no);
    $DaylightSettings->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Disable auto daylight timeset','imaging').":", $DaylightSettings),
        array("value" => "true","required" => True)
    );
    //_____________
    $HideWireless = new SelectItemtitle("HideWireless",$Infobule_HideWireless); 
    $HideWireless->setElements($yes_no);
    $HideWireless->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Hide wireless setup in OOBE','imaging').":", $HideWireless),
        array("value" => "true","required" => True)
    );
    //_____________
    $MachineOOBE = new SelectItemtitle("MachineOOBE",$InfoBule_MachineOOBE);
    $MachineOOBE->setElements($yes_no);
    $MachineOOBE->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Skip machine OOBE','imaging').":", $MachineOOBE),
        array("value" => "true","required" => True)
    );
    //_____________
    $UserOOBE = new SelectItemtitle("UserOOBE",$InfoBule_UserOOBE);
    $UserOOBE->setElements($yes_no);
    $UserOOBE->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Skip user OOBE','imaging').":", $UserOOBE),
        array("value" => "true","required" => True)
    );
    //_____________
    $ControlPanelView = new SelectItemtitle("ControlPanelView",$InfoBule_ControlPanelView);
    $ControlPanelView->setElements(array(_T('Category View', "imaging"),_T('Classic View', "imaging")));
    $ControlPanelView->setElementsVal(array('0','1'));
    $f->add(
        new TrFormElement(_T('Control Panel View','imaging').":", $ControlPanelView),
        array("value" => "1","required" => True)
    );
    //_____________
    $ControlPanelIconSize = new SelectItemtitle("ControlPanelIconSize",$InfoBule_ControlPanelIconSize);
    $ControlPanelIconSize->setElements(array(_T('Large', "imaging"),_T('Small', "imaging")));
    $ControlPanelIconSize->setElementsVal(array('0','1'));
    $f->add(
        new TrFormElement(_T('Control Panel Icon Size','imaging').":", $ControlPanelIconSize),
        array("value" => "0","required" => True)
    );
    //------------------
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Partition Settings", "imaging")),
                                                        new Iconereply('Partition_Settings',$Infobule_Partition_Settings)
                                                )
                                )
        )
    );
    //_____________
    $WipeDisk = new SelectItemtitle("WipeDisk",$InfoBule_WipeDisk);
    $WipeDisk->setElements($yes_no);
    $WipeDisk->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Wipe Disk','imaging').":", $WipeDisk),
        array("value" => "false","required" => True)
    );
    //_____________
    $InstallDisk = new SelectItemtitle("InstallDisk",$InfoBule_InstallDisk);
    $InstallDisk->setElements($suite0_5);
    $InstallDisk->setElementsVal($suite0_5);
    $f->add(
        new TrFormElement(_T('Install to disk','imaging').":", $InstallDisk),
        array("value" => "0","required" => True)
    );
    //_____________
    $Format = new SelectItemtitle("Format",$InfoBule_Format);
    $Format->setElements(array('NTFS','FAT32'));
    $Format->setElementsVal(array('NTFS','FAT32'));
    $f->add(
        new TrFormElement(_T('Main Partition Format','imaging').":", $Format),
        array("value" => "NTFS","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement($InfoBule_Label, new InputTplTitle('Label',$InfoBule_Label)),
        array("required" => True,'value' => 'OS')
    );
    //_____________   
    $DriveLetter = new SelectItemtitle("DriveLetter",$InfoBule_DriveLetter);
    $DriveLetter->setElements($DriveLetterTabElement);
    $DriveLetter->setElementsVal($DriveLetterTabElement);
    $f->add(
        new TrFormElement(_T('Main Partition Letter','imaging').":", $DriveLetter),
        array("value" => "C","required" => True)
    );
    //_____________
    $PartitionOrder = new SelectItemtitle("PartitionOrder",$InfoBule_PartitionOrder);
    $PartitionOrder->setElements($suite2_5);
    $PartitionOrder->setElementsVal($suite2_5);
    $f->add(
        new TrFormElement(_T('Partition Order','imaging').":", $PartitionOrder),
        array("value" => "2","required" => True)
    );
    //------------------
    //------------------
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                                                array(  new SpanElement(_T("Administrators Account", "imaging")),
                                                        new Iconereply('Administrators_Account',$InfoBule_Administrators_Account)
                                                )
                                )
        )
    );
    //_____________   
    $f->add(
        new TrFormElement(_T('Password','imaging'), new InputTplTitle('PasswordAdmin',$InfoBule_PasswordAdmin)),
        array(  "required" => True,
                "value" => "bQBhAG4AZAByAGkAdgBhAEEAZABtAGkAbgBpAHMAdAByAGEAdABvAHIAUABhAHMAcwB3AG8AcgBkAA==")
    ); //mandrivaAdministratorPassword
    //--------------
    //--------------
    $f->add(
            new TrFormElement("",       new multifieldTpl(  array(  new SpanElement(_T("User Account", "imaging")),
                                                                        new Iconereply('User_Account', $InfoBule_User_Account )
                                                            )
                                    )
        )
    );
    //_____________
    $f->add(
        new TrFormElement(_T('User Name','imaging'), new InputTplTitle('FullName',$InfoBule_FullName)),
        array("value" => "Temp","required" => True)
    );
    //_____________
    $Group = new SelectItemtitle("Group",$InfoBule_Group);
    $Group->setElements($GroupTabElement);
    $Group->setElementsVal($GroupTabValue);
    $f->add(
        new TrFormElement(_T('Group','imaging').":", $Group),
        array("value" => "Users","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Description','imaging'), new InputTplTitle('Description',$InfoBule_Description)),
        array("value" => "Temp","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Password: (Optional)','imaging'), new InputTplTitle('Password',$InfoBule_Password)),
        array("value" => ""));
    //_____________
    $Autologon = new SelectItemtitle("Autologon",$InfoBule_Autologon);
    $Autologon->setElements($yes_no);
    $Autologon->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Auto Logon','imaging').":", $Autologon),
        array("value" => "true","required" => True)
    );
    //_____________
    $EnableUAC = new SelectItemtitle("EnableUAC",$InfoBule_EnableUAC);
    $EnableUAC->setElements($EnableDisabled);
    $EnableUAC->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('UAC','imaging').":", $EnableUAC),
            array("value" => "false","required" => True)
    );
    //_____________
    $EnableFirewall = new SelectItemtitle("EnableFirewall",$InfoBule_EnableFirewall);
    $EnableFirewall->setElements($EnableDisabled);
    $EnableFirewall->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Enable Firewall','imaging').":", $EnableFirewall),
            array("value" => "true","required" => True)
    );
    //_____________function addButton($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") 
    //$f->addButton("bvalid", _T("Validate",'imaging'),"btnPrimary",'style="text-align: center;"');
    
    
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
//     //------------------
//     //------------------
//     $g = new SpanElement(_T("Xml Windows Answer File Generator", "imaging"));
//     $g->display();
    //_____________
//     $h = new Iconereply('awfg_show',_T("AWFG", "imaging"));$h->display();
echo "<div title= 'jffffffffffffffffffffffffffffffffffffffffffffjjj'>";
    echo "<pre  id='codeTocopy2' style='width:100%;'></pre>";
echo "</div>";
?>
