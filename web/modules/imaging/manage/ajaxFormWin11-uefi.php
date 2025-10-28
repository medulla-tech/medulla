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
'<?php echo $strin; ?>xml version="1.0" encoding="utf-8"<?php echo $strou; ?>',
'<unattend xmlns="urn:schemas-microsoft-com:unattend">',
'<!--',
'________________________________',
'OS Windows 11 [amd64 uefi]',
'Windows Answer File Generator :',
'',
'date : <?php echo $strin; ?>dateval<?php echo $strou; ?>',
'',
'Installation Notes',
'Location: <?php echo $strin; ?>Location<?php echo $strou; ?>',
'Notes: <?php echo $strin; ?>Comments<?php echo $strou; ?>',
'list parameters : @@listParameters@@',
'________________________________',
'-->',
'',
'',
//Language Setup
    '<settings pass="offlineServicing"></settings>',
    '<settings pass="windowsPE">',
        '<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<SetupUILanguage>',
                '<UILanguage><?php echo $strin; ?>SetupUILanguage<?php echo $strou; ?></UILanguage>',
            '</SetupUILanguage>',
            '<InputLocale><?php echo $strin; ?>InputLocale<?php echo $strou; ?></InputLocale>',
            '<SystemLocale><?php echo $strin; ?>SetupUILanguage<?php echo $strou; ?></SystemLocale>',
            '<UILanguage><?php echo $strin; ?>SetupUILanguage<?php echo $strou; ?></UILanguage>',
            '<UILanguageFallback><?php echo $strin; ?>SetupUILanguage<?php echo $strou; ?></UILanguageFallback>',
            '<UserLocale><?php echo $strin; ?>UserLocale<?php echo $strou; ?></UserLocale>',
        '</component>',
        '',
        '',
        //Disk COnfiguration
        '<component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">',
            '<ImageInstall>',
                '<OSImage>',
                    '<InstallTo>',
                        '<DiskID>0</DiskID>',
                        '<PartitionID>3</PartitionID>',
                    '</InstallTo>',
                '</OSImage>',
            '</ImageInstall>',
            //User Data
            '<UserData>',
                '<AcceptEula><?php echo $strin; ?>AcceptEULA<?php echo $strou; ?></AcceptEula>',
                '<FullName><?php echo $strin; ?>FullName<?php echo $strou; ?></FullName>',
                '<Organization><?php echo $strin; ?>OrginazationName<?php echo $strou; ?></Organization>',
                '<ProductKey>',
                    '<Key><?php echo $strin; ?>ProductKey1<?php echo $strou; ?>-<?php echo $strin; ?>ProductKey2<?php echo $strou; ?>-<?php echo $strin; ?>ProductKey3<?php echo $strou; ?>-<?php echo $strin; ?>ProductKey4<?php echo $strou; ?>-<?php echo $strin; ?>ProductKey5<?php echo $strou; ?></Key>',
                    '<WillShowUI>OnError</WillShowUI>',
                '</ProductKey>',
            '</UserData>',
            '<EnableFirewall><?php echo $strin; ?>EnableFirewall<?php echo $strou; ?></EnableFirewall>',
            '<UseConfigurationSet>false</UseConfigurationSet>',
            '<RunSynchronous>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>1</Order>',
                    '<Path>cmd.exe /c ">>"X:\\diskpart.txt" (echo SELECT DISK=0&amp;echo CLEAN&amp;echo CONVERT GPT&amp;echo CREATE PARTITION EFI SIZE=300&amp;echo FORMAT QUICK FS=FAT32 LABEL="System"&amp;echo CREATE PARTITION MSR SIZE=16)"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>2</Order>',
                    '<Path>cmd.exe /c ">>"X:\\diskpart.txt" (echo CREATE PARTITION PRIMARY&amp;echo SHRINK MINIMUM=1000&amp;echo FORMAT QUICK FS=NTFS LABEL="Windows"&amp;echo CREATE PARTITION PRIMARY&amp;echo FORMAT QUICK FS=NTFS LABEL="Recovery")"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>3</Order>',
                    '<Path>cmd.exe /c ">>"X:\\diskpart.txt" (echo SET ID="de94bba4-06d1-4d40-a16a-bfd50179d6ac"&amp;echo GPT ATTRIBUTES=0x8000000000000001)"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>4</Order>',
                    '<Path>cmd.exe /c "diskpart.exe /s "X:\\diskpart.txt" >>"X:\\diskpart.log" || ( type "X:\\diskpart.log" &amp; echo diskpart encountered an error. &amp; pause &amp; exit /b 1 )"</Path>',
                '</RunSynchronousCommand>',
            '</RunSynchronous>',
        '</component>',
    '</settings>',
    '',
    '',
    //UAC
    '<settings pass="offlineServicing">',
        '<component name="Microsoft-Windows-LUA-Settings" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<EnableLUA><?php echo $strin; ?>EnableUAC<?php echo $strou; ?></EnableLUA>',
        '</component>',
    '</settings>',
    '<settings pass="generalize">',
        '<component name="Microsoft-Windows-Security-SPP" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<SkipRearm><?php echo $strin; ?>SkipRearm<?php echo $strou; ?></SkipRearm>',
        '</component>',
    '</settings>',
    '',
    '',
    //Specialize pass
    '<settings pass="specialize">',
        '<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<InputLocale><?php echo $strin; ?>InputLocale<?php echo $strou; ?></InputLocale>',
            '<SystemLocale><?php echo $strin; ?>UILanguage<?php echo $strou; ?></SystemLocale>',
            '<UILanguage><?php echo $strin; ?>UILanguage<?php echo $strou; ?></UILanguage>',
            '<UILanguageFallback><?php echo $strin; ?>UILanguage<?php echo $strou; ?></UILanguageFallback>',
            '<UserLocale><?php echo $strin; ?>UserLocale<?php echo $strou; ?></UserLocale>',
        '</component>',
        //Join domain
        '<component name="Microsoft-Windows-UnattendedJoin" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<Identification>',
                '<Credentials>',
                    '<Domain><?php echo $strin; ?>Domain<?php echo $strou; ?></Domain>',
                    '<Password><?php echo $strin; ?>DomainPassword<?php echo $strou; ?></Password>',
                    '<Username><?php echo $strin; ?>DomainUser<?php echo $strou; ?></Username>',
                '</Credentials>',
                '<JoinDomain><?php echo $strin; ?>JoinDomain<?php echo $strou; ?></JoinDomain>',
                '<MachineObjectOU><?php echo $strin; ?>MachineObjectOU<?php echo $strou; ?></MachineObjectOU>',
            '</Identification>',
        '</component>',
        //Skip auto activation
        '<component name="Microsoft-Windows-Security-SPP-UX" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<SkipAutoActivation><?php echo $strin; ?>SkipAutoActivation<?php echo $strou; ?></SkipAutoActivation>',
        '</component>',
        //CEIP
        '<component name="Microsoft-Windows-SQMApi" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<CEIPEnabled><?php echo $strin; ?>CEIPEnabled<?php echo $strou; ?></CEIPEnabled>',
        '</component>',
        //Computer name
        '<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<ComputerName><?php echo $strin; ?>ComputerName<?php echo $strou; ?></ComputerName>',
            '<CopyProfile><?php echo $strin;?>CopyProfile<?php echo $strou;?></CopyProfile>',
        '</component>',
        '<component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<ExtendOSPartition>',
                '<Extend><?php echo $strin;?>ExtendOSPartition<?php echo $strou;?></Extend>',
            '</ExtendOSPartition>',
            '<RunSynchronous>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>1</Order>',
                    '<Path>powershell.exe -WindowStyle Normal -NoProfile -Command "$xml = [xml]::new(); $xml.Load(\'C:\\Windows\\Panther\\unattend.xml\'); $sb = [scriptblock]::Create( $xml.unattend.Extensions.ExtractScript ); Invoke-Command -ScriptBlock $sb -ArgumentList $xml;"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>2</Order>',
                    '<Path>powershell.exe -WindowStyle Normal -NoProfile -Command "Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\Specialize.ps1\' -Raw | Invoke-Expression;"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>3</Order>',
                    '<Path>reg.exe load "HKU\\DefaultUser" "C:\\Users\\Default\\NTUSER.DAT"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>4</Order>',
                    '<Path>powershell.exe -WindowStyle Normal -NoProfile -Command "Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\DefaultUser.ps1\' -Raw | Invoke-Expression;"</Path>',
                '</RunSynchronousCommand>',
                '<RunSynchronousCommand wcm:action="add">',
                    '<Order>5</Order>',
                    '<Path>reg.exe unload "HKU\\DefaultUser"</Path>',
                '</RunSynchronousCommand>',
            '</RunSynchronous>',
        '</component>',
    '</settings>',
    '',
    '',
    // OOBE system
    '<settings pass="oobeSystem">',
        '<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            '<InputLocale><?php echo $strin; ?>InputLocale<?php echo $strou; ?></InputLocale>',
            '<SystemLocale><?php echo $strin; ?>UILanguage<?php echo $strou; ?></SystemLocale>',
            '<UILanguage><?php echo $strin; ?>UILanguage<?php echo $strou; ?></UILanguage>',
            '<UserLocale><?php echo $strin; ?>UserLocale<?php echo $strou; ?></UserLocale>',
        '</component>',
        '<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
            //OOBE settings
            '<OOBE>',
                //Hide EULA page
                '<HideEULAPage><?php echo $strin; ?>HideEULA<?php echo $strou; ?></HideEULAPage>',
                //Hide OEM registration
                '<HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>',
                //Hide Online account
                '<HideOnlineAccountScreens>true</HideOnlineAccountScreens>',
                //Hide wireless setup
                '<HideWirelessSetupInOOBE><?php echo $strin; ?>HideWireless<?php echo $strou; ?></HideWirelessSetupInOOBE>',
                '<ProtectYourPC><?php echo $strin; ?>ProtectComputer<?php echo $strou; ?></ProtectYourPC>',
            '</OOBE>',
            //User accounts
            '<UserAccounts>',
                '<LocalAccounts>',
                    '<LocalAccount wcm:action="add">',
                        //Password
                        '<Password>',
                            '<Value><?php echo $strin; ?>Password<?php echo $strou; ?></Value>',
                            '<PlainText>true</PlainText>',
                        '</Password>',
                        //Description
                        '<Description><?php echo $strin; ?>Description<?php echo $strou; ?></Description>',
                        //Display Name
                        '<DisplayName><?php echo $strin; ?>FullName<?php echo $strou; ?></DisplayName>',
                        //Group
                        '<Group><?php echo $strin; ?>Group<?php echo $strou; ?></Group>',
                        //Name
                        '<Name><?php echo $strin; ?>FullName<?php echo $strou; ?></Name>',
                    '</LocalAccount>',
                '</LocalAccounts>',
                '<AdministratorPassword>',
                    '<Value><?php echo $strin;?>PasswordAdmin<?php echo $strou;?></Value>',
                    '<PlainText>true</PlainText>',
                '</AdministratorPassword>',
            '</UserAccounts>',
            //Registered Organization
            '<RegisteredOrganization><?php echo $strin; ?>OrginazationName<?php echo $strou; ?></RegisteredOrganization>',
            //Registered Owner
            '<RegisteredOwner><?php echo $strin; ?>FullName<?php echo $strou; ?></RegisteredOwner>',
            //Disable automatic daylight savings mode
            '<DisableAutoDaylightTimeSet><?php echo $strin; ?>DaylightSettings<?php echo $strou; ?></DisableAutoDaylightTimeSet>',
            '<FirstLogonCommands>',
                '<SynchronousCommand wcm:action="add">',
                    '<Description>Control Panel View</Description>',
                    '<Order>1</Order>',
                    '<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v StartupPage /t REG_DWORD /d 1<?php echo $strin; ?>ControlPanelView<?php echo $strou; ?> /f</CommandLine>',
                    '<RequiresUserInput>true</RequiresUserInput>',
                '</SynchronousCommand>',
                '<SynchronousCommand wcm:action="add">',
                    '<Order>2</Order>',
                    '<Description>Control Panel Icon Size</Description>',
                    '<RequiresUserInput>false</RequiresUserInput>',
                    '<CommandLine>reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ControlPanel" /v AllItemsIconView /t REG_DWORD /d <?php echo $strin; ?>ControlPanelIconSize<?php echo $strou; ?> /f</CommandLine>',
                '</SynchronousCommand>',
            '</FirstLogonCommands>',
            //Timezone settings
            '<TimeZone><?php echo $strin; ?>TimeZone<?php echo $strou; ?></TimeZone>',
        '</component>',
    '</settings>',
    '<Extensions xmlns="https://schneegans.de/windows/unattend-generator/">',
        '<ExtractScript>',
