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
'<? echo $strin; ?>xml version="1.0" encoding="utf-8"<? echo $strou; ?>',
'<unattend xmlns="urn:schemas-microsoft-com:unattend">',
'<!--',
'________________________________',
'OS Windows 10 [x86 and amd64]',
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
//Language Setup
'<settings pass="windowsPE">',
'<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SetupUILanguage>',
'<UILanguage><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguage>',
'</SetupUILanguage>',
'<InputLocale><? echo $strin; ?>InputLocale<? echo $strou; ?></InputLocale>',
'<SystemLocale><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></SystemLocale>',
'<UILanguage><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguage>',
'<UILanguageFallback><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguageFallback>',
'<UserLocale><? echo $strin; ?>UserLocale<? echo $strou; ?></UserLocale>',
'</component>',
'<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SetupUILanguage>',
'<UILanguage><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguage>',
'</SetupUILanguage>',
'<InputLocale><? echo $strin; ?>InputLocale<? echo $strou; ?></InputLocale>',
'<SystemLocale><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></SystemLocale>',
'<UILanguage><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguage>',
'<UILanguageFallback><? echo $strin; ?>SetupUILanguage<? echo $strou; ?></UILanguageFallback>',
'<UserLocale><? echo $strin; ?>UserLocale<? echo $strou; ?></UserLocale>',
'</component>',
//Disk COnfiguration
'<component name="Microsoft-Windows-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<DiskConfiguration>',
'<Disk wcm:action="add">',
'<CreatePartitions>',
//System Reserved
'<CreatePartition wcm:action="add">',
'<Order>1</Order>',
'<Type>Primary</Type>',
'<Size>100</Size>',
'</CreatePartition>',
//OS partition
'<CreatePartition wcm:action="add">',
'<Extend>true</Extend>',
'<Order><? echo $strin; ?>PartitionOrder<? echo $strou; ?></Order>',
'<Type>Primary</Type>',
'</CreatePartition>',
'</CreatePartitions>',
'<ModifyPartitions>',
//Settings for system reserved partition
'<ModifyPartition wcm:action="add">',
'<Active>true</Active>',
'<Format><? echo $strin; ?>Format<? echo $strou; ?></Format>',
'<Label>System Reserved</Label>',
'<Order>1</Order>',
'<PartitionID>1</PartitionID>',
'<TypeID>0x27</TypeID>',
'</ModifyPartition>',
//Settings for OS partition
'<ModifyPartition wcm:action="add">',
'<Active>true</Active>',
'<Format><? echo $strin; ?>Format<? echo $strou; ?></Format>',
'<Label><? echo $strin; ?>Label<? echo $strou; ?></Label>',
'<Letter><? echo $strin; ?>DriveLetter<? echo $strou; ?></Letter>',
'<Order><? echo $strin; ?>PartitionOrder<? echo $strou; ?></Order>',
'<PartitionID><? echo $strin; ?>PartitionOrder<? echo $strou; ?></PartitionID>',
'</ModifyPartition>',
'</ModifyPartitions>',
'<DiskID><? echo $strin; ?>InstallDisk<? echo $strou; ?></DiskID>',
'<WillWipeDisk><? echo $strin; ?>WipeDisk<? echo $strou; ?></WillWipeDisk>',
'</Disk>',
'</DiskConfiguration>',
//Install OS to disk and partition
'<ImageInstall>',
'<OSImage>',
'<InstallTo>',
'<DiskID><? echo $strin; ?>InstallDisk<? echo $strou; ?></DiskID>',
'<PartitionID><? echo $strin; ?>PartitionOrder<? echo $strou; ?></PartitionID>',
'</InstallTo>',
'<InstallToAvailablePartition>false</InstallToAvailablePartition>',
'</OSImage>',
'</ImageInstall>',
//User Data
'<UserData>',
'<AcceptEula><? echo $strin; ?>AcceptEULA<? echo $strou; ?></AcceptEula>',
'<FullName><? echo $strin; ?>FullName<? echo $strou; ?></FullName>',
'<Organization><? echo $strin; ?>OrginazationName<? echo $strou; ?></Organization>',
'<ProductKey>',
'<Key><? echo $strin; ?>ProductKey1<? echo $strou; ?>-<? echo $strin; ?>ProductKey2<? echo $strou; ?>-<? echo $strin; ?>ProductKey3<? echo $strou; ?>-<? echo $strin; ?>ProductKey4<? echo $strou; ?>-<? echo $strin; ?>ProductKey5<? echo $strou; ?></Key>',
'</ProductKey>',
'</UserData>',
'<EnableFirewall><? echo $strin; ?>EnableFirewall<? echo $strou; ?></EnableFirewall>',
'</component>',
//Disk COnfiguration
'<component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<DiskConfiguration>',
'<Disk wcm:action="add">',
'<CreatePartitions>',
//System Reserved
'<CreatePartition wcm:action="add">',
'<Order>1</Order>',
'<Type>Primary</Type>',
'<Size>100</Size>',
'</CreatePartition>',
//OS partition
'<CreatePartition wcm:action="add">',
'<Extend>true</Extend>',
'<Order><? echo $strin; ?>PartitionOrder<? echo $strou; ?></Order>',
'<Type>Primary</Type>',
'</CreatePartition>',
'</CreatePartitions>',
'<ModifyPartitions>',
//Settings for system reserved partition
'<ModifyPartition wcm:action="add">',
'<Active>true</Active>',
'<Format>NTFS</Format>',
'<Label>System Reserved</Label>',
'<Order>1</Order>',
'<PartitionID>1</PartitionID>',
'<TypeID>0x27</TypeID>',
'</ModifyPartition>',
//Settings for OS partition
'<ModifyPartition wcm:action="add">',
'<Active>true</Active>',
'<Format><? echo $strin; ?>Format<? echo $strou; ?></Format>',
'<Label><? echo $strin; ?>Label<? echo $strou; ?></Label>',
'<Letter><? echo $strin; ?>DriveLetter<? echo $strou; ?></Letter>',
'<Order><? echo $strin; ?>PartitionOrder<? echo $strou; ?></Order>',
'<PartitionID><? echo $strin; ?>PartitionOrder<? echo $strou; ?></PartitionID>',
'</ModifyPartition>',
'</ModifyPartitions>',
'<DiskID><? echo $strin; ?>InstallDisk<? echo $strou; ?></DiskID>',
'<WillWipeDisk><? echo $strin; ?>WipeDisk<? echo $strou; ?></WillWipeDisk>',
'</Disk>',
'</DiskConfiguration>',
//Install OS to disk and partition
'<ImageInstall>',
'<OSImage>',
'<InstallTo>',
'<DiskID><? echo $strin; ?>InstallDisk<? echo $strou; ?></DiskID>',
'<PartitionID><? echo $strin; ?>PartitionOrder<? echo $strou; ?></PartitionID>',
'</InstallTo>',
'<InstallToAvailablePartition>false</InstallToAvailablePartition>',
'</OSImage>',
'</ImageInstall>',
//User Data
'<UserData>',
'<AcceptEula><? echo $strin; ?>AcceptEULA<? echo $strou; ?></AcceptEula>',
'<FullName><? echo $strin; ?>FullName<? echo $strou; ?></FullName>',
'<Organization><? echo $strin; ?>OrginazationName<? echo $strou; ?></Organization>',
'<ProductKey>',
'<Key><? echo $strin; ?>ProductKey1<? echo $strou; ?>-<? echo $strin; ?>ProductKey2<? echo $strou; ?>-<? echo $strin; ?>ProductKey3<? echo $strou; ?>-<? echo $strin; ?>ProductKey4<? echo $strou; ?>-<? echo $strin; ?>ProductKey5<? echo $strou; ?></Key>',
'</ProductKey>',
'</UserData>',
'<EnableFirewall><? echo $strin; ?>EnableFirewall<? echo $strou; ?></EnableFirewall>',
'</component>',
'</settings>',
//UAC
'<settings pass="offlineServicing">',
'<component name="Microsoft-Windows-LUA-Settings" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<EnableLUA><? echo $strin; ?>EnableUAC<? echo $strou; ?></EnableLUA>',
'</component>',
'</settings>',
'<settings pass="generalize">',
'<component name="Microsoft-Windows-Security-SPP" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SkipRearm><? echo $strin; ?>SkipRearm<? echo $strou; ?></SkipRearm>',
'</component>',
'</settings>',
//Specialize pass
'<settings pass="specialize">',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin; ?>InputLocale<? echo $strou; ?></InputLocale>',
'<SystemLocale><? echo $strin; ?>UILanguage<? echo $strou; ?></SystemLocale>',
'<UILanguage><? echo $strin; ?>UILanguage<? echo $strou; ?></UILanguage>',
'<UILanguageFallback><? echo $strin; ?>UILanguage<? echo $strou; ?></UILanguageFallback>',
'<UserLocale><? echo $strin; ?>UserLocale<? echo $strou; ?></UserLocale>',
'</component>',
//Join domain
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
//Skip auto activation
'<component name="Microsoft-Windows-Security-SPP-UX" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<SkipAutoActivation><? echo $strin; ?>SkipAutoActivation<? echo $strou; ?></SkipAutoActivation>',
'</component>',
//CEIP
'<component name="Microsoft-Windows-SQMApi" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<CEIPEnabled><? echo $strin; ?>CEIPEnabled<? echo $strou; ?></CEIPEnabled>',
'</component>',
//CEIP
'<component name="Microsoft-Windows-SQMApi" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<CEIPEnabled><? echo $strin; ?>CEIPEnabled<? echo $strou; ?></CEIPEnabled>',
'</component>',
//Computer name
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin; ?>ComputerName<? echo $strou; ?></ComputerName>',
'<ProductKey><? echo $strin; ?>ProductKey1<? echo $strou; ?>-<? echo $strin; ?>ProductKey2<? echo $strou; ?>-<? echo $strin; ?>ProductKey3<? echo $strou; ?>-<? echo $strin; ?>ProductKey4<? echo $strou; ?>-<? echo $strin; ?>ProductKey5<? echo $strou; ?></ProductKey>',
'<CopyProfile><? echo $strin;?>CopyProfile<? echo $strou;?></CopyProfile>',
'</component>',
//Computer name
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ComputerName><? echo $strin; ?>ComputerName<? echo $strou; ?></ComputerName>',
'<ProductKey><? echo $strin; ?>ProductKey1<? echo $strou; ?>-<? echo $strin; ?>ProductKey2<? echo $strou; ?>-<? echo $strin; ?>ProductKey3<? echo $strou; ?>-<? echo $strin; ?>ProductKey4<? echo $strou; ?>-<? echo $strin; ?>ProductKey5<? echo $strou; ?></ProductKey>',
'<CopyProfile><? echo $strin;?>CopyProfile<? echo $strou;?></CopyProfile>',
'</component>',
'<component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'<Extend><? echo $strin;?>ExtendOSPartition<? echo $strou;?></Extend>',
'</ExtendOSPartition>',
'<RunSynchronous>',
'<RunSynchronousCommand wcm:action="add">',
'<Path>net user Administrator /active:yes</Path>',
'<Order>1</Order>',
'</RunSynchronousCommand>',
'<RunSynchronousCommand wcm:action="add">',
'<Order>2</Order>',
'<Path>powershell.exe -executionpolicy bypass -File c:\\ProgramData\\SysPrep\\drivers\\install-driver-cert.ps1</Path>',
'</RunSynchronousCommand>',
'</RunSynchronous>',
'</component>',
'<component name="Microsoft-Windows-Deployment" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<ExtendOSPartition>',
'<Extend><? echo $strin;?>ExtendOSPartition<? echo $strou;?></Extend>',
'</ExtendOSPartition>',
'<RunSynchronous>',
'<RunSynchronousCommand wcm:action="add">',
'<Path>net user Administrator /active:yes</Path>',
'<Order>1</Order>',
'</RunSynchronousCommand>',
'<RunSynchronousCommand wcm:action="add">',
'<Order>2</Order>',
'<Path>powershell.exe -executionpolicy bypass -File c:\\Windows\\INF\\driverpack\\install-driver-cert.ps1</Path>',
'</RunSynchronousCommand>',
'</RunSynchronous>',
'</component>',
'</settings>',
'<settings pass="oobeSystem">',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin; ?>InputLocale<? echo $strou; ?></InputLocale>',
'<SystemLocale><? echo $strin; ?>UILanguage<? echo $strou; ?></SystemLocale>',
'<UILanguage><? echo $strin; ?>UILanguage<? echo $strou; ?></UILanguage>',
'<UserLocale><? echo $strin; ?>UserLocale<? echo $strou; ?></UserLocale>',
'</component>',
'<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<InputLocale><? echo $strin; ?>InputLocale<? echo $strou; ?></InputLocale>',
'<SystemLocale><? echo $strin; ?>UILanguage<? echo $strou; ?></SystemLocale>',
'<UILanguage><? echo $strin; ?>UILanguage<? echo $strou; ?></UILanguage>',
'<UserLocale><? echo $strin; ?>UserLocale<? echo $strou; ?></UserLocale>',
'</component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="x86" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
'<OOBE>',
//Hide EULA page
'<HideEULAPage><? echo $strin; ?>HideEULA<? echo $strou; ?></HideEULAPage>',
//Hide OEM registration
'<HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>',
//Hide Online account
'<HideOnlineAccountScreens>true</HideOnlineAccountScreens>',
//Hide wireless setup
'<HideWirelessSetupInOOBE><? echo $strin; ?>HideWireless<? echo $strou; ?></HideWirelessSetupInOOBE>',
'<ProtectYourPC><? echo $strin; ?>ProtectComputer<? echo $strou; ?></ProtectYourPC>',
'</OOBE>',
//User accounts
'<UserAccounts>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
//Password
'<Password>',
'<Value><? echo $strin; ?>Password<? echo $strou; ?></Value>',
'<PlainText>true</PlainText>',
'</Password>',
//Description
'<Description><? echo $strin; ?>Description<? echo $strou; ?></Description>',
//Display Name
'<DisplayName><? echo $strin; ?>FullName<? echo $strou; ?></DisplayName>',
//Group
'<Group><? echo $strin; ?>Group<? echo $strou; ?></Group>',
//Name
'<Name><? echo $strin; ?>FullName<? echo $strou; ?></Name>',
'</LocalAccount>',
'</LocalAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin;?>PasswordAdmin<? echo $strou;?></Value>',
'<PlainText>true</PlainText>',
'</AdministratorPassword>',
'</UserAccounts>',
//Registered Organization
'<RegisteredOrganization><? echo $strin; ?>OrginazationName<? echo $strou; ?></RegisteredOrganization>',
//Registered Owner
'<RegisteredOwner><? echo $strin; ?>FullName<? echo $strou; ?></RegisteredOwner>',
//Disable automatic daylight savings mode
'<DisableAutoDaylightTimeSet><? echo $strin; ?>DaylightSettings<? echo $strou; ?><\/DisableAutoDaylightTimeSet>',
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<Description>Control Panel View</Description>',
'<Order>1</Order>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v StartupPage /t REG_DWORD /d <? echo $strin; ?>ControlPanelView<? echo $strou; ?> /f</CommandLine>',
'<RequiresUserInput>true</RequiresUserInput>',
'</SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Order>2</Order>',
'<Description>Control Panel Icon Size</Description>',
'<RequiresUserInput>false</RequiresUserInput>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v AllItemsIconView /t REG_DWORD /d <? echo $strin; ?>ControlPanelIconSize<? echo $strou; ?> /f</CommandLine>',
'</SynchronousCommand>',
'<\/FirstLogonCommands>',
//Timezone settings
'<TimeZone><? echo $strin; ?>TimeZone<? echo $strou; ?><\/TimeZone>',
'</component>',
'<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
//OOBE settings
'<OOBE>',
//Hide EULA page
'<HideEULAPage><? echo $strin; ?>HideEULA<? echo $strou; ?></HideEULAPage>',
//Hide OEM registration
'<HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>',
//Hide Online account
'<HideOnlineAccountScreens>true</HideOnlineAccountScreens>',
//Hide wireless setup
'<HideWirelessSetupInOOBE><? echo $strin; ?>HideWireless<? echo $strou; ?></HideWirelessSetupInOOBE>',
'<ProtectYourPC><? echo $strin; ?>ProtectComputer<? echo $strou; ?></ProtectYourPC>',
'</OOBE>',
//User accounts
'<UserAccounts>',
'<LocalAccounts>',
'<LocalAccount wcm:action="add">',
//Password
'<Password>',
'<Value><? echo $strin; ?>Password<? echo $strou; ?></Value>',
'<PlainText>true</PlainText>',
'</Password>',
//Description
'<Description><? echo $strin; ?>Description<? echo $strou; ?></Description>',
//Display Name
'<DisplayName><? echo $strin; ?>FullName<? echo $strou; ?></DisplayName>',
//Group
'<Group><? echo $strin; ?>Group<? echo $strou; ?></Group>',
//Name
'<Name><? echo $strin; ?>FullName<? echo $strou; ?></Name>',
'</LocalAccount>',
'</LocalAccounts>',
'<AdministratorPassword>',
'<Value><? echo $strin;?>PasswordAdmin<? echo $strou;?></Value>',
'<PlainText>true</PlainText>',
'</AdministratorPassword>',
'</UserAccounts>',
//Registered Organization
'<RegisteredOrganization><? echo $strin; ?>OrginazationName<? echo $strou; ?></RegisteredOrganization>',
//Registered Owner
'<RegisteredOwner><? echo $strin; ?>FullName<? echo $strou; ?></RegisteredOwner>',
//Disable automatic daylight savings mode
'<DisableAutoDaylightTimeSet><? echo $strin; ?>DaylightSettings<? echo $strou; ?><\/DisableAutoDaylightTimeSet>',
'<FirstLogonCommands>',
'<SynchronousCommand wcm:action="add">',
'<Description>Control Panel View</Description>',
'<Order>1</Order>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v StartupPage /t REG_DWORD /d 1<? echo $strin; ?>ControlPanelView<? echo $strou; ?> /f</CommandLine>',
'<RequiresUserInput>true</RequiresUserInput>',
'</SynchronousCommand>',
'<SynchronousCommand wcm:action="add">',
'<Order>2</Order>',
'<Description>Control Panel Icon Size</Description>',
'<RequiresUserInput>false</RequiresUserInput>',
'<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v AllItemsIconView /t REG_DWORD /d <? echo $strin; ?>ControlPanelIconSize<? echo $strou; ?> /f</CommandLine>',
'</SynchronousCommand>',
'<\/FirstLogonCommands>',
//Timezone settings
'<TimeZone><? echo $strin; ?>TimeZone<? echo $strou; ?><\/TimeZone>',
'</component>',
'</settings>',
'<cpi:offlineImage cpi:source="wim:c:/users/1781181/desktop/install.wim#Windows 10 Pro" xmlns:cpi="urn:schemas-microsoft-com:cpi" />',
'</unattend>',
].join('\r\n');

