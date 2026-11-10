<?php
/**
 * (c) 2015-2025 Siveo, http://siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.var title = $( "em" ).attr( "title" );
 */

 // Windows 11 bloats
$bloats = [
    _T("3D Viewer", "mastering") => [
        "id"=>"viewer3d",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.Microsoft3DViewer'"],
        "value" => "3D Viewer",
    ],
    _T("Bing Search", "mastering") =>[
        "id"=>"bingsearch",
        "name" => "bloats[]",
        "removepackages" => ["'Microsoft.BingSearch'"],
        "value" =>"Bing Search",
    ],
    _T("Calculator", "mastering") =>[
        "id"=>"calculator",
        "name" => "bloats[]",
        "removepackages"=>["'Microsoft.WindowsCalculator'"],
        "value" =>"Calculator"
    ],
    _T("Camera", "mastering") =>[
        "id"=>"camera",
        "name" => "bloats[]",
        "removepackages"=>["'Microsoft.WindowsCamera'"],
        "value" =>"Camera"
    ],
    _T("Clipchamp", "mastering")=>[
        "id"=>"clipchamp",
        "name" => "bloats[]",
        "removepackages" =>["'Clipchamp.Clipchamp'"],
        "value" =>"Clipchamp"
    ],
    _T("Clock", "mastering")=>[
        "id"=>"clock",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.WindowsAlarms'"],
        "value" =>"Clock"
    ],
    _T("Copilot", "mastering")=>[
        "id"=>"copilot",
        "name" => "bloats[]",
        "useronce" => ['{
    Get-AppxPackage -Name \'Microsoft.Windows.Ai.Copilot.Provider\' | Remove-AppxPackage;
    }'],
        "defaultuser" => ['{
    reg.exe add "HKU\DefaultUser\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f;
    }'],
    "value" =>"Copilot"
    ],
    _T("Cortana", "mastering")=>[
        "id"=>"cortana",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.549981C3F5F10'"],
        "value" =>"Cortana"
    ],
    _T("Dev Home", "mastering")=>[
        "id"=>"devhome",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.Windows.DevHome'"],
        "specialize"=>['{
        Remove-Item -LiteralPath \'Registry::HKLM\\Software\\Microsoft\\WindowsUpdate\\Orchestrator\\UScheduler_Oobe\\DevHomeUpdate\' -Force -ErrorAction \'SilentlyContinue\';
        }'],
        "value" =>"Dev Home"
    ],
    _T("Family", "mastering")=>[
        "id"=>"family",
        "name" => "bloats[]",
        "removepackages" =>["'MicrosoftCorporationII.MicrosoftFamily'"],
        "value" =>"Family"
    ],
    _T("Feedback Hub", "mastering")=>[
        "id"=>"feedbackhub",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.WindowsFeedbackHub'"],
        "value" =>"Feedback Hub"
    ],
    _T("Get Help", "mastering")=>[
        "id"=>"gethelp",
        "name" => "bloats[]",
        "removepackages" =>["'Microsoft.GetHelp'"],
        "value" =>"Get Help"
    ],
    _T("Handwriting (all languages)", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"handwriting",
        "removecapabilities" =>["'Language.Handwriting'"],
        "value" =>"Handwriting (all languages)"
    ],
    _T("Internet Explorer", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"internetexplorer",
        "removecapabilities" =>["'Browser.InternetExplorer'"],
        "value" =>"Internet Explorer"
    ],
    _T("Mail and Calendar", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mailandcalendar",
        "removepackages" =>["'microsoft.windowscommunicationsapps'"],
        "value" =>"Mail and Calendar"
    ],
    _T("Maps", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"maps",
        "removepackages" =>["'Microsoft.WindowsMaps'"],
        "value" =>"Maps"
    ],
    _T("Math Input Panel", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mathinputpanel",
        "removecapabilities" =>["'MathRecognizer'"],
        "value" =>"Math Input Panel"
    ],
    _T("Media Features", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mediafeatures",
        "removefeatures" =>["'MediaPlayback'"],
        "value" =>"Media Features"
    ],
    _T("Mixed Reality", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mixedreality",
        "removepackages" =>["'Microsoft.MixedReality.Portal'"],
        "value" =>"Mixed Reality"
    ],
    _T("Movies & TV", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"moviesandtv",
        "removepackages" =>["'Microsoft.ZuneVideo'"],
        "value" =>"Movies & TV"
    ],
    _T("News", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"news",
        "removepackages" =>["'Microsoft.BingNews'"],
        "value" =>"News"
    ],
    _T("Notepad (modern)", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"notepadmodern",
        "removepackages" =>["'Microsoft.WindowsNotepad'"],
        "defaultuser" =>['{
    reg.exe add "HKU\DefaultUser\Software\Microsoft\Notepad" /v ShowStoreBanner /t REG_DWORD /d 0 /f;
}'],
"value" =>"Notepad (modern)"
    ],
    _T("Office 365", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"office365",
        "removepackages" =>["'Microsoft.MicrosoftOfficeHub'"],
        "value" =>"Office 365"
    ],
    _T("OneDrive", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"onedrive",
        "specialize" =>["Remove-Item -LiteralPath 'C:\Users\Default\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk', 'C:\Windows\System32\OneDriveSetup.exe', 'C:\Windows\SysWOW64\OneDriveSetup.exe' -ErrorAction 'Continue'"],
        "defaultuser" => ["Remove-ItemProperty -LiteralPath 'Registry::HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'OneDriveSetup' -Force -ErrorAction 'Continue'"],
        "value" =>"OneDrive"
    ],
    _T("OneNote", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"onenote",
        "removepackages" =>["'Microsoft.Office.OneNote'"],
        "value" =>"OneNote"
    ],
    _T("OnSync", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"onsync",
        "removecapabilities" =>["'OneCoreUAP.OneSync'"],
        "value" =>"OnSync"
    ],
    _T("OpenSSH Client", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"openssh",
        "removecapabilities" =>["'OpenSSH.Client'"],
        "value" =>"OpenSSH Client"
    ],
    _T("Outlook for Windows", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"outlook",
        "specialize" =>["Remove-Item -LiteralPath 'Registry::HKLM\Software\Microsoft\WindowsUpdate\Orchestrator\UScheduler_Oobe\OutlookUpdate' -Force -ErrorAction "],
        "removepackages" =>["'Microsoft.OutlookForWindows'"],
        "value" =>"Outlook for Windows"
    ],
    _T("Paint", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"paint",
        "removepackages" =>["'Microsoft.Paint'", "'Microsoft.MSPaint'"],
        "removecapabilities" =>["'Microsoft.MSPaint'"],
        "value" =>"Paint"
    ],
    _T("Paint 3D", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"paint3d",
        "removepackages" =>["'Microsoft.MSPaint'"],
        "value" =>"Paint 3D"
    ],
    _T("People", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"people",
        "removepackages" =>["'Microsoft.People'"],
        "value" =>"People"
    ],
    _T("Photos", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"photos",
        "removepackages" =>["'Microsoft.Windows.Photos'"],
        "value" =>"Photos"
    ],
    _T("Power Automate", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"powerautomate",
        "removepackages" =>["'Microsoft.PowerAutomateDesktop'"],
        "value" =>"Power Automate"
    ],
    _T("PowerShell 2.0", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"powershell2",
        "removefeatures" =>["'MicrosoftWindowsPowerShellV2Root'"],
        "value" =>"PowerShell 2.0"
    ],
    _T("PowerShell ISE", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"powershellise",
        "removecapabilities" =>["'Microsoft.Windows.PowerShell.ISE'"],
        "value" =>"PowerShell ISE"
    ],
    _T("Quick Assist", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"quickassist",
        "removecapabilities" =>["'App.Support.QuickAssist'"],
        "value" =>"Quick Assist"
    ],
    _T("Recall", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"recall",
        "removefeatures" =>["'Recall'"],
        "value" =>"Recall"
    ],
    _T("Remote Desktop Client", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"remotedesktop",
        "removefeatures" =>["'Microsoft-RemoteDesktopConnection'"],
        "value" =>"Remote Desktop Client"
    ],
    _T("Skype", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"skype",
        "removepackages" =>["'Microsoft.SkypeApp'"],
        "value" =>"Skype"
    ],
    _T("Snipping Tool", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"snippingtools",
        "removepackages" =>["'Microsoft.ScreenSketch'"],
        "removecapabilities" =>["'Microsoft.Windows.SnippingTool'"],
        "removefeatures" =>["'Microsoft-SnippingTool'"],
        "value" =>"Snipping Tool"
    ],
    _T("Solitaire Collection", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"solitairecollection",
        "removepackages" =>["'Microsoft.MicrosoftSolitaireCollection'"],
        "value" =>"Solitaire Collection"
    ],
    _T("Speech (all languages)", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"speech",
        "removecapabilities" =>["'Language.Speech'"],
        "value" =>"Speech (all languages)"
    ],
    _T("Text To Speech", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"texttospeech",
        "removepackages" =>[],
        "removecapavilities"=>["'Language.TextToSpeech'"],
        "value" =>"Text To Speech"
    ],
    _T("Steps Recorder", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"stepsrecorder",
        "removecapabilities" =>["'App.StepsRecorder'"],
        "value" =>"Steps Recorder"
    ],
    _T("Sticky Notes", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"stickynotes",
        "removepackages" =>["'Microsoft.MicrosoftStickyNotes'"],
        "value" =>"Sticky Notes"
    ],
    _T("Teams", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"teams",
        "removepackages" =>["'MicrosoftTeams'", "'MSTeams'"],
        "specialize"=>['reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Communications" /v ConfigureChatAutoInstall /t REG_DWORD'],
        "value" =>"Teams"
    ],
    _T("Tips", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"tips",
        "specialize" =>["Get-Content -LiteralPath 'C:\Windows\Setup\Scripts\RemovePackages.ps1' -Raw | Invoke-Expression"],
        "value" =>"Tips"
    ],
    _T("To Do", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"todo",
        "removepackages" =>["'Microsoft.Todos'"],
        "value" =>"To Do"
    ],
    _T("Voice Recorder", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"voicerecorder",
        "removepackages" =>["'Microsoft.WindowsSoundRecorder'"],
        "value" =>"Voice Recorder"
    ],
    _T("Wallet", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"wallet",
        "removepackages" =>["'Microsoft.Wallet'"],
        "value" =>"Wallet"
    ],
    _T("Weather", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"weather",
        "removepackages" =>["'Microsoft.BingWeather'"],
        "value" =>"Weather"
    ],
    _T("Windows Fax and Scan", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"windowsfaxandscan",
        "removecapabilities" =>["'Print.Fax.Scan'"],
        "specialize"=>["Get-Content -LiteralPath 'C:\Windows\Setup\Scripts\RemoveCapabilities.ps1' -Raw | Invoke-Expression;"],
        "value" =>"Windows Fax and Scan"
    ],
    _T("Windows Hello", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"windowshello",
        "removecapabilities" =>["'Hello.Face.18967'","'Hello.Face.Migration.18967'","Hello.Face.20134"],
        "value" =>"Windows Hello"
    ],
    _T("Windows Media Player (classic)", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mediaplayerclassic",
        "removecapabilities" =>["'Media.WindowsMediaPlayer'"],
        "value" =>"Windows Media Player (classic)"
    ],
    _T("Windows Media Player (modern)", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"mediaplayermodern",
        "removepackages" =>["'Microsoft.ZuneMusic'"],
        "value" =>"Windows Media Player (modern)"
    ],
    _T("Windows Terminal", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"windowsterminal",
        "removepackages" =>["'Microsoft.WindowsTerminal'"],
        "value" =>"Windows Terminal"
    ],
    _T("WordPad", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"wordpad",
        "removecapabilities" =>["'Microsoft.Windows.WordPad'"],
        "value" =>"WordPad"
    ],
    _T("Xbox Apps", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"xboxapps",
        "removepackages" =>["'Microsoft.Xbox.TCUI'", "'Microsoft.XboxApp'", "Microsoft.XboxGameOverlay", "Microsoft.XboxGamingOverlay", "Microsoft.XboxIdentityProvider", "Microsoft.XboxSpeechToTextOverlay", "Microsoft.GamingApp"],
        "defaultuser" =>['reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f;'],
        "value" =>"Xbox Apps"
    ],
    _T("Your Phone/Phone Link", "mastering")=>[
        "name" => "bloats[]",
        "id"=>"phonelink",
        "removepackages" =>["'Microsoft.YourPhone'"],
        "value" =>"Your Phone/Phone Link"
    ],
];