'param(',
    '[xml] $Document',
');',
'foreach( $file in $Document.unattend.Extensions.File ) {',
'$path = [System.Environment]::ExpandEnvironmentVariables( $file.GetAttribute( \'path\' ) );',
'mkdir -Path( $path | Split-Path -Parent ) -ErrorAction \'SilentlyContinue\';',
'$encoding = switch( [System.IO.Path]::GetExtension( $path ) ) {',
'{ $_ -in \'.ps1\', \'.xml\' } { [System.Text.Encoding]::UTF8; }',
'{ $_ -in \'.reg\', \'.vbs\', \'.js\' } { [System.Text.UnicodeEncoding]::new( $false, $true ); }',
'default { [System.Text.Encoding]::Default; }',
'};',
'$bytes = $encoding.GetPreamble() + $encoding.GetBytes( $file.InnerText.Trim() );',
'[System.IO.File]::WriteAllBytes( $path, $bytes );',
'}',
        '</ExtractScript>',
        // Bloat remove packages
        '<File path="C:\\Windows\\Setup\\Scripts\\RemovePackages.ps1">',
'$selectors = @(',
'<?php echo $strin;?>BloatsRemovePackages<?php echo $strou;?>',
');',
'$getCommand = {',
'Get-AppxProvisionedPackage -Online;',
'};',
'$filterCommand = {',
'$_.DisplayName -eq $selector;',
'};',
'$removeCommand = {',
'[CmdletBinding()]',
'param(',
'[Parameter( Mandatory, ValueFromPipeline )]',
'$InputObject',
');',
'process {',
'$InputObject | Remove-AppxProvisionedPackage -AllUsers -Online -ErrorAction \'Continue\';',
'}',
'};',
'$type = \'Package\';',
'$logfile = \'C:\\Windows\\Setup\\Scripts\\RemovePackages.log\';',
'&amp; {',
'$installed = &amp; $getCommand;',
'foreach( $selector in $selectors ) {',
'$result = [ordered] @{',
'Selector = $selector;',
'};',
'$found = $installed | Where-Object -FilterScript $filterCommand;',
'if( $found ) {',
'$result.Output = $found | &amp; $removeCommand;',
'if( $? ) {',
'    $result.Message = "$type removed.";',
'} else {',
'    $result.Message = "$type not removed.";',
'    $result.Error = $Error[0];',
'}',
'} else {',
'$result.Message = "$type not installed.";',
'}',
'$result | ConvertTo-Json -Depth 3 -Compress;',
'}',
'} *>&amp;1 >> $logfile;',
    '</File>',

    // Bloat remove capabilities
    '<File path="C:\\Windows\\Setup\\Scripts\\RemoveCapabilities.ps1">',