</script>
<?php
require("../../../includes/config.inc.php");
require("../../../includes/i18n.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/PageGenerator.php");
require("../includes/data_Windows_Answer_File_Generator.inc.php");
require("../includes/class_form.php");
?>
<?php

if(isset($_SESSION['parameters']))
{
	$parameters = $_SESSION['parameters'];
}
    $f = new ValidatingForm();
    $f->add(new HiddenTpl("codeToCopy"), array("value" => "", "hide" => True));


//==== NEW SECTION ====
// Installation Notes
//=====================
$f->add(new TitleElement(_T("Installation Notes", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Installation_Notes',$InfoBule_Installation_Notes)));
$f->push(new Table());

	//_____________
    $f->add(
        new TrFormElement(_T('Title','imaging'), new InputTplTitle('Location',"name file xml")),
        array("required" => True,'value'=>(isset($parameters)) ? $parameters['Title'] : '')
    );
    //_____________
    $f->add(new TrFormElement("Notes".":", new OptTextareaTpl(array('name'=>'Comments','value'=>(isset($parameters)) ? $parameters['Notes'] : _T('Enter your comments here...','imaging')))));

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// Os Settings
//=====================
$f->add(new TitleElement(_T("Os Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('General_Settings',$InfoBule_General_Settings)));
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
        (isset($parameters)) ? $parameters['ProductKey1'] : "W269N","",
        (isset($parameters)) ? $parameters['ProductKey2'] : "WFGWX","",
        (isset($parameters)) ? $parameters['ProductKey3'] : "YVC9B","",
        (isset($parameters)) ? $parameters['ProductKey4'] : "4J6C9","",
        (isset($parameters)) ? $parameters['ProductKey5'] : "T83GX"
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Product Key','imaging').":", new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Organization Name','imaging').":", new InputTplTitle('OrginazationName',$InfoBule_OrginazationName)),
        array('value' => (isset($parameters)) ? $parameters['OrginazationName'] :'Siveo', "required" => True)
    );
    //_____________
    $EULA = new SelectItemtitle("AcceptEULA",$InfoBule_AcceptEULA);
    $EULA->setElements($yes_no);
    $EULA->setElementsVal(array('true', 'false'));
    $f->add(
        new TrFormElement(_T('Accept EULA','imaging').":", $EULA),
        array("value" => (isset($parameters)) ? $parameters['AcceptEULA'] : "true","required" => True)
    );
    //_____________
    $Skipactivation = new SelectItemtitle("SkipAutoActivation",$InfoBule_SkipAutoActivation);
    $Skipactivation->setElements($yes_no);
    $Skipactivation->setElementsVal(array('true', 'false'));
    $f->add(
        new TrFormElement(_T('Skip automatic activation','imaging').":", $Skipactivation),
        array("value" => (isset($parameters)) ? $parameters['SkipAutoActivation'] : "true","required" => True)
    );
    //_____________
    $SkipLicense = new SelectItemtitle("SkipRearm",$InfoBule_SkipRearm);
    $SkipLicense->setElements($yes_no);
    $SkipLicense->setElementsVal(array('1', '0'));
    $f->add(
        new TrFormElement(_T('Skip License Rearm','imaging').":", $SkipLicense),
        array("value" => (isset($parameters)) ? $parameters['SkipRearm'] : "1","required" => True)
    );
    //_____________
    $SetupUILanguage = new SelectItemtitle("SetupUILanguage",$InfoBule_SetupUILanguage);
    $SetupUILanguage->setElements($eleUILanguage);
    $SetupUILanguage->setElementsVal($valUILanguage);
     //_____________
    $f->add(
        new TrFormElement(_T('Setup Language','imaging').":", $SetupUILanguage),
        array("value" => (isset($parameters)) ? $parameters['SetupUILanguage'] :"fr-FR","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement(_T('Computer Name','imaging').":", new InputTplTitle('ComputerName',$Infobule_ComputerName)),
        array("required" => True,"value" =>(isset($parameters)) ? $parameters['ComputerName'] :'windows10-PC')
    );
    //_____________
    $InputLocale = new SelectItemtitle("InputLocale",$Infobule_InputLocale);
    $InputLocale->setElements($elementInputarray);
    $InputLocale->setElementsVal($valeurInputarray);
    $f->add(
        new TrFormElement(_T('Keyboard or input method','imaging').":", $InputLocale),
        array("value" => (isset($parameters)) ? $parameters['InputLocale'] :'1036:0000040c',"required" => True)
    );
    //_____________
    $UserLocale = new SelectItemtitle("UserLocale",$InfoBule_UserLocale);
    $UserLocale->setElements($eleUILanguage);
    $UserLocale->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('Currency and Date format','imaging').":", $UserLocale),
        array("value" =>(isset($parameters)) ? $parameters['UserLocale'] :"fr-FR","required" => True)
    );
    //_____________
    $TimeZone = new SelectItemtitle("TimeZone",$InfoBule_TimeZone);
    $TimeZone->setElements($element_timezone);
    $TimeZone->setElementsVal($val_timezone);
    $f->add(
        new TrFormElement(_T('Time Zone','imaging').":", $TimeZone),
        array("value" =>  (isset($parameters)) ? $parameters['TimeZone'] :"Romance Standard Time","required" => True)
    );
    //_____________
    $UILanguage = new SelectItemtitle("UILanguage",$InfoBule_UILanguage);
    $UILanguage->setElements($eleUILanguage);
    $UILanguage->setElementsVal($valUILanguage);
    $f->add(
        new TrFormElement(_T('UI Language','imaging').":", $UILanguage),
        array("value" => (isset($parameters)) ? $parameters['UILanguage'] :'fr-FR' ,"required" => True)
    );

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// Partition Settings
//=====================
$f->add(new TitleElement(_T("Partition Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Partition_Settings',$Infobule_Partition_Settings)));
$f->push(new Table());

    //_____________
    $WipeDisk = new SelectItemtitle("WipeDisk",$InfoBule_WipeDisk);
    $WipeDisk->setElements($yes_no);
    $WipeDisk->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Wipe Disk','imaging').":", $WipeDisk),
        array("value" => (isset($parameters)) ? $parameters['WipeDisk'] : "false","required" => True)
    );
    //_____________
    $InstallDisk = new SelectItemtitle("InstallDisk",$InfoBule_InstallDisk);
    $InstallDisk->setElements($suite0_5);
    $InstallDisk->setElementsVal($suite0_5);
    $f->add(
        new TrFormElement(_T('Install to disk','imaging').":", $InstallDisk),
        array("value" => (isset($parameters)) ? $parameters['InstallDisk'] : "0","required" => True)
    );
    //_____________
    $PartitionOrder = new SelectItemtitle("PartitionOrder",$InfoBule_PartitionOrder);
    $PartitionOrder->setElements($suite2_5);
    $PartitionOrder->setElementsVal($suite2_5);
    $f->add(
        new TrFormElement(_T('Partition Order','imaging').":", $PartitionOrder),
        array("value" => (isset($parameters)) ? $parameters['PartitionOrder'] : "2","required" => True)
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
    $Format = new SelectItemtitle("Format",$InfoBule_Format);
    $Format->setElements(array('NTFS','FAT32'));
    $Format->setElementsVal(array('NTFS','FAT32'));
    $f->add(
        new TrFormElement(_T('Main Partition Format','imaging').":", $Format),
        array("value" => (isset($parameters)) ? $parameters['Format'] : "NTFS","required" => True)
    );
    //_____________
    $f->add(
        new TrFormElement($InfoBule_Label, new InputTplTitle('Label',$InfoBule_Label)),
        array("required" => True,'value' => (isset($parameters)) ? $parameters['Label'] : 'OS')
    );
    //_____________
    $DriveLetter = new SelectItemtitle("DriveLetter",$InfoBule_DriveLetter);
    $DriveLetter->setElements($DriveLetterTabElement);
    $DriveLetter->setElementsVal($DriveLetterTabElement);
    $f->add(
        new TrFormElement(_T('Main Partition Letter','imaging').":", $DriveLetter),
        array("value" => (isset($parameters)) ? $parameters['DriveLetter'] : "C","required" => True)
    );

$f->pop();
$f->add(new SepTpl());


//==== NEW SECTION ====
// Security Settings
//=====================
$f->add(new TitleElement(_T("Security Settings", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Out_Of_Box_Experience',$InfoBule_Out_Of_Box_Experience)));
$f->push(new Table());

    //_____________
    $ProtectComputer = new SelectItemtitle("ProtectComputer",$InfoBule_ProtectComputer);
    $ProtectComputer->setElements($ProtectComputerTabElement);
    $ProtectComputer->setElementsVal(array('1','2','3'));
    $f->add(
        new TrFormElement(_T('Protect Your Computer','imaging').":", $ProtectComputer),
        array("value" => (isset($parameters)) ? $parameters['ProtectComputer'] : "1","required" => True)
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
    $NetworkLocation = new SelectItemtitle("NetworkLocation",$InfoBule_NetworkLocation );
    $NetworkLocation->setElements(array('Home','Work','Other'));
    $NetworkLocation->setElementsVal(array('Home','Work','Other'));
    $f->add(
        new TrFormElement(_T('Network Location','imaging').":", $NetworkLocation),
        array("value" => (isset($parameters)) ? $parameters['NetworkLocation'] :"Work","required" => True)
    );
    //_____________
    $HideEULA = new SelectItemtitle("HideEULA",$InfoBule_HideEULA);
    $HideEULA->setElements($yes_no);
    $HideEULA->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Hide EULA page','imaging').":", $HideEULA),
        array("value" => (isset($parameters)) ? $parameters['HideEULA'] : "true","required" => True)
    );
    //_____________
    $EnableFirewall = new SelectItemtitle("EnableFirewall",$InfoBule_EnableFirewall);
    $EnableFirewall->setElements($EnableDisabled);
    $EnableFirewall->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Enable Firewall','imaging').":", $EnableFirewall),
        array("value" => (isset($parameters)) ? $parameters['EnableFirewall'] : "true","required" => True)
    );
    //_____________
    $DaylightSettings = new SelectItemtitle("DaylightSettings",$InfoBule_DaylightSettings);
    $DaylightSettings->setElements($yes_no);
    $DaylightSettings->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Disable auto daylight timeset','imaging').":", $DaylightSettings),
        array("value" => (isset($parameters)) ? $parameters['DaylightSettings'] : "true","required" => True)
    );
    //_____________
    $HideWireless = new SelectItemtitle("HideWireless",$Infobule_HideWireless);
    $HideWireless->setElements($yes_no);
    $HideWireless->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Hide wireless setup in OOBE','imaging').":", $HideWireless),
        array("value" => (isset($parameters)) ? $parameters['HideWireless'] : "true","required" => True)
    );
    //_____________
    $ControlPanelView = new SelectItemtitle("ControlPanelView",$InfoBule_ControlPanelView);
    $ControlPanelView->setElements(array(_T('Category View', "imaging"),_T('Classic View', "imaging")));
    $ControlPanelView->setElementsVal(array('0','1'));
    $f->add(
        new TrFormElement(_T('Control Panel View','imaging').":", $ControlPanelView),
        array("value" => (isset($parameters)) ? $parameters['ControlPanelView'] : "1","required" => True)
    );
    //_____________
    $ControlPanelIconSize = new SelectItemtitle("ControlPanelIconSize",$InfoBule_ControlPanelIconSize);
    $ControlPanelIconSize->setElements(array(_T('Large', "imaging"),_T('Small', "imaging")));
    $ControlPanelIconSize->setElementsVal(array('0','1'));
    $f->add(
        new TrFormElement(_T('Control Panel Icon Size','imaging').":", $ControlPanelIconSize),
        array("value" => (isset($parameters)) ? $parameters['ControlPanelIconSize'] : "0","required" => True)
    );

$f->pop();
$f->add( new SepTpl());

//==== NEW SECTION ====
// Domain Settings
//=====================
$f->add(new TitleElement(_T("Domain Settings","imaging")));
$f->push(new Table());

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
// User Account
//=====================
$f->add(new TitleElement(_T("User Account", "imaging")));
$f->add(new TrFormElement("", new Iconereply('User_Account', $InfoBule_User_Account )));
$f->push(new Table());

    //_____________
    $CEIPEnabled = new SelectItemtitle("CEIPEnabled",$InfoBule_CEIPEnabled);
    $CEIPEnabled->setElements($EnableDisabled);
    $CEIPEnabled->setElementsVal(array('1','0'));
    $f->add(
        new TrFormElement(_T('Customer Experience Improvement Program (CEIP)','imaging').":", $CEIPEnabled),
            array("value" => (isset($parameters)) ? $parameters['CEIPEnabled'] : "0","required" => True)
    );
    //_____________
    $CopyProfile = new SelectItemtitle("CopyProfile", $InfoBule_CopyProfile);
    $CopyProfile->setElements($yes_no);
    $CopyProfile->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('Copy Profile','imaging').":", $CopyProfile),
        array("value" => (isset($parameters)) ? $parameters['CopyProfile'] : "true","required" => True)
    );
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
    //_____________
    $EnableUAC = new SelectItemtitle("EnableUAC",$InfoBule_EnableUAC);
    $EnableUAC->setElements($EnableDisabled);
    $EnableUAC->setElementsVal($truefalse);
    $f->add(
        new TrFormElement(_T('UAC','imaging').":", $EnableUAC),
            array("value" => (isset($parameters)) ? $parameters['EnableUAC'] : "false","required" => True)
    );

    //=============
    $bo = new buttonTpl('bvalid', _T("Validate",'imaging'),'btnPrimary',_T("Create Xml Windows Answer File Generator", "imaging"));
    $rr = new TrFormElementcollapse($bo);
    $rr->setstyle("text-align: center;");
    $f->add(
            $rr
    );
    $f->add(
        new TrFormElement("",   new multifieldTpl(
                array(  new SpanElementtitle(_T("Xml Windows Answer File Generator", "imaging"),Null, $InfoBule_showxml),
                    new Iconereply('awfg_show',$InfoBule_showxml)
                )
            )
        )
    );
    $f->pop();

$f->pop();
$f->display();

echo "<pre id='codeTocopy2' style='width:100%;'></pre>";
?>