?>
<script type="text/javascript">

fn_Installation_Notes=function(){
    var list_id_masque=['Comments'];
    jQuery.each(list_id_masque, function( index,value) {
        jQuery('#'+value).parents("tr").toggle();
    });
    if (jQuery('#'+list_id_masque[0]).is(":visible")){
        jQuery('#Installation_Notes').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
    }
    else{
        jQuery('#Installation_Notes').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
    }
};


    fn_General_Settings=function(){
        var list_id_masque=[
            'ComputerName',
            'SetupUILanguage',
            "ShowWindowsLive",
            "InputLocale",
            "UserLocale",
            "TimeZone",
            "UILanguage",
            "AcceptEULA",
            "SkipAutoActivation",
            "SkipRearm"
        ];

        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#General_Settings').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#General_Settings').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };


    fn_Regional_Settings=function(){
        var list_id_masque=[];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Regional_Settings').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#Regional_Settings').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };


    fn_Out_Of_Box_Experience=function(){
        var list_id_masque=[
            "NetworkLocation",
            "HideEULA",
            "DaylightSettings",
            "HideWireless",
            "MachineOOBE",
            "UserOOBE",
            "ControlPanelView",
            "ControlPanelIconSize",
            "EnableFirewall"
        ];

        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Out_Of_Box_Experience').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#Out_Of_Box_Experience').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };


    fn_Partition_Settings=function(){
        var list_id_masque=[
            "Format",
            "DriveLetter",
            "Label",
            "InstallDisk",
            "PartitionOrder"
        ];

        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Partition_Settings').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#Partition_Settings').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };


    fn_User_Account=function(){
        var list_id_masque=[
            "FullName",
            "Group",
            "Description",
            "Password",
            "EnableUAC"
        ];

        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();

        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#User_Account').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#User_Account').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };


    fn_awfg_show=function(){
        var list_id_masque=["codeTocopy2"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#awfg_show').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#awfg_show').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };

    fn_Specialize_Settings=function(){
        var list_id_masque=[];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Specialize_Settings').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#Specialize_Settings').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    };

    fn_Bloatwares=function(){
        jQuery('input[name="bloats[]"').parents("tr").toggle();

        if (jQuery('input[name="bloats[]"').is(":visible")){
            jQuery('#Bloatwares').css( 'cursor', 'n-resize' ).attr('src', 'img/other/expanded.svg');
        }
        else{
            jQuery('#Bloatwares').css( 'cursor', 's-resize' ).attr('src', 'img/other/expand.svg');
        }
    }



    fn_Specialize_Settings()
    fn_General_Settings()
    fn_User_Account()
    fn_Regional_Settings()
    fn_Out_Of_Box_Experience()
    fn_Partition_Settings()
    fn_Bloatwares()
    fn_Installation_Notes()
    fn_awfg_show()
</script>


<?php

        $elementInputarray = array(
                                        'Albanian',
                                        'Arabic',
                                        'Arabic (102)',
                                        'Arabic (102) AZERTY',
                                        'Armenian Eastern',
                                        'Armenian Western',
                                        'Assamese - Inscript',
                                        'Azeri Cyrillic',
                                        'Azeri Latin',
                                        'Bashkir',
                                        'Belarusian',
                                        'Belgian (Comma)',
                                        'Belgian (Period)',
                                        'Belgian French',
                                        'Bengali',
                                        'Bengali - Inscript',
                                        'Bengali - Inscript (Legacy)',
                                        'Bosnian (Cyrillic)',
                                        'Bulgarian',
                                        'Bulgarian (Latin)',
                                        'Bulgarian (phonetic layout)',
                                        'Bulgarian (phonetic traditional)',
                                        'Canadian French',
                                        'Canadian French (Legacy)',
                                        'Canadian Multilingual Standard',
                                        'Chinese (Simplified) - US Keyboard',
                                        'Chinese (Traditional) - US Keyboard',
                                        'Chinese (Traditional Macao S.A.R.) US Keyboard',
                                        'Chinese (Simplified, Singapore) - US keyboard',
                                        'Croatian',
                                        'Czech',
                                        'Czech (QWERTY)',
                                        'Czech Programmers',
                                        'Danish',
                                        'Devanagari - Inscript',
                                        'Divehi Phonetic',
                                        'Divehi Typewriter',
                                        'Dutch',
                                        'Estonian',
                                        'Faeroese',
                                        'Finnish',
                                        'Finnish with Sami',
                                        'French',
                                        'Gaelic',
                                        'Georgian',
                                        'Georgian (Ergonomic)',
                                        'Georgian (QWERTY)',
                                        'German',
                                        'German (IBM)',
                                        'Greek',
                                        'Greek (220)',
                                        'Greek (220) Latin',
                                        'Greek (319)',
                                        'Greek (319) Latin',
                                        'Greek Latin',
                                        'Greek Polytonic',
                                        'Greenlandic',
                                        'Gujarati',
                                        'Hausa',
                                        'Hebrew',
                                        'Hindi Traditional',
                                        'Hungarian',
                                        'Hungarian 101-key',
                                        'Icelandic',
                                        'Igbo',
                                        'Inuktitut - Latin',
                                        'Inuktitut - Naqittaut',
                                        'Irish',
                                        'Italian',
                                        'Italian (142)',
                                        'Japanese',
                                        'Kannada',
                                        'Kazakh',
                                        'Khmer',
                                        'Korean',
                                        'Kyrgyz Cyrillic',
                                        'Lao',
                                        'Latin American',
                                        'Latvian',
                                        'Latvian (QWERTY)',
                                        'Lithuanian',
                                        'Lithuanian IBM',
                                        'Lithuanian New',
                                        'Luxembourgish',
                                        'Macedonian (FYROM)',
                                        'Macedonian (FYROM) - Standard',
                                        'Malayalam',
                                        'Maltese 47-Key',
                                        'Maltese 48-Key',
                                        'Maori',
                                        'Marathi',
                                        'Mongolian (Mongolian Script)',
                                        'Mongolian Cyrillic',
                                        'Nepali',
                                        'Norwegian',
                                        'Norwegian with Sami',
                                        'Oriya',
                                        'Pashto (Afghanistan)',
                                        'Persian',
                                        'Polish (214)',
                                        'Polish (Programmers)',
                                        'Portuguese',
                                        'Portuguese (Brazilian ABNT)',
                                        'Portuguese (Brazilian ABNT2)',
                                        'Punjabi',
                                        'Romanian (Legacy)',
                                        'Romanian (Programmers)',
                                        'Romanian (Standard)',
                                        'Russian',
                                        'Russian (Typewriter)',
                                        'Sami Extended Finland-Sweden',
                                        'Sami Extended Norway',
                                        'Serbian (Cyrillic)',
                                        'Serbian (Latin)',
                                        'Sesotho sa Leboa',
                                        'Setswana',
                                        'Sinhala',
                                        'Sinhala - wij',
                                        'Slovak',
                                        'Slovak (QWERTY)',
                                        'Slovenian',
                                        'Sorbian Extended',
                                        'Sorbian Standard',
                                        'Sorbian Standard (Legacy)',
                                        'Spanish',
                                        'Spanish Variation',
                                        'Swedish',
                                        'Swedish with Sami',
                                        'Swiss French',
                                        'Swiss German',
                                        'Syriac',
                                        'Syriac Phonetic',
                                        'Tajik',
                                        'Tamil',
                                        'Tatar',
                                        'Telugu',
                                        'Thai Kedmanee',
                                        'Thai Kedmanee (non-ShiftLock)',
                                        'Thai Pattachote',
                                        'Thai Pattachote (non-ShiftLock)',
                                        'Tibetan (PRC)',
                                        'Turkish F',
                                        'Turkish Q',
                                        'Turkmen',
                                        'Uyghur (Legacy)',
                                        'Ukrainian',
                                        'Ukrainian (Enhanced)',
                                        'United Kingdom',
                                        'United Kingdom Extended',
                                        'United States - Dvorak',
                                        'United States - International',
                                        'United States - Devorak for left hand',
                                        'United States - Dvorak for right hand',
                                        'United States - English',
                                        'Urdu',
                                        'Uyghur',
                                        'Uzbek Cyrillic',
                                        'Vietnamese',
                                        'Wolof',
                                        'Yakut',
                                        'Yoruba');
        $valeurInputarray = array(
                                        '1052:0000041c',
                                        '1025:00000401',
                                        '66561:00010401',
                                        '132097:00020401',
                                        '1067:0000042',
                                        '66603:0001042b',
                                        '1101:0000044',
                                        '2092:0000082c',
                                        '1068:0000042c',
                                        '1133:0000046d',
                                        '1059:00000423',
                                        '67596:0001080c',
                                        '2067:00000813',
                                        '2060:0000080c',
                                        '1093:00000445',
                                        '132165:00020445',
                                        '66629:00010445',
                                        '8218:0000201a',
                                        '197634:0030402',
                                        '66562:00010402',
                                        '132098:00020402',
                                        '263170:00040402',
                                        '4105:00001009',
                                        '3084:00000c0c',
                                        '69641:00011009',
                                        '2052:00000804',
                                        '1028:00000404',
                                        '5124:00001404',
                                        '4100:00001004',
                                        '1050:0000041a',
                                        '1029:00000405',
                                        '66565:00010405',
                                        '132101:00020405',
                                        '1030:00000406',
                                        '1081:00000439',
                                        '1125:00000465',
                                        '66661:00010465',
                                        '1043:00000413',
                                        '1061:00000425',
                                        '1080:00000438',
                                        '1035:0000040b',
                                        '67643:0001083b',
                                        '1036:0000040c',
                                        '71689:00011809',
                                        '55:00000437',
                                        '132151:00020437',
                                        '66615:00010437',
                                        '1031:00000407',
                                        '66567:00010407',
                                        '1032:00000408',
                                        '66568:00010408',
                                        '197640:00030408',
                                        '132104:00020408',
                                        '263176:00040408',
                                        '328713:00050409',
                                        '394248:00060408',
                                        '1135:0000046f',
                                        '1095:00000447',
                                        '1128:00000468',
                                        '1037:0000040d',
                                        '66617:00010439',
                                        '1038:0000040e',
                                        '66574:0001040e',
                                        '1039:0000040f',
                                        '1136:00000470',
                                        '2141:0000085d',
                                        '66653:0001045d',
                                        '6153:00001809',
                                        '1040:00000410',
                                        '66576:00010410',
                                        '1041:00000411',
                                        '1099:0000044b',
                                        '1087:0000043f',
                                        '1107:00000453',
                                        '1042:00000412',
                                        '1088:00000440',
                                        '1108:00000454',
                                        '2058:0000080a',
                                        '1062:00000426',
                                        '66598:00010426',
                                        '66599:00010427',
                                        '1063:00000427',
                                        '132135:00020427',
                                        '1134:0000046e',
                                        '1071:0000042f',
                                        '66607:0001042f',
                                        '1100:0000044c',
                                        '1082:0000043a',
                                        '66618:0001043a',
                                        '1153:00000481',
                                        '1102:0000044e',
                                        '2128:00000850',
                                        '1104:00000450',
                                        '1121:00000461',
                                        '1044:00000414',
                                        '1083:0000043b',
                                        '1096:00000448',
                                        '1123:00000463',
                                        '1065:00000429',
                                        '66581:00010415',
                                        '1045:00000415',
                                        '2070:00000816',
                                        '1046:00000416',
                                        '66582:00010416',
                                        '1094:00000446',
                                        '1048:00000418',
                                        '132120:00020418',
                                        '66584:00010418',
                                        '1049:00000419',
                                        '66585:00010419',
                                        '133179:0002083b',
                                        '66619:0001043b',
                                        '3098:00000c1a',
                                        '2074:0000081a',
                                        '1132:0000046c',
                                        '1074:00000432',
                                        '1115:0000045b',
                                        '66651:0001045b',
                                        '1051:0000041b',
                                        '66587:0001041b',
                                        '1060:00000424',
                                        '66606:0001042e',
                                        '132142:0002042e',
                                        '1070:0000042e',
                                        '1034:0000040a',
                                        '66570:0001040a',
                                        '1053:0000041d',
                                        '2107:0000083b',
                                        '4108:0000100c',
                                        '2055:00000807',
                                        '1114:0000045a',
                                        '66650:0001045a',
                                        '1064:00000428',
                                        '1097:00000449',
                                        '1092:00000444',
                                        '1098:0000044a',
                                        '1054:0000041e',
                                        '132126:0002041e',
                                        '66590:0001041e',
                                        '197662:0003041e',
                                        '1105:00000451',
                                        '66591:0001041f',
                                        '1055:0000041f',
                                        '1090:00000442',
                                        '1152:00000480',
                                        '1058:00000422',
                                        '132130:00020422',
                                        '2057:00000809',
                                        '1106:00000452',
                                        '66569:00010409',
                                        '132105:00020409',
                                        '197641:00030409',
                                        '263177:00040409',
                                        '1033:00000409',
                                        '1056:00000420',
                                        '66688:00010480',
                                        '2115:00000843',
                                        '1066:0000042a',
                                        '1160:00000488',
                                        '1157:00000485',
                                        '1130:0000046a');



        $eleUILanguage  = array(
                                        'Afrikaans - South Africa',
                                        'Albanian - Albania',
                                        'Alsatian - France',
                                        'Amharic - Ethiopia',
                                        'Arabic - Algeria',
                                        'Arabic - Bahrain',
                                        'Arabic - Egypt',
                                        'Arabic - Iraq',
                                        'Arabic - Jordan',
                                        'Arabic - Kuwait',
                                        'Arabic - Lebanon',
                                        'Arabic - Libya',
                                        'Arabic - Morocco',
                                        'Arabic - Oman',
                                        'Arabic - Qatar',
                                        'Arabic - Saudi Arabia',
                                        'Arabic - Syria',
                                        'Arabic - Tunisia',
                                        'Arabic - U.A.E.',
                                        'Arabic - Yemen',
                                        'Armenian - Armenia',
                                        'Assamese - India',
                                        'Azerbaijani - Azerbaijan (Cyrillic)',
                                        'Azerbaijani - Azerbaijan (Latin)',
                                        'Bangla - Bangladesh',
                                        'Bangla - India (Bengali Script)',
                                        'Bashkir - Russia',
                                        'Basque - Basque',
                                        'Belarusian - Belarus',
                                        'Bosnian - Bosnia and Herzegovina (Cyrillic)',
                                        'Bosnian - Bosnia and Herzegovina (Latin)',
                                        'Breton - France',
                                        'Bulgarian - Bulgaria',
                                        'Burmese - Myanmar',
                                        'Catalan - Catalan',
                                        'Central Atlas Tamazight (Latin) - Algeria',
                                        'Central Atlas Tamazight (Latin) - Algeria',
                                        'Central Atlas Tamazight (Tifinagh) - Morocco',
                                        'Central Kurdish (Iraq)',
                                        'Cherokee (Cherokee, United States)',
                                        'Chinese - Hong Kong',
                                        'Chinese - Macao',
                                        'Chinese - PRC',
                                        'Chinese - Singapore',
                                        'Corsican - France',
                                        'Croatian - Bosnia and Herzegovina',
                                        'Croatian - Croatia',
                                        'Czech - Czech Republic',
                                        'Danish - Denmark',
                                        'Dari - Afghanistan',
                                        'Divehi - Maldives',
                                        'Dutch - Belgium',
                                        'Dutch - Netherlands',
                                        'English - Australia',
                                        'English - Belize',
                                        'English - Canada',
                                        'English - Caribbean',
                                        'English - India',
                                        'English - Ireland',
                                        'English - Jamaica',
                                        'English - Malaysia',
                                        'English - New Zealand',
                                        'English - Philippines',
                                        'English - Singapore',
                                        'English - South Africa',
                                        'English - Trinidad',
                                        'English - United Kingdom',
                                        'English - United States',
                                        'English - Zimbabwe',
                                        'Estonian - Estonia',
                                        'Faroese - Faroe Islands',
                                        'Filipino - Philippines',
                                        'Finnish - Finland',
                                        'French - Belgium',
                                        'French - Canada',
                                        'French - France',
                                        'French - Luxembourg',
                                        'French - Monaco',
                                        'French - Switzerland',
                                        'Frisian - Netherlands',
                                        'Fulah (Latin, Senegal)',
                                        'Galician - Galician',
                                        'Georgian - Georgia',
                                        'German - Austria',
                                        'German - Germany',
                                        'German - Liechtenstein',
                                        'German - Luxembourg',
                                        'German - Switzerland',
                                        'Greek - Greece',
                                        'Greenlandic - Greenland',
                                        'Guarani - Paraguay',
                                        'Gujarati - India (Gujarati Script)',
                                        'Hausa (Latin) - Nigeria',
                                        'Hawaiian - United States',
                                        'Hebrew - Israel',
                                        'Hindi - India',
                                        'Hungarian - Hungary',
                                        'Icelandic - Iceland',
                                        'Igbo - Nigeria',
                                        'Inari Sami - Finland',
                                        'Indonesian - Indonesia',
                                        'Inuktitut (Latin) - Canada',
                                        'Inuktitut (Syllabics) - Canada',
                                        'Irish - Ireland',
                                        'isiXhosa / Xhosa - South Africa',
                                        'isiZulu / Zulu - South Africa',
                                        'Italian - Italy',
                                        'Italian - Switzerland',
                                        'Japanese - Japan',
                                        'Javanese (Latin) - Indonesia',
                                        'Kannada - India (Kannada Script)',
                                        'Kazakh - Kazakhstan',
                                        'Khmer - Cambodia',
                                        'K\'iche - Guatemala',
                                        'Kinyarwanda - Rwanda',
                                        'Konkani - India',
                                        'Korean(Extended Wansung) - Korea',
                                        'Kyrgyz - Kyrgyzstan',
                                        'Lao - Lao PDR',
                                        'Latvian - Legacy',
                                        'Latvian - Standard',
                                        'Lithuanian - Lithuania',
                                        'Lower Sorbian - Germany',
                                        'Lule Sami - Norway',
                                        'Lule Sami - Sweden',
                                        'Luxembourgish - Luxembourg',
                                        'Macedonian - F.Y.R.O.M',
                                        'Malay - Brunei',
                                        'Malay - Malaysia',
                                        'Malayalam - India (Malayalam Script)',
                                        'Maltese - Malta',
                                        'Maori - New Zealand',
                                        'Mapudungun - Chile',
                                        'Marathi - India',
                                        'Mohawk - Mohawk',
                                        'Mongolian (Cyrillic) - Mongolia',
                                        'Mongolian (Mongolian) - Mongolia',
                                        'Mongolian (Mongolian - PRC - Legacy)',
                                        'Mongolian (Mongolian - PRC - Standard)',
                                        'N\'ko - Guinea',
                                        'Nepali - Nepal',
                                        'Northern Sami - Finland',
                                        'Northern Sami - Norway',
                                        'Northern Sami - Sweden',
                                        'Norwegian - Norway (Bokmal)',
                                        'Norwegian - Norway (Nynorsk)',
                                        'Occitan - France',
                                        'Odia - India (Odia Script)',
                                        'Pashto - Afghanistan',
                                        'Persian',
                                        'Polish - Poland',
                                        'Portuguese - Brazil',
                                        'Portuguese - Portugal',
                                        'Punjabi - India (Gurmukhi Script)',
                                        'Punjabi (Islamic Republic of Pakistan)',
                                        'Quechua - Bolivia',
                                        'Quechua - Ecuador',
                                        'Quechua - Peru',
                                        'Romanian - Romania',
                                        'Romansh - Switzerland',
                                        'Russian - Russia',
                                        'Sakha - Russia',
                                        'Sanskrit - India',
                                        'Scottish Gaelic - United Kingdom',
                                        'Serbian - Bosnia and Herzegovina (Cyrillic)',
                                        'Serbian - Bosnia and Herzegovina (Latin)',
                                        'Serbian - Montenegro (Cyrillic)',
                                        'Serbian - Montenegro (Latin)',
                                        'Serbian - Serbia (Cyrillic)',
                                        'Serbian - Serbia (Latin)',
                                        'Serbian - Serbia and Montenegro (Former) (Cyrillic)',
                                        'Serbian - Serbia and Montenegro (Former) (Latin)',
                                        'Sesotho sa Leboa / Northern Sotho - South Africa',
                                        'Setswana / Tswana - Botswana',
                                        'Setswana / Tswana - South Africa',
                                        'Shona - Zimbabwe',
                                        'Sindhi (Islamic Republic of Pakistan)',
                                        'Sinhala - Sri Lanka',
                                        'Skolt Sami - Finland',
                                        'Slovak - Slovakia',
                                        'Slovenian - Slovenia',
                                        'Southern Sami - Norway',
                                        'Southern Sami - Sweden',
                                        'Spanish - Argentina',
                                        'Spanish - Bolivarian Republic of Venezuela',
                                        'Spanish - Bolivia',
                                        'Spanish - Chile',
                                        'Spanish - Colombia',
                                        'Spanish - Costa Rica',
                                        'Spanish - Dominican Republic',
                                        'Spanish - Ecuador',
                                        'Spanish - El Salvador',
                                        'Spanish - Guatemala',
                                        'Spanish - Honduras',
                                        'Spanish - Mexico',
                                        'Spanish - Nicaragua',
                                        'Spanish - Panama',
                                        'Spanish - Paraguay',
                                        'Spanish - Peru',
                                        'Spanish - Puerto Rico',
                                        'Spanish - Spain (International Sort)',
                                        'Spanish - Spain (Traditional Sort)',
                                        'Spanish - United States',
                                        'Spanish - Uruguay',
                                        'Standard Moroccan Tamazight - Morocco',
                                        'Swahili - Kenya',
                                        'Swedish - Finland',
                                        'Swedish - Sweden',
                                        'Syriac - Syria',
                                        'Tajik - Tajikistan',
                                        'Tamil - India',
                                        'Tamil - Sri Lanka',
                                        'Tatar - Russia (Legacy)',
                                        'Tatar - Russia (Standard)',
                                        'Telugu - India (Telugu Script)',
                                        'Thai - Thailand',
                                        'Tibetan - PRC',
                                        'Tigrinya (Eritrea)',
                                        'Tigrinya (Ethiopia)',
                                        'Turkish - Turkey',
                                        'Turkmen - Turkmenistan',
                                        'Ukrainian - Ukraine',
                                        'Upper Sorbian - Germany',
                                        'Urdu - India',
                                        'Urdu (Islamic Republic of Pakistan)',
                                        'Uyghur - PRC',
                                        'Uzbek - Uzbekistan (Cyrillic)',
                                        'Uzbek - Uzbekistan (Latin)',
                                        'Valencian - Valencia',
                                        'Vietnamese - Vietnam',
                                        'Welsh - United Kingdom',
                                        'Wolof - Senegal',
                                        'Yi - PRC',
                                        'Yoruba - Nigeria');

        $valUILanguage  = array(
                                        'af-ZA',
                                        'sq-AL',
                                        'gsw-FR',
                                        'am-ET',
                                        'ar-DZ',
                                        'ar-BH',
                                        'ar-EG',
                                        'ar-IQ',
                                        'ar-JO',
                                        'ar-KW',
                                        'ar-LB',
                                        'ar-LY',
                                        'ar-MA',
                                        'ar-OM',
                                        'ar-QA',
                                        'ar-SA',
                                        'ar-SY',
                                        'ar-TN',
                                        'ar-AE',
                                        'ar-YE',
                                        'hy-AM',
                                        'as-IN',
                                        'az-Cyrl-AZ',
                                        'az-Latn-AZ',
                                        'bn-BD',
                                        'bn-IN',
                                        'ba-RU',
                                        'eu-ES',
                                        'be-BY',
                                        'bs-Cyrl-BA',
                                        'bs-Latn-BA',
                                        'br-FR',
                                        'bg-BG',
                                        'my-MM',
                                        'ca-ES',
                                        'fr-FR',
                                        'tzm-Latn-DZ',
                                        'tzm-Tfng-MA',
                                        'ku-Arab-IQ',
                                        'chr-Cher-US',
                                        'zh-TW',
                                        'zh-TW',
                                        'zh-CN',
                                        'zh-CN',
                                        'co-FR',
                                        'hr-BA',
                                        'hr-HR',
                                        'cs-CZ',
                                        'da-DK',
                                        'prs-AF',
                                        'dv-MV',
                                        'nl-BE',
                                        'nl-NL',
                                        'en-AU',
                                        'en-BZ',
                                        'en-CA',
                                        'en-029',
                                        'en-IN',
                                        'en-IE',
                                        'en-JM',
                                        'en-MY',
                                        'en-NZ',
                                        'en-PH',
                                        'en-SG',
                                        'en-ZA',
                                        'en-TT',
                                        'en-GB',
                                        'en-US',
                                        'en-ZW',
                                        'et-EE',
                                        'fo-FO',
                                        'fil-PH',
                                        'fi-FI',
                                        'fr-BE',
                                        'fr-CA',
                                        'fr-FR',
                                        'fr-LU',
                                        'fr-MC',
                                        'fr-CH',
                                        'fy-NL',
                                        'ff-Latn-SN',
                                        'gl-ES',
                                        'ka-GE',
                                        'de-AT',
                                        'de-DE',
                                        'de-LI',
                                        'de-LU',
                                        'de-CH',
                                        'el-GR',
                                        'kl-GL',
                                        'gn-PY',
                                        'gu-IN',
                                        'ha-Latn-NG',
                                        'haw-US',
                                        'he-IL',
                                        'hi-IN',
                                        'hu-HU',
                                        'is-IS',
                                        'ig-NG',
                                        'smn-FI',
                                        'id-ID',
                                        'iu-Latn-CA',
                                        'iu-Cans-CA',
                                        'ga-IE',
                                        'xh-ZA',
                                        'zu-ZA',
                                        'it-IT',
                                        'it-CH',
                                        'ja-JP',
                                        'jv-Latn-ID',
                                        'kn-IN',
                                        'kk-KZ',
                                        'km-KH',
                                        'qut-GT',
                                        'rw-RW',
                                        'kok-IN',
                                        'ko-KR',
                                        'ky-KG',
                                        'lo-LA',
                                        'lv-LV',
                                        'lv-LV',
                                        'lt-LT',
                                        'dsb-DE',
                                        'smj-NO',
                                        'smj-SE',
                                        'lb-LU',
                                        'mk-MK',
                                        'ms-BN',
                                        'ms-MY',
                                        'ml-IN',
                                        'mt-MT',
                                        'mi-NZ',
                                        'arn-CL',
                                        'mr-IN',
                                        'moh-CA',
                                        'mn-MN',
                                        'mn-Mong-MN',
                                        'mn-Mong-CN',
                                        'mn-Mong-CN',
                                        'nqo-GN',
                                        'ne-NP',
                                        'se-FI',
                                        'se-NO',
                                        'se-SE',
                                        'nb-NO',
                                        'nn-NO',
                                        'oc-FR',
                                        'or-IN',
                                        'ps-AF',
                                        'fa-IR',
                                        'pl-PL',
                                        'pt-BR',
                                        'pt-PT',
                                        'pa-IN',
                                        'pa-Arab-PK',
                                        'quz-BO',
                                        'quz-EC',
                                        'quz-PE',
                                        'ro-RO',
                                        'rm-CH',
                                        'ru-RU',
                                        'sah-RU',
                                        'sa-IN',
                                        'gd-GB',
                                        'sr-Cyrl-BA',
                                        'sr-Latn-BA',
                                        'sr-Cyrl-ME',
                                        'sr-Latn-ME',
                                        'sr-Cyrl-RS',
                                        'sr-Latn-RS',
                                        'sr-Cyrl-CS',
                                        'sr-Latn-CS',
                                        'nso-ZA',
                                        'tn-BW',
                                        'tn-ZA',
                                        'sn-Latn-ZW',
                                        'sd-Arab-PK',
                                        'si-LK',
                                        'sms-FI',
                                        'sk-SK',
                                        'sl-SI',
                                        'sma-NO',
                                        'sma-SE',
                                        'es-AR',
                                        'es-VE',
                                        'es-BO',
                                        'es-CL',
                                        'es-CO',
                                        'es-CR',
                                        'es-DO',
                                        'es-EC',
                                        'es-SV',
                                        'es-GT',
                                        'es-HN',
                                        'es-MX',
                                        'es-NI',
                                        'es-PA',
                                        'es-PY',
                                        'es-PE',
                                        'es-PR',
                                        'es-ES',
                                        'es-ES_tradnl',
                                        'es-US',
                                        'es-UY',
                                        'zgh-Tfng-MA',
                                        'sw-KE',
                                        'sv-FI',
                                        'sv-SE',
                                        'syr-SY',
                                        'tg-Cyrl-TJ',
                                        'ta-IN',
                                        'ta-LK',
                                        'tt-RU',
                                        'tt-RU',
                                        'te-IN',
                                        'th-TH',
                                        'bo-CN',
                                        'ti-ET',
                                        'ti-ET',
                                        'tr-TR',
                                        'tk-TM',
                                        'uk-UA',
                                        'hsb-DE',
                                        'ur-IN',
                                        'ur-PK',
                                        'ug-CN',
                                        'uz-Cyrl-UZ',
                                        'uz-Latn-UZ',
                                        'ca-ES-valencia',
                                        'vi-VN',
                                        'cy-GB',
                                        'wo-SN',
                                        'ii-CN',
                                        'yo-NG');

        $element_timezone = array(      '(UTC-12:00) International Date Line West',
                                        '(UTC-11:00) Midway Island, Samoa',
                                        '(UTC-10:00) Hawaii',
                                        '(UTC-09:00) Alaska',
                                        '(UTC-08:00) Pacific Time (US &amp; Canada)',
                                        '(UTC-08:00) Tijuana, Baja California',
                                        '(UTC-07:00) Arizona',
                                        '(UTC-07:00) Chihuahua, La Paz, Mazatlan',
                                        '(UTC-07:00) Mountain Time (US &amp; Canada)',
                                        '(UTC-06:00) Central America',
                                        '(UTC-06:00) Central Time (US &amp; Canada)',
                                        '(UTC-06:00) Guadalajara, Mexico City, Monterrey',
                                        '(UTC-06:00) Saskatchewan',
                                        '(UTC-05:00) Bogota, Lima, Quito',
                                        '(UTC-05:00) Eastern Time (US &amp; Canada)',
                                        '(UTC-05:00) Indiana (East)',
                                        '(UTC-04:30) Caracas',
                                        '(UTC-04:00) Asuncion',
                                        '(UTC-04:00) Atlantic Time (Canada)',
                                        '(UTC-04:00) Georgetown, La Paz, San Juan',
                                        '(UTC-04:00) Santiago',
                                        '(UTC-03:30) Newfoundland',
                                        '(UTC-03:00) Brasilia',
                                        '(UTC-03:00) Buenos Aires',
                                        '(UTC-03:00) Cayenne',
                                        '(UTC-03:00) Greenland',
                                        '(UTC-03:00) Montevideo',
                                        '(UTC-02:00) Mid-Atlantic',
                                        '(UTC-01:00) Azores',
                                        '(UTC-01:00) Cape Verde Is.',
                                        '(UTC) Casablanca',
                                        '(UTC) Coordinated Universal Time',
                                        '(UTC) Dublin, Edinburgh, Lisbon, London',
                                        '(UTC) Monrovia, Reykjavik',
                                        '(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna',
                                        '(UTC+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague',
                                        '(UTC+01:00) Brussels, Copenhagen, Madrid, Paris',
                                        '(UTC+01:00) Sarajevo, Skopje, Warsaw, Zagreb',
                                        '(UTC+01:00) West Central Africa',
                                        '(UTC+02:00) Amman',
                                        '(UTC+02:00) Athens, Bucharest, Istanbul',
                                        '(UTC+02:00) Beirut',
                                        '(UTC+02:00) Cairo',
                                        '(UTC+02:00) Harare, Pretoria',
                                        '(UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius',
                                        '(UTC+02:00) Jerusalem',
                                        '(UTC+02:00) Minsk',
                                        '(UTC+02:00) Windhoek',
                                        '(UTC+03:00) Baghdad',
                                        '(UTC+03:00) Kuwait, Riyadh',
                                        '(UTC+03:00) Moscow, St. Petersburg, Volgograd',
                                        '(UTC+03:00) Nairobi',
                                        '(UTC+03:00) Tbilisi',
                                        '(UTC+03:30) Tehran',
                                        '(UTC+04:00) Abu Dhabi, Muscat',
                                        '(UTC+04:00) Baku',
                                        '(UTC+04:00) Port Louis',
                                        '(UTC+04:00) Yerevan',
                                        '(UTC+04:30) Kabul',
                                        '(UTC+05:00) Ekaterinburg',
                                        '(UTC+05:00) Islamabad, Karachi',
                                        '(UTC+05:00) Tashkent',
                                        '(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi',
                                        '(UTC+05:45) Kathmandu',
                                        '(UTC+06:00) Almaty, Novosibirsk',
                                        '(UTC+06:00) Astana, Dhaka',
                                        '(UTC+06:30) Yangon (Rangoon)',
                                        '(UTC+07:00) Bangkok, Hanoi, Jakarta',
                                        '(UTC+07:00) Krasnoyarsk',
                                        '(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi',
                                        '(UTC+08:00) Irkutsk, Ulaan Bataar',
                                        '(UTC+08:00) Kuala Lumpur, Singapore',
                                        '(UTC+08:00) Perth',
                                        '(UTC+08:00) Taipei',
                                        '(UTC+09:00) Osaka, Sapporo, Tokyo',
                                        '(UTC+09:00) Seoul',
                                        '(UTC+09:00) Yakutsk',
                                        '(UTC+09:30) Adelaide',
                                        '(UTC+09:30) Darwin',
                                        '(UTC+10:00) Brisbane',
                                        '(UTC+10:00) Canberra, Melbourne, Sydney',
                                        '(UTC+10:00) Guam, Port Moresby',
                                        '(UTC+10:00) Hobart',
                                        '(UTC+10:00) Vladivostok',
                                        '(UTC+11:00) Magadan, Solomon Is., New Caledonia',
                                        '(UTC+12:00) Auckland, Wellington',
                                        '(UTC+12:00) Fiji, Marshall Is.',
                                        '(UTC+12:00) Petropavlovsk-Kamchatsky',
                                        '(UTC+13:00) Nuku\'alofa');

        $val_timezone = array(          'Dateline Standard Time',
                                        'UTC-11',
                                        'Hawaiian Standard Time',
                                        'Alaskan Standard Time',
                                        'Pacific Standard Time',
                                        'Pacific Standard Time (Mexico)',
                                        'US Mountain Standard Time',
                                        'Mountain Standard Time (Mexico)',
                                        'Mountain Standard Time',
                                        'Central America Standard Time',
                                        'Central Standard Time',
                                        'Central Standard Time (Mexico)',
                                        'Canada Central Standard Time',
                                        'SA Pacific Standard Time',
                                        'Eastern Standard Time',
                                        'US Eastern Standard Time',
                                        'Venezuela Standard Time',
                                        'Paraguay Standard Time',
                                        'Atlantic Standard Time',
                                        'SA Western Standard Time',
                                        'Pacific SA Standard Time',
                                        'Newfoundland Standard Time',
                                        'E. South America Standard Time',
                                        'Argentina Standard Time',
                                        'SA Eastern Standard Time',
                                        'Greenland Standard Time',
                                        'Montevideo Standard Time',
                                        'Mid-Atlantic Standard Time',
                                        'Azores Standard Time',
                                        'Cape Verde Standard Time',
                                        'Morocco Standard Time',
                                        'UTC',
                                        'GMT Standard Time',
                                        'Greenwich Standard Time',
                                        'W. Europe Standard Time',
                                        'Central Europe Standard Time',
                                        'Romance Standard Time',
                                        'Central European Standard Time',
                                        'W. Central Africa Standard Time',
                                        'Jordan Standard Time',
                                        'GTB Standard Time',
                                        'Middle East Standard Time',
                                        'Egypt Standard Time',
                                        'South Africa Standard Time',
                                        'FLE Standard Time',
                                        'Israel Standard Time',
                                        'Kaliningrad Standard Time',
                                        'Namibia Standard Time',
                                        'Arabic Standard Time',
                                        'Arab Standard Time',
                                        'Russian Standard Time',
                                        'E. Africa Standard Time',
                                        'Georgian Standard Time',
                                        'Iran Standard Time',
                                        'Arabian Standard Time',
                                        'Azerbaijan Standard Time',
                                        'Mauritius Standard Time',
                                        'Caucasus Standard Time',
                                        'Afghanistan Standard Time',
                                        'Ekaterinburg Standard Time',
                                        'Pakistan Standard Time',
                                        'West Asia Standard Time',
                                        'India Standard Time',
                                        'Nepal Standard Time',
                                        'N. Central Asia Standard Time',
                                        'Central Asia Standard Time',
                                        'Myanmar Standard Time',
                                        'SE Asia Standard Time',
                                        'North Asia Standard Time',
                                        'China Standard Time',
                                        'North Asia East Standard Time',
                                        'Singapore Standard Time',
                                        'W. Australia Standard Time',
                                        'Taipei Standard Time',
                                        'Tokyo Standard Time',
                                        'Korea Standard Time',
                                        'Yakutsk Standard Time',
                                        'Cen. Australia Standard Time',
                                        'AUS Central Standard Time',
                                        'E. Australia Standard Time',
                                        'AUS Eastern Standard Time',
                                        'West Pacific Standard Time',
                                        'Tasmania Standard Time',
                                        'Vladivostok Standard Time',
                                        'Central Pacific Standard Time',
                                        'New Zealand Standard Time',
                                        'Fiji Standard Time',
                                        'UTC+12',
                                        'Tonga Standard Time');

        $DriveLetterTabElement = array('C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z');


       $GroupTabElement=array(
                                        _T('Account Operators','mastering'),
                                        _T('Administrators','mastering'),
                                        _T('Backup Operators','mastering'),
                                        _T('Crypto Operators','mastering'),
                                        _T('DCOM Users','mastering'),
                                        _T('Guests','mastering'),
                                        _T('IUsers','mastering'),
                                        _T('Network Configuration Operators','mastering'),
                                        _T('Perf Logging Users','mastering'),
                                        _T('Perf Monitoring Users','mastering'),
                                        _T('Power Users','mastering'),
                                        _T('Print Operators','mastering'),
                                        _T('Remote Desktop Users','mastering'),
                                        _T('Replicator','mastering'),
                                        _T('System Operators','mastering'),
                                        _T('Users','mastering'));
        $GroupTabValue = array(
                                        'AccountOperators',
                                        'Administrators',
                                        'BackupOperators',
                                        'CryptoOperators',
                                        'DCOMUsers',
                                        'Guests',
                                        'IUsers',
                                        'NetworkConfigurationOperators',
                                        'PerfLoggingUsers',
                                        'PerfMonitoringUsers',
                                        'PowerUsers',
                                        'PrintOperators',
                                        'RemoteDesktopUsers',
                                        'Replicator',
                                        'SystemOperators',
                                        'Users');
        $UpdatesTabElement= array(
                                        _T('Never check for updates','mastering'),
                                        _T('Check for updates but choose to download and install','mastering'),
                                        _T('Download updates but choose when to install','mastering'),
                                        _T('Install updates automatically','mastering'));

        $ProtectComputerTabElement = array(
                                        _T('Recommended settings','mastering'),
                                        _T('Install selective updates','mastering'),
                                        _T('Do not install selective updates','mastering'));


        $yes_no=        array(
                                        _T('Yes','mastering'),
                                        _T('No','mastering'));

        $truefalse = array(
                                        'true',
                                        'false');

        $suite2_5 = array(
                                        '2','3','4','5');
        $suite0_5 = array(
                                        '0','1','2','3','4','5');
        $suite4_7 = array(
                                        '4','5','6','7');

        $suite0_24 = array(             '0','1','2','3','4','5','6','7','8','9','10','11','12',
                                        '13','14','15','16','17','18','19','20','21','22','23','24');

        $EnableDisabled = array(
                                        _T('Enable','mastering'),
                                        _T('Disabled','mastering'));

//Windows 8
        $InfoBule_CEIPEnabled=
                        _T('CEIPEnabled indicates whether the Windows Customer Experience Improvement Program (CEIP) is enabled','mastering').
                        "\n".
                        _T('If the Microsoft-Windows-SQMAPI component is enabled, it collects and sends data to Microsoft about Windows usage','mastering').
                        "\n".
                        _T('Participation in this program is voluntary, and the results are recorded to implement improvements for future releases','mastering').
                        "\n".
                        _T('enabled ','mastering').
                        ' : '.
                        _T('Specifies that Windows CEIP is not enabled','mastering').
                        "\n".
                        _T('Disabled','mastering').
                        ' : '.
                        _T('Specifies that Windows CEIP is enabled','mastering');

        $InfoBule_SystemDefaultBackgroundColor=
                        _T('SystemDefaultBackgroundColor specifies the system default Windows background color scheme appearing on first boot, and on LogonUI if no user is selected','mastering');

        $InfoBule_UILanguage=
                        _T('Specifies the default system language to display user interface (UI) items (such as menus, dialog boxes, and help files)','mastering');

        $InfoBule_TimeZone=
                        _T('Specifies the time zone of the computer. The time zones that are specified in Windows System Image Manager are not localized','mastering');

        $InfoBule_Installation_Notes=
                        _T("Meta Information xml", "mastering");

        $InfoBule_General_Settings =
                        _T("Configure General Settings", "mastering");

        $InfoBule_ProductKey=
                        _T('Specifies the key used to activate Windows','mastering').
                        "\n".
                        _T('IMPORTANT','mastering').
                        "\n".
                        _T('Entering an invalid product key in the answer file will cause Windows Setup to fail','mastering');

        $InfoBule_AcceptEULA=
                        _T('Specifies whether to automatically accept the Microsoft Software License Terms','mastering').
                        "\n".
                        _T('Yes','mastering').
                        " : ".
                        _T('Specifies that the license terms are automatically accepted without being displayed to the end user','mastering').
                        "\n".
                        _T('No','mastering').
                        " : ".
                        _T('Prompts the user to accept the license terms before proceeding with Windows Setup','mastering');

        $InfoBule_SkipAutoActivation=
                        _T("Specifies whether Windows attempts to automatically activate",'mastering').
                        "\n".
                        _T("For automatic activation to complete, a valid Windows product key is required",'mastering').
                        "\n".
                        _T("true",'mastering').
                        " : ".
                        _T("Specifies that Windows does not attempt to automatically activate",'mastering').
                        "\n".
                        _T("false",'mastering').
                        " : ".
                        _T("Specifies that Windows attempts to automatically activate",'mastering');

        $InfoBule_SkipRearm=
                        _T('Specifies whether to run the Windows Software Licensing Rearm program','mastering').
                        "\n".
                        _T('Yes','mastering').
                        " : " .
                        _T('Specifies that the computer is not rearmed and the computer will not be restored to its original, out-of-box state. All activation-related licensing and registry data will remain and will not be reset. Similarly, any grace period timers is not reset.','mastering').
                        "\n".
                        _T('No','mastering').
                        " : "
                        ._T('Specifies that the computer is rearmed, restoring the computer to the original, out-of-box state. All activation-related licensing and registry data is removed or reset, and any grace period timers are also reset.','mastering');

        $InfoBule_SetupUILanguage= _T('SetupUILanguage defines the language to use in Windows Setup and Windows Deployment Services','mastering');

        $Infobule_ComputerName= _T("Specifies the computer name used to access the computer from the network",'mastering');

        $InfoBule_OrganizationName= _T("Specifies the name of the organization that owns the computer",'mastering');

        $InfoBule_UserLocale=
                        _T('Specifies the per-user settings used for formatting dates, times, currency, and numbers in a Windows installation','mastering');

        $Infobule_InputLocale=
                        _T('Specifies the input language and keyboard layout for a Windows installation', "mastering");

        $Infobule_Partition_Settings=
                        _T("Configure Partition Settings", "mastering");

        $InfoBule_Label=
                        _T('Main Partition Label','mastering');

        $InfoBule_User_Account =
                        _T("Configure User Account", "mastering");

        $InfoBule_Updates=
                        _T('CommandLine reg','mastering');

        $InfoBule_Out_Of_Box_Experience=
                        _T("OOBE specifies the out-of-box experience for the end user", "mastering").
                        "\n".
                        _T("These settings specify whether to do the following", "mastering").
                        " : \n".
                        _T("   - Hide the Microsoft Software License Terms page in Windows Welcome", "mastering").
                        "\n".
                        _T("   - Skip Windows Welcome, also known as Machine OOBE", "mastering").
                        "\n".
                        _T("   - Skip Welcome Center, also known as Per User OOBE", "mastering").
                        "\n".
                        _T("It also specifies the following", "mastering").
                        "\n".
                        _T("   - The network type", "mastering").
                        "\n".
                        _T("   - What type of computer protection is in place", "mastering");

        $InfoBule_NetworkLocation=
                        _T('Specifies the location of the network if the computer is connected to a network when a user first logs on','mastering').
                        "\n".
                        _T('Home','mastering').
                        " : ".
                        _T('Specifies a private home network','mastering').
                        "\n".
                        _T('Work','mastering').
                        " : ".
                        _T('Specifies a private office network','mastering').
                        "\n".
                        _T('Other','mastering').
                        " : ".
                        _T('Specifies neither a home or work network','mastering').
                        "\n".
                        _T('Network discovery is disabled by default on this network type','mastering');

        $InfoBule_ProtectComputer=
                        _T('Specifies whether to display the Help protect your computer automatically page of Windows Welcome to the user','mastering').
                        "\n".
                        _T('There is no default value. If a value is not set, the page opens during Windows Welcome','mastering').
                        "\n -1 : ".
                        _T('Specifies the recommended level of protection for your computer','mastering').
                        "\n -2 : ".
                        _T('Specifies that only updates are installed','mastering').
                        "\n -3 : ".
                        _T('Specifies that automatic protection is disabled','mastering');

        $InfoBule_HideEULA=
                        _T('Specifies whether to hide the Microsoft Software License Terms page of Windows Welcome','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that the Microsoft Software License Terms page of Windows Welcome is not displayed','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that the Microsoft Software License Terms page of Windows Welcome is displayed','mastering');

        $InfoBule_DaylightSettings=
                        _T('Specifies whether the time on the computer is set to daylight saving time','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that the time on the computer is not reset to daylight saving time','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that the time on the computer is reset to daylight saving time','mastering');

        $Infobule_HideWireless=
                        _T('Specifies whether to hide the Join Wireless Network screen that appears during Windows Welcome','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Hides the Join Wireless Network screen during Windows Welcome','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Does not hide the Join Wireless Network screen during Windows Welcome','mastering');

        $InfoBule_MachineOOBE=
                        _T('Specifies whether to skip Windows Welcome','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that Windows Welcome is skipped','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that Windows Welcome is shown','mastering').
                        "\n".
                        _T('warning','mastering').
                        "\n".
                        _T('If you enable SkipMachineOOBE, any settings specified for ProtectYourPC and NetworkLocation in your answer file are ignored','mastering');

        $InfoBule_UserOOBE=
                        _T('Specifies whether to skip Welcome Center. This can be used only for testing prior to shipment','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that Welcome Center is skipped','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that Welcome Center is shown','mastering');

        $InfoBule_ControlPanelView=
                        _T('CommandLine reg Set the Control Panel View to Small Icons','mastering');

        $InfoBule_ControlPanelIconSize=
                        _T('CommandLine reg ControlPanel AllItemsIconView','mastering');

        $InfoBule_WipeDisk=
                        _T('Specifies whether to erase all partitions on the hard disk before adding additional configurations to the disk','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that the disk is erased','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that the disk is not erased','mastering');

        $InfoBule_InstallDisk=
                        _T('Specifies the disk ID of the disk to which the image is to be installed','mastering').
                        "\n".
                        _T('This sequence starts with 0','mastering').
                        "\n".
                        _T('If you are installing to a computer with a single disk, you must specify 0','mastering').
                        "\n".
                        _T('Disk_ID is an integer','mastering');

        $InfoBule_Format=
                        _T('Specifies whether to erase the partition, and which file system to apply to the partition','mastering').
                        "\n".
                        _T('NTFS','mastering').
                        " : ".
                        _T('Formats the partition for the NTFS file system','mastering').
                        "\n".
                        _T('FAT32','mastering').
                        " : ".
                        _T('Formats the partition for the File Allocation Table (FAT) file system','mastering');

        $InfoBule_DriveLetter=
                        _T('Specifies the drive letter to apply to a partition. Drive_letter is an uppercase letter, C through Z','mastering');

        $InfoBule_PartitionOrder=
                        _T('Specifies the order in which the ModifyPartition command is to be run at first logon','mastering').
                        "\n".
                        _T('Synchronous commands start in the order specified in the unattended installation answer file, and each command must finish before the next command starts','mastering').
                        "\n".
                        _T('Synchronous commands are always run before asynchronous commands in the same configuration pass','mastering');

        $InfoBule_Administrators_Account=
                        _T("Configure Administrators Account", "mastering");

        $InfoBule_PasswordAdmin=
                        _T('Specifies the administrator password of the computer and whether it is hidden in the unattended installation answer file','mastering');

        $InfoBule_Group=
                        _T('Specifies the name of an existing local security group to which a new LocalAccount will be added during installation','mastering');

        $InfoBule_Description=
                        _T('Specifies a LocalAccount','mastering');

        $InfoBule_Password=
                        _T('Specifies the password for a LocalAccount and whether the password is hidden in the unattended installation answer file','mastering');

        $InfoBule_FullName=
                        _T('Specifies the name of the end user. User_name is a string with a maximum length of 63 characters','mastering');

        $InfoBule_EnableUAC=
                        _T('Specifies whether Windows User Account Controls (UAC) notifies the user when programs try to make changes to the computer. UAC was formerly known as Limited User Account (LUA)','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Windows notifies the user when programs try to make changes to the computer','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Windows does not notify the user when programs try to install software or make changes to the computer','mastering').
                        "\n\n".
                        _T('To provide better protection for computers connected to any kind of network (such as the Internet, a home network, or an organization network), the Windows operating system enables Windows Firewall on all network connections by default','mastering');

        $InfoBule_EnableFirewall=
                        _T('Windows Firewall is a stateful host firewall that discards unsolicited incoming traffic, providing a level of protection for computers against malicious users or programs','mastering').
                        "\n".
                        _T('To provide better protection for computers connected to any kind of network (such as the Internet, a home network, or an organization network), the Windows operating system enables Windows Firewall on all network connections by default','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Enables Windows Firewall for Windows PE','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Disables Windows Firewall for Windows PE','mastering');

        $InfoBule_CopyProfile=
                        _T('Use the following steps to use CopyProfile to set customized user profiles','mastering').
                        " : ".
                        "\n".
                        _T('Log on as a user whose profile you can customize (for example, the built-in-administrator account)','mastering').
                        "\n".
                        _T('Customize the desired user profile settings','mastering').
                        "\n".
                        _T('Set CopyProfile to true in the Unattend.xml file that you will use with Sysprep in the next step','mastering').
                        "\n".
                        _T('Run sysprep /generalize /unattend:unattend.xml to copy the customized user profile settings over the default user profile','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Changes the default user profile with customizations made . You must set this value to true only if you have made customizations to the logged-on user profile that you need to apply to all new users','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Does not change the default user profile','mastering');

        $InfoBule_ShowWindowsLive=
                        _T('ShowWindowsLive specifies whether to display a link to Windows Live on the Start menu','mastering').
                        "\n".
                        _T('If the Windows Live shortcut has been removed from the Start menu, this setting cannot be used to put it back on the Start menu','mastering').
                        "\n".
                        _T('true','mastering').
                        " : ".
                        _T('Specifies that a link to Windows Live is displayed on the Start menu','mastering').
                        "\n".
                        _T('false','mastering').
                        " : ".
                        _T('Specifies that a link to Windows Live is not displayed on the Start menu','mastering');

        $InfoBule_ExtendOSPartition=
                        _T("Specifies whether to extend the partition to fill the entire hard disk", "mastering");

        $InfoBule_backgroundWin8=
                        _T("In Windows 8, SystemDefaultBackgroundColor must be a value from 0 to 24, as shown in the following image, which represents the index of the color scheme as viewed in the SystemSettings", "mastering");

        $InfoBule_backgroundWin81=
                        _T("In Windows 8.1, SystemDefaultBackgroundColor must be a value from 0 to 24 which represents the index of the color scheme as viewed in the out-of-box experience (OOBE) phase. The colors are indexed in the same manner as Windows 8 colors, from left to right. Samples of the color choices are shown in the following image", "mastering");

        $InfoBule_showxml=
                        _T("Show file XML AWFG", "mastering");

		$InfoBule_Domain=_T("Domain specifies the name of the domain used for an account authentication. Domain is used to authenticate an account before the computer can be joined to a domain during Windows Setup.", "mastering");

		$InfoBule_DomainPassword=_T("Password specifies the password of the user account used for authentication of an account to the domain before the computer can be joined to a domain during Windows Setup.", "mastering");

		$InfoBule_DomainUser=_T("Username specifies the name of the user account with permission to add the computer to a domain during Windows Setup.","mastering");

		$InfoBule_JoinDomain = _T("Domain to join","mastering");

		$InfoBule_MachineObjectOU = _T("MachineObjectOU is an optional setting. It specifies the Lightweight Directory Access Protocol (LDAP) X 500-distinguished name of the organizational unit (OU) in which the computer account is created. This account is in Active Directory on a domain controller in the domain to which the computer is being joined.","mastering");

        $InfoBule_Bloatware = _T("Remove Bloatwares from the install", "mastering");
?>