'$selectors = @(',
'<?php echo $strin;?>BloatsRemoveCapabilities<?php echo $strou;?>',
');',
'$getCommand = {',
'Get-WindowsCapability -Online | Where-Object -Property \'State\' -NotIn -Value @(',
'\'NotPresent\';',
'\'Removed\';',
');',
'};',
'$filterCommand = {',
'($_.Name -split \'~\')[0] -eq $selector;',
'};',
'$removeCommand = {',
'[CmdletBinding()]',
'param(',
'[Parameter( Mandatory, ValueFromPipeline )]',
'$InputObject',
');',
'process {',
'$InputObject | Remove-WindowsCapability -Online -ErrorAction \'Continue\';',
'}',
'};',
'$type = \'Capability\';',
'$logfile = \'C:\\Windows\\Setup\\Scripts\\RemoveCapabilities.log\';',
'&amp; {',
'$installed = &amp; $getCommand;',
'foreach( $selector in $selectors ) {',
'$result = [ordered] @{',
'Selector = $selector;',
'};',
'$found = $installed | Where-Object -FilterScript $filterCommand;',
'if( $found ) {',
'$result.Output = $found | &amp; $removeCommand;',
'if( $? ) {',
'$result.Message = "$type removed.";',
'} else {',
'$result.Message = "$type not removed.";',
'$result.Error = $Error[0];',
'}',
'} else {',
'$result.Message = "$type not installed.";',
'}',
'$result | ConvertTo-Json -Depth 3 -Compress;',
'}',
'} *>&amp;1 >> $logfile;',
'</File>',
// Bloats remove features
'<File path="C:\\Windows\\Setup\\Scripts\\RemoveFeatures.ps1">',
'$selectors = @(',
'<?php echo $strin;?>BloatsRemoveFeatures<?php echo $strou;?>',
');',
'$getCommand = {',
'Get-WindowsOptionalFeature -Online | Where-Object -Property \'State\' -NotIn -Value @(',
'\'Disabled\';',
'\'DisabledWithPayloadRemoved\';',
');',
'};',
'$filterCommand = {',
'$_.FeatureName -eq $selector;',
'};',
'$removeCommand = {',
'[CmdletBinding()]',
'param(',
'[Parameter( Mandatory, ValueFromPipeline )]',
'$InputObject',
');',
'process {',
'$InputObject | Disable-WindowsOptionalFeature -Online -Remove -NoRestart -ErrorAction \'Continue\';',
'}',
'};',
'$type = \'Feature\';',
'$logfile = \'C:\\Windows\\Setup\\Scripts\\RemoveFeatures.log\';',
'&amp; {',
'$installed = &amp; $getCommand;',
'foreach( $selector in $selectors ) {',
'$result = [ordered] @{',
'Selector = $selector;',
'};',
'$found = $installed | Where-Object -FilterScript $filterCommand;',
'if( $found ) {',
'$result.Output = $found | &amp; $removeCommand;',
'if( $? ) {',
'$result.Message = "$type removed.";',
'} else {',
'$result.Message = "$type not removed.";',
'$result.Error = $Error[0];',
'}',
'} else {',
'$result.Message = "$type not installed.";',
'}',
'$result | ConvertTo-Json -Depth 3 -Compress;',
'}',
'} *>&amp;1 >> $logfile;',
'</File>',

'<File path="C:\\Windows\\Setup\\Scripts\\PauseWindowsUpdate.ps1">',
'$formatter = {',
'$args[0].ToString( "yyyy\'-\'MM\'-\'dd\'T\'HH\':\'mm\':\'ssK" );',
'};',
'$now = [datetime]::UtcNow;',
'$start = &amp; $formatter $now;',
'$end = &amp; $formatter $now.AddDays( 7 );',
'',
'$params = @{',
'LiteralPath = \'Registry::HKLM\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings\';',
'Type = \'String\';',
'Force = $true;',
'};',
'',
'Set-ItemProperty @params -Name \'PauseFeatureUpdatesStartTime\' -Value $start;',
'Set-ItemProperty @params -Name \'PauseFeatureUpdatesEndTime\' -Value $end;',
'Set-ItemProperty @params -Name \'PauseQualityUpdatesStartTime\' -Value $start;',
'Set-ItemProperty @params -Name \'PauseQualityUpdatesEndTime\' -Value $end;',
'Set-ItemProperty @params -Name \'PauseUpdatesStartTime\' -Value $start;',
'Set-ItemProperty @params -Name \'PauseUpdatesExpiryTime\' -Value $end;',
'</File>',

// Pause Windows Update
'<File path="C:\\Windows\\Setup\\Scripts\\PauseWindowsUpdate.xml">',
'<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">',
'<Triggers>',
'<BootTrigger>',
'<Repetition>',
'<Interval>P1D</Interval>',
'<StopAtDurationEnd>false</StopAtDurationEnd>',
'</Repetition>',
'<Enabled>true</Enabled>',
'</BootTrigger>',
'</Triggers>',
'<Principals>',
'<Principal id="Author">',
'<UserId>S-1-5-19</UserId>',
'<RunLevel>LeastPrivilege</RunLevel>',
'</Principal>',
'</Principals>',
'<Settings>',
'<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>',
'<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>',
'<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>',
'<AllowHardTerminate>true</AllowHardTerminate>',
'<StartWhenAvailable>false</StartWhenAvailable>',
'<RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>',
'<IdleSettings>',
'<StopOnIdleEnd>true</StopOnIdleEnd>',
'<RestartOnIdle>false</RestartOnIdle>',
'</IdleSettings>',
'<AllowStartOnDemand>true</AllowStartOnDemand>',
'<Enabled>true</Enabled>',
'<Hidden>false</Hidden>',
'<RunOnlyIfIdle>false</RunOnlyIfIdle>',
'<WakeToRun>false</WakeToRun>',
'<ExecutionTimeLimit>PT72H</ExecutionTimeLimit>',
'<Priority>7</Priority>',
'</Settings>',
'<Actions Context="Author">',
'<Exec>',
'<Command>C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe</Command>',
'<Arguments>-Command "Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\PauseWindowsUpdate.ps1\' -Raw | Invoke-Expression;"</Arguments>',
'</Exec>',
'</Actions>',
'</Task>',
'</File>',
// Set Start Pins
'<File path="C:\\Windows\\Setup\\Scripts\\SetStartPins.ps1">',
'$json = \'{"pinnedList":[]}\';',
'if( [System.Environment]::OSVersion.Version.Build -lt 20000 ) {',
'return;',
'}',

'$key = \'Registry::HKLM\\SOFTWARE\\Microsoft\\PolicyManager\\current\\device\\Start\';',
'New-Item -Path $key -ItemType \'Directory\' -ErrorAction \'SilentlyContinue\';',
'Set-ItemProperty -LiteralPath $key -Name \'ConfigureStartPins\' -Value $json -Type \'String\';',
'</File>',


'<File path="C:\\Windows\\Setup\\Scripts\\Specialize.ps1">',
'$scripts = @(',
'<?php echo $strin;?>BloatsSpecialize<?php echo $strou;?>',
'{ net.exe accounts /maxpwage:UNLIMITED; };',
'{',
'Register-ScheduledTask -TaskName \'PauseWindowsUpdate\' -Xml $( Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\PauseWindowsUpdate.xml\' -Raw );',
'};',
'{',
'reg.exe add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f;',
'};',
'{',
'reg.exe add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f;',
'};',
'{',
'reg.exe add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" /v "PreventDeviceEncryption" /t REG_DWORD /d 1 /f;',
'};',
'{',
'reg.exe add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f;',
'};',
'{',
'Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\SetStartPins.ps1\' -Raw | Invoke-Expression;',
'};',
'{',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ControlAnimations" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\AnimateMinMax" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\TaskbarAnimations" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\DWMAeroPeekEnabled" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\MenuAnimation" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\TooltipAnimation" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\SelectionFade" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\DWMSaveThumbnailEnabled" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\CursorShadow" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ListviewShadow" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ThumbnailsOrIcon" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ListviewAlphaSelect" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\DragFullWindows" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ComboBoxAnimation" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\FontSmoothing" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\ListBoxSmoothScrolling" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'Set-ItemProperty -LiteralPath "Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\\DropShadow" -Name \'DefaultValue\' -Value 0 -Type \'DWord\' -Force;',
'};',
');',
'',
'&amp; {',
'[float] $complete = 0;',
'[float] $increment = 100 / $scripts.Count;',
'foreach( $script in $scripts ) {',
'Write-Progress -Activity \'Running scripts to customize your Windows installation. Do not close this window.\' -PercentComplete $complete;',
'\'*** Will now execute command &#xAB;{0}&#xBB;.\' -f $(',
'$str = $script.ToString().Trim() -replace \'\\s+\', \' \';',
'$max = 100;',
'if( $str.Length -le $max ) {',
'$str;',
'} else {',
'$str.Substring( 0, $max - 1 ) + \'&#x2026;\';',
'}',
');',
'$start = [datetime]::Now;',
'&amp; $script;',
'\'*** Finished executing command after {0:0} ms.\' -f [datetime]::Now.Subtract( $start ).TotalMilliseconds;',
'"`r`n" * 3;',
'$complete += $increment;',
'}',
'} *>&amp;1 >> "C:\\Windows\\Setup\\Scripts\\Specialize.log";',
'</File>',

'<File path="C:\\Windows\\Setup\\Scripts\\UserOnce.ps1">',
'$scripts = @(',
'<?php echo $strin;?>BloatsUserOnce<?php echo $strou;?>',
'{',
'Set-ItemProperty -LiteralPath \'Registry::HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\' -Name \'VisualFXSetting\' -Type \'DWord\' -Value 2 -Force;',
'};',
');',
'',
'&amp; {',
'[float] $complete = 0;',
'[float] $increment = 100 / $scripts.Count;',
'foreach( $script in $scripts ) {',
'Write-Progress -Activity \'Running scripts to configure this user account. Do not close this window.\' -PercentComplete $complete;',
'\'*** Will now execute command &#xAB;{0}&#xBB;.\' -f $(',
'$str = $script.ToString().Trim() -replace \'\\s+\', \' \';',
'$max = 100;',
'if( $str.Length -le $max ) {',
'$str;',
'} else {',
'$str.Substring( 0, $max - 1 ) + \'&#x2026;\';',
'}',
');',
'$start = [datetime]::Now;',
'&amp; $script;',
'\'*** Finished executing command after {0:0} ms.\' -f [datetime]::Now.Subtract( $start ).TotalMilliseconds;',
'"`r`n" * 3;',
'$complete += $increment;',
'}',
'} *>&amp;1 >> "$env:TEMP\\UserOnce.log";',
'</File>',

'<File path="C:\\Windows\\Setup\\Scripts\\DefaultUser.ps1">',
'$scripts = @(',
'<?php echo $strin;?>BloatsDefaultUser<?php echo $strou;?>',
'{',
'reg.exe add "HKU\\DefaultUser\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f;',
'};',
'{',
'reg.exe add "HKU\\DefaultUser\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f;',
'};',
'{',
'reg.exe add "HKU\\DefaultUser\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v "UnattendedSetup" /t REG_SZ /d "powershell.exe -WindowStyle Normal -NoProfile -Command """Get-Content -LiteralPath \'C:\\Windows\\Setup\\Scripts\\UserOnce.ps1\' -Raw | Invoke-Expression;""" /f;',
'};',
');',
'</File>',
'<File path="C:\\Windows\\Setup\\Scripts\\FirstLogon.ps1">',
'$scripts = @(',
'{',
'Set-ItemProperty -LiteralPath \'Registry::HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\' -Name \'AutoLogonCount\' -Type \'DWord\' -Force -Value 0;',
'};',
');',
'&amp; {',
'[float] $complete = 0; ',
'[float] $increment = 100 / $scripts.Count;',
'foreach($script in $scripts )',
'{',
'Write-Progress -Activity \'Running scripts to finalize your Windows installation. Do not close this window.\' -PercentComplete $complete; \'*** Will now execute command «{0}».\' -f $( $str = $script.ToString().Trim() -replace \'\\s+\', \' \'; $max = 100; if( $str.Length -le $max ) { $str; } else { $str.Substring( 0, $max - 1 ) + \'…\'; } ); $start = [datetime]::Now; &amp; $script; \'*** Finished executing command after {0:0} ms.\' -f [datetime]::Now.Subtract( $start ).TotalMilliseconds; "`r`n" * 3; $complete += $increment;',
'}',
'} *>&amp;1 >> "C:\\Windows\\Setup\\Scripts\\FirstLogon.log";',
'</File>',
'</Extensions>',
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

if(isset($_SESSION['parameters'])) {
    $parameters = $_SESSION['parameters'];
}
else if(isset($_POST)) {
    $parameters = $_POST;
}
else {
    $parameters = NULL;
}

$f = new ValidatingForm();
$f->add(new HiddenTpl("codeToCopy"), array("value" => "", "hide" => true));


//==== NEW SECTION ====
// Installation Notes
//=====================
$f->add(new TitleElement(_T("Installation Notes", "imaging")));
$f->add(new TrFormElement("", new Iconereply('Installation_Notes', $InfoBule_Installation_Notes)));
$f->push(new Table());

//_____________
$f->add(
    new TrFormElement(_T('Title', 'imaging'), new InputTplTitle('Location', "name file xml")),
    array("required" => true,'value'=>(isset($parameters['Title'])) ? $parameters['Title'] : '')
);
//_____________
$f->add(new TrFormElement("Notes".":", new OptTextareaTpl(array('name'=>'Comments','value'=>(isset($parameters['Notes'])) ? $parameters['Notes'] : _T('Enter your comments here...', 'imaging')))));

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
    new TrFormElement(_T('Organization Name', 'imaging').":", new InputTplTitle('OrginazationName', $InfoBule_OrginazationName)),
    array('value' => (isset($parameters['OrginazationName'])) ? $parameters['OrginazationName'] : 'Medulla', "required" => true)
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
if(isset($parameters['Bloats'])){
    $blatsFlag = true;
}
foreach($bloats as $bloatName=>$bloat){
    $checked = '';
    if($blatsFlag && in_array($bloatName, $parameters['Bloats'])){
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
$bo = new buttonTpl('bvalid', _T("Validate", 'imaging'), 'btnPrimary', _T("Create Xml Windows Answer File Generator", "imaging"));
$rr = new TrFormElementcollapse($bo);
$rr->setstyle("text-align: center;");
$f->add(
    $rr
);
$f->add(
    new TrFormElement(
        "",
        new multifieldTpl(
            array(  new SpanElementtitle(_T("Xml Windows Answer File Generator", "imaging"), null, $InfoBule_showxml),
                    new Iconereply('awfg_show', $InfoBule_showxml)
                )
        )
    )
);
$f->pop();

$f->pop();
$f->display();

echo "<pre id='codeTocopy2' style='width:100%;'></pre>";
?>
