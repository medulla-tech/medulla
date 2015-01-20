<?php
/**
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.var title = $( "em" ).attr( "title" );
 */
 
 ?>
<script type="text/javascript">



function getExtension(filename){
        var parts = filename.split(".");
        return (parts[(parts.length-1)]);
    }
    
    jQuery( "#bvalid").click(function() {
        if(jQuery('#Location').val()=="" || jQuery('#Location').val()==".xml"){
            jQuery('#Location').focus()
        }
        else{
            createxml()
        }
    });
    createxml = function(){
    
    
        jQuery.post( "modules/imaging/manage/ajaxgenereAWFGxml.php", 
                            { 
                                data:  jQuery('#codeTocopy2').text(),
                                titre: jQuery('#Location').val() 
        })
        .done(function( data1 ) {        
            var file =  '  <? echo _T('File','imaging'); ?>  ';  
            var avai =  ' <? echo _T('available','imaging'); ?>'; 
                if(data1 == 1){
                    var  Msgxml1 = "Windows Answer File Generator available\non smb://"+window.location.host +"/postinst/sysprep/" + 
                            jQuery('#Location').val() ;
                    jQuery( "#spanxml" ).attr( "title", Msgxml1 );
                    //alert( file + jQuery('#Location').val() + avai)
                   
                }
        });
    }
 /*   
 //button subtmit form
jQuery( "#buttonform" ).click(function() {
  if( jQuery('#Location').val() != "" ){
   if(getExtension( jQuery('#Location').val() ) != "xml"){
    var namefile=jQuery('#Location').val() + ".xml"
      jQuery('#Location').val( namefile )
   }
   jQuery('input[name=bvalidbutton]').val("1");
   jQuery( "#formxml" ).submit();
   return false;
  }
  jQuery('#Location').focus()
  return false;
});*/




jQuery(function () {
    jQuery('#Comments').val('Enter your comments here...');
    jQuery('#Comments').bind('input propertychange', function() { update();});
    jQuery( '#Location' ).on('change', function () {
        if(getExtension( jQuery('#Location').val() ) != "xml"){
            var namefile=jQuery('#Location').val() + ".xml"
            jQuery('#Location').val( namefile )
        }
        update(); 
    });
    jQuery( '#ProductKey1' ).on( 'change',  function(){jQuery('#ProductKey1').val(jQuery('#ProductKey1').val().toUpperCase());
    update()});
    jQuery( '#ProductKey2' ).on( 'change',  function(){jQuery('#ProductKey2').val(jQuery('#ProductKey2').val().toUpperCase());update()});
    jQuery( '#ProductKey3' ).on( 'change',  function(){jQuery('#ProductKey3').val(jQuery('#ProductKey3').val().toUpperCase());update()});
    jQuery( '#ProductKey4' ).on( 'change',  function(){jQuery('#ProductKey4').val(jQuery('#ProductKey4').val().toUpperCase());update()});
    jQuery( '#ProductKey5' ).on( 'change',  function(){jQuery('#ProductKey5').val(jQuery('#ProductKey5').val().toUpperCase());update()});
    jQuery( '#AcceptEULA').on('change', function () { update(); });
    jQuery( '#EnableFirewall' ).on('change', function () { update(); });
    jQuery( '#ExtendOSPartition' ).on('change', function () { update(); });
    jQuery( '#ShowWindowsLive' ).on('change', function () { update(); });
    jQuery( '#CopyProfile' ).on('change', function () { update(); });
    jQuery( '#SkipAutoActivation' ).on('change', function () { update(); });
    jQuery( '#SkipRearm' ).on('change', function () { update(); });
    jQuery( '#SetupUILanguage' ).on('change', function () { update(); });
    jQuery( '#FullName' ).on('change', function () { update(); });
    jQuery( '#ComputerName' ).on('change', function () { update(); });
    jQuery( '#InputLocale' ).on('change', function () { update(); });
    jQuery( '#UserLocale' ).on('change', function () { update(); });
    jQuery( '#TimeZone' ).on('change', function () { update(); });
    jQuery( '#UILanguage' ).on('change', function () { update(); });
    jQuery( '#NetworkLocation' ).on('change', function () { update(); });
    jQuery( '#ProtectComputer' ).on('change', function () { update(); });
    jQuery( '#HideEULA' ).on('change', function () { update(); });
    jQuery( '#DaylightSettings' ).on('change', function () { update(); });
    jQuery( '#HideWireless' ).on('change', function () { update(); });
    jQuery( '#MachineOOBE' ).on('change', function () { update(); });
    jQuery( '#UserOOBE' ).on('change', function () { update(); });
    jQuery( '#WipeDisk' ).on('change', function () { update(); });
    jQuery( '#InstallDisk' ).on('change', function () { update(); });
    jQuery( '#Format' ).on('change', function () { update(); });
    jQuery( '#Label' ).on('change', function () { update(); });
    jQuery( '#DriveLetter' ).on('change', function () { update(); });
    jQuery( '#PartitionOrder' ).on('change', function () { update(); });
    jQuery( '#Group' ).on('change', function () { update(); });
    jQuery( '#Description' ).on('change', function () { update(); });
    jQuery( '#Password' ).on('change', function () { update(); });
    jQuery( '#Autologon' ).on('change', function () { update(); });
    jQuery( '#EnableUAC' ).on('change', function () { update(); });
    jQuery( '#Updates' ).on('change', function () { update(); });
    jQuery( '#OrginazationName' ).on('change', function () { update(); });
    jQuery( '#BGC').on('change', function () { update(); });
    jQuery( '#CEIPEnabled').on('change', function () { update(); });
    jQuery( '#ControlPanelView' ).on('change', function () { update(); });
    jQuery( '#ControlPanelIconSize' ).on('change', function () { update(); });
    jQuery( '#DownloadButton' ).on('change', function () { update(); });
    jQuery( '#PasswordAdmin' ).on('change', function () { update(); });
    update();
});


function update() {
    Msgxml  = "To have the Windows Answer File Generator on \n" + 
              "smb://" + window.location.host + "/postinst/sysprep/" + jQuery('#Location').val() + "\n" +
              "click on Validation" ;
    jQuery( "#spanxml" ).attr( "title", Msgxml );
    var erreur=0;
    if (jQuery('#OrginazationName').val() == ""){
            erreur = 2;
            msg = "<? echo _T('Organization Name missing','imaging'); ?>";
    }
    if( jQuery('#Location').val() == "" ||  jQuery('#Location').val() == ".xml" ){
            erreur = 1;
            msg = "<? echo _T('title missing','imaging'); ?>";
    }
    if(erreur != 0 ){
            jQuery("#msg_bvalid").text(msg)
            jQuery("#bvalid").prop('disabled', true);
            jQuery("#bvalid").prop('disabled', true);
            jQuery("#msg_bvalid").show();
      }
      else{
             jQuery( "#bvalid").prop('disabled', false);
             jQuery("#msg_bvalid").hide();
             
      }

    da=new Date()
    var dateval = da.getFullYear()+ '-'+da.getMonth() + '-' + da.getDate()
    var variables = {
        'Location': jQuery('#Location').val(),
        'Comments': jQuery('#Comments').val(),
        //'Arch': jQuery('#Arch').val(),
        'ProductKey1': jQuery('#ProductKey1').val().toUpperCase(),
        'ProductKey2': jQuery('#ProductKey2').val().toUpperCase(),
        'ProductKey3': jQuery('#ProductKey3').val().toUpperCase(),
        'ProductKey4': jQuery('#ProductKey4').val().toUpperCase(),
        'ProductKey5': jQuery('#ProductKey5').val().toUpperCase(),
        'EnableFirewall': jQuery('#EnableFirewall').find('option:selected').val(),
        'ShowWindowsLive' : jQuery('#ShowWindowsLive').find('option:selected').val(),
        'CopyProfile' : jQuery('#CopyProfile').find('option:selected').val(), 
        'ExtendOSPartition' :jQuery('#ExtendOSPartition').find('option:selected').val(),
        'SkipAutoActivation': jQuery('#SkipAutoActivation').find('option:selected').val(),
        'SkipRearm': jQuery('#SkipRearm').find('option:selected').val(),
        'AcceptEULA': jQuery('#AcceptEULA').find('option:selected').val(),
        'SetupUILanguage': jQuery('#SetupUILanguage').find('option:selected').val(),
        'FullName': jQuery('#FullName').val(),
        'ComputerName': jQuery('#ComputerName').val(),
        'InputLocale': jQuery('#InputLocale').find('option:selected').val(),
        'UserLocale': jQuery('#UserLocale').find('option:selected').val(),
        'TimeZone': jQuery('#TimeZone').find('option:selected').val(),
        'UILanguage': jQuery('#UILanguage').find('option:selected').val(),
        'NetworkLocation': jQuery('#NetworkLocation').find('option:selected').val(),
        'ProtectComputer': jQuery('#ProtectComputer').find('option:selected').val(),
        'HideEULA': jQuery('#HideEULA').find('option:selected').val(),
        'DaylightSettings': jQuery('#DaylightSettings').find('option:selected').val(),
        'HideWireless': jQuery('#HideWireless').find('option:selected').val(),
        'MachineOOBE': jQuery('#MachineOOBE').find('option:selected').val(),
        'UserOOBE': jQuery('#UserOOBE').find('option:selected').val(),
        'WipeDisk': jQuery('#WipeDisk').find('option:selected').val(),
        'InstallDisk': jQuery('#InstallDisk').find('option:selected').val(),
        'MainPartition': jQuery('#MainPartition').find('option:selected').val(),
        'Format': jQuery('#Format').find('option:selected').val(),
        'Label': jQuery('#Label').val(),
        'DriveLetter': jQuery('#DriveLetter').find('option:selected').val(),
        'PartitionOrder': jQuery('#PartitionOrder').find('option:selected').val(),
        'Group': jQuery('#Group').find('option:selected').val(),
        'Description': jQuery('#Description').val(),
        'Password': jQuery('#Password').val(),
        'PasswordAdmin': jQuery('#PasswordAdmin').val(),
        'Autologon': jQuery('#Autologon').find('option:selected').val(),
        'EnableUAC': jQuery('#EnableUAC').find('option:selected').val(),
        'Updates': jQuery('#Updates').find('option:selected').val(),
        'OrginazationName': jQuery('#OrginazationName').val(),
        'BGC':jQuery( '#BGC').find('option:selected').val(),
        'CEIPEnabled':jQuery( '#CEIPEnabled').find('option:selected').val(),  
        'ControlPanelView': jQuery('#ControlPanelView').find('option:selected').val(),
        'ControlPanelIconSize': jQuery('#ControlPanelIconSize').find('option:selected').val(),
        'dateval': dateval
    };
        listParameters={}

        var newXml = template.replace(/<\?(\w+)\?>/g,
        function(match, name) {
            if(!((name == "dateval") || (name == "Location") || (name == "Comments"))) listParameters[name]=variables[name]
        return variables[name];
        });

        var myJsonString = JSON.stringify(listParameters);
        newXml = newXml.replace("@@listParameters@@",myJsonString);
        jQuery('input[name=codeToCopy]').val(newXml);
        jQuery.post( "modules/imaging/manage/ajaxmiseenforme.php", { data: newXml })
            .done(function( data1 ) {
                jQuery('#codeTocopy2').text(data1);
        });
}


    fn_Installation_Notes=function(){
        var list_id_masque=['Comments'];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Installation_Notes').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Installation_Notes').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_General_Settings=function(){
        var list_id_masque=[//'SkipProductKey',
                            'AcceptEULA',
                            'ComputerName',
                            'SetupUILanguage',
                            'SkipRearm',
                            'SkipAutoActivation'];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#General_Settings').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#General_Settings').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_Regional_Settings=function(){
        var list_id_masque=["InputLocale",
                            "UserLocale",
                            "TimeZone",
                            "UILanguage"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Regional_Settings').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Regional_Settings').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_Out_Of_Box_Experience=function(){
        var list_id_masque=["NetworkLocation",
                            "ProtectComputer",
                            "Updates",
                            "HideEULA",
                            "DaylightSettings",
                            "HideWireless",
                            "MachineOOBE",
                            "UserOOBE",
                            "ControlPanelView",
                            "ControlPanelIconSize"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Out_Of_Box_Experience').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Out_Of_Box_Experience').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_Partition_Settings=function(){
        var list_id_masque=[//"MainPartition",
                            "Format",
                            "DriveLetter",
                            "Label"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Partition_Settings').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Partition_Settings').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_Administrators_Account=function(){
        var list_id_masque=["PasswordAdmin"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Administrators_Account').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Administrators_Account').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_User_Account=function(){
        var list_id_masque=["FullName",
                            "Group",
                            "Description",
                            "Password",
                            "EnableUAC",
                            "Autologon",
                            "EnableFirewall"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
            
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#User_Account').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#User_Account').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };
    fn_awfg_show=function(){
        var list_id_masque=["codeTocopy2"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#awfg_show').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#awfg_show').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };

    fn_Specialize_Settings=function(){
        var list_id_masque=["CopyProfile",
                            "ShowWindowsLive",
                            "ExtendOSPartition"];
        jQuery.each(list_id_masque, function( index,value) {
            jQuery('#'+value).parents("tr").toggle();
        });
        if (jQuery('#'+list_id_masque[0]).is(":visible")){
            jQuery('#Specialize_Settings').css( 'cursor', 'n-resize' ).attr('src', 'modules/imaging/graph/images/imaging-del.png');
        }
        else{
            jQuery('#Specialize_Settings').css( 'cursor', 's-resize' ).attr('src', 'modules/imaging/graph/images/imaging-add.png');
        }
    };

    fn_Specialize_Settings()
    fn_General_Settings()
    fn_User_Account()
    fn_Regional_Settings()
    fn_Out_Of_Box_Experience()
    fn_Partition_Settings()
    fn_Administrators_Account()
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
                                        _T('Account Operators','imaging'),
                                        _T('Administrators','imaging'),
                                        _T('Backup Operators','imaging'),
                                        _T('Crypto Operators','imaging'),
                                        _T('DCOM Users','imaging'),
                                        _T('Guests','imaging'),
                                        _T('IUsers','imaging'),
                                        _T('Network Configuration Operators','imaging'),
                                        _T('Perf Logging Users','imaging'),
                                        _T('Perf Monitoring Users','imaging'),
                                        _T('Power Users','imaging'),
                                        _T('Print Operators','imaging'),
                                        _T('Remote Desktop Users','imaging'),
                                        _T('Replicator','imaging'),
                                        _T('System Operators','imaging'),
                                        _T('Users','imaging'));
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
                                        _T('Never check for updates','imaging'),
                                        _T('Check for updates but choose to download and install','imaging'),
                                        _T('Download updates but choose when to install','imaging'),
                                        _T('Install updates automatically','imaging'));                        
                                
        $ProtectComputerTabElement = array( 
                                        _T('Recommended settings','imaging'),
                                        _T('Install selective updates','imaging'),
                                        _T('Do not install selective updates','imaging'));                        
                                
        
        $yes_no=        array(
                                        _T('Yes','imaging'),
                                        _T('No','imaging'));
                                
        $truefalse = array(
                                        'true',
                                        'false');                        
                                
        $suite2_5 = array(
                                        '2','3','4','5');
        $suite0_5 = array(
                                        '0','1','2','3','4','5');
                                        
        $suite0_24 = array(             '0','1','2','3','4','5','6','7','8','9','10','11','12',
                                        '13','14','15','16','17','18','19','20','21','22','23','24');
         
        $EnableDisabled = array(
                                        _T('Enable','imaging'),
                                        _T('Disabled','imaging'));

                                        
//Windows 8
        $InfoBule_CEIPEnabled=
                        _T('CEIPEnabled indicates whether the Windows Customer Experience Improvement Program (CEIP) is enabled','imaging').
                        "\n".
                        _T('If the Microsoft-Windows-SQMAPI component is enabled, it collects and sends data to Microsoft about Windows usage','imaging').
                        "\n".
                        _T('Participation in this program is voluntary, and the results are recorded to implement improvements for future releases','imaging').
                        "\n".
                        _T('enabled ','imaging').
                        ' : '.
                        _T('Specifies that Windows CEIP is not enabled','imaging').
                        "\n".
                        _T('Disabled','imaging').
                        ' : '.
                        _T('Specifies that Windows CEIP is enabled','imaging');

        $InfoBule_SystemDefaultBackgroundColor=
                        _T('SystemDefaultBackgroundColor specifies the system default Windows background color scheme appearing on first boot, and on LogonUI if no user is selected','imaging');

        $InfoBule_UILanguage=
                        _T('Specifies the default system language to display user interface (UI) items (such as menus, dialog boxes, and help files)','imaging');

        $InfoBule_TimeZone= 
                        _T('Specifies the time zone of the computer. The time zones that are specified in Windows System Image Manager are not localized','imaging');
        
        $InfoBule_Installation_Notes=
                        _T("Meta Information xml", "imaging");
        
        $InfoBule_General_Settings = 
                        _T("Configure General Settings", "imaging");                        
                                
        $InfoBule_ProductKey=
                        _T('Specifies the key used to activate Windows','imaging').
                        "\n".
                        _T('IMPORTANT','imaging').
                        "\n".
                        _T('Entering an invalid product key in the answer file will cause Windows Setup to fail','imaging');                        
                                
        $InfoBule_AcceptEULA=
                        _T('Specifies whether to automatically accept the Microsoft Software License Terms','imaging').
                        "\n".
                        _T('Yes','imaging').
                        " : ".
                        _T('Specifies that the license terms are automatically accepted without being displayed to the end user','imaging').
                        "\n".
                        _T('No','imaging').
                        " : ".
                        _T('Prompts the user to accept the license terms before proceeding with Windows Setup','imaging');                        
                                
                                
        $InfoBule_SkipAutoActivation=  
                        _T("Specifies whether Windows attempts to automatically activate",'imaging').
                        "\n".
                        _T("For automatic activation to complete, a valid Windows product key is required",'imaging').
                        "\n".
                        _T("true",'imaging').
                        " : ".
                        _T("Specifies that Windows does not attempt to automatically activate",'imaging').
                        "\n".
                        _T("false",'imaging').
                        " : ".
                        _T("Specifies that Windows attempts to automatically activate",'imaging');                        
                                
        $InfoBule_SkipRearm= 
                        _T('Specifies whether to run the Windows Software Licensing Rearm program','imaging').
                        "\n".
                        _T('Yes','imaging').
                        " : " .
                        _T('Specifies that the computer is not rearmed and the computer will not be restored to its original, out-of-box state. All activation-related licensing and registry data will remain and will not be reset. Similarly, any grace period timers is not reset.','imaging').
                        "\n".
                        _T('No','imaging').
                        " : "
                        ._T('Specifies that the computer is rearmed, restoring the computer to the original, out-of-box state. All activation-related licensing and registry data is removed or reset, and any grace period timers are also reset.','imaging');                        
                                
        $InfoBule_SetupUILanguage=
                        _T('SetupUILanguage defines the language to use in Windows Setup and Windows Deployment Services','imaging');                        
                                
        $Infobule_ComputerName= 
                        _T("Specifies the computer name used to access the computer from the network",'imaging');

        $InfoBule_OrginazationName= 
                        _T("Specifies the name of the organization that owns the computer",'imaging');                        
   
        $InfoBule_UserLocale=
                        _T('Specifies the per-user settings used for formatting dates, times, currency, and numbers in a Windows installation','imaging');                        
                                
        $Infobule_InputLocale=    
                        _T('Specifies the input language and keyboard layout for a Windows installation', "imaging");                        
                                
        $Infobule_Partition_Settings=
                        _T("Configure Partition Settings", "imaging");                        
                                
        $InfoBule_Label=
                        _T('Main Partition Label','imaging');
                                
        $InfoBule_User_Account = 
                        _T("Configure User Account", "imaging");                        
                                
        $InfoBule_Updates=
                        _T('CommandLine reg','imaging');
        $InfoBule_Out_Of_Box_Experience=
                        _T("OOBE specifies the out-of-box experience for the end user", "imaging").
                        "\n".
                        _T("These settings specify whether to do the following", "imaging").
                        " : \n".
                        _T("   - Hide the Microsoft Software License Terms page in Windows Welcome", "imaging").
                        "\n".
                        _T("   - Skip Windows Welcome, also known as Machine OOBE", "imaging").
                        "\n".
                        _T("   - Skip Welcome Center, also known as Per User OOBE", "imaging").
                        "\n".
                        _T("It also specifies the following", "imaging").
                        "\n".
                        _T("   - The network type", "imaging").
                        "\n".
                        _T("   - What type of computer protection is in place", "imaging");

        $InfoBule_NetworkLocation=
                        _T('Specifies the location of the network if the computer is connected to a network when a user first logs on','imaging').
                        "\n".
                        _T('Home','imaging').
                        " : ".
                        _T('Specifies a private home network','imaging').
                        "\n".
                        _T('Work','imaging').
                        " : ".
                        _T('Specifies a private office network','imaging').
                        "\n".
                        _T('Other','imaging').
                        " : ".
                        _T('Specifies neither a home or work network','imaging').
                        "\n".
                        _T('Network discovery is disabled by default on this network type','imaging');

        $InfoBule_ProtectComputer= 
                        _T('Specifies whether to display the Help protect your computer automatically page of Windows Welcome to the user','imaging').
                        "\n".
                        _T('There is no default value. If a value is not set, the page opens during Windows Welcome','imaging').
                        "\n -1 : ".    
                        _T('Specifies the recommended level of protection for your computer','imaging').
                        "\n -2 : ".
                        _T('Specifies that only updates are installed','imaging').
                        "\n -3 : ".
                        _T('Specifies that automatic protection is disabled','imaging');

        $InfoBule_HideEULA= 
                        _T('Specifies whether to hide the Microsoft® Software License Terms page of Windows® Welcome','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that the Microsoft Software License Terms page of Windows Welcome is not displayed','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that the Microsoft Software License Terms page of Windows Welcome is displayed','imaging');                

        $InfoBule_DaylightSettings= 
                        _T('Specifies whether the time on the computer is set to daylight saving time','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that the time on the computer is not reset to daylight saving time','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that the time on the computer is reset to daylight saving time','imaging');  

        $Infobule_HideWireless=
                        _T('Specifies whether to hide the Join Wireless Network screen that appears during Windows® Welcome','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Hides the Join Wireless Network screen during Windows Welcome','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Does not hide the Join Wireless Network screen during Windows Welcome','imaging');

        $InfoBule_MachineOOBE= 
                        _T('Specifies whether to skip Windows Welcome','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that Windows Welcome is skipped','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that Windows Welcome is shown','imaging').
                        "\n".
                        _T('warning','imaging').
                        "\n".
                        _T('If you enable SkipMachineOOBE, any settings specified for ProtectYourPC and NetworkLocation in your answer file are ignored','imaging');

        $InfoBule_UserOOBE=
                        _T('Specifies whether to skip Welcome Center. This can be used only for testing prior to shipment','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that Welcome Center is skipped','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that Welcome Center is shown','imaging');
                        
        $InfoBule_ControlPanelView= 
                        _T('CommandLine reg Set the Control Panel View to Small Icons','imaging');

        $InfoBule_ControlPanelIconSize= 
                        _T('CommandLine reg ControlPanel AllItemsIconView','imaging');
        
        $InfoBule_WipeDisk= 
                        _T('Specifies whether to erase all partitions on the hard disk before adding additional configurations to the disk','imaging').
                        "\n".   
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that the disk is erased','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that the disk is not erased','imaging');

        $InfoBule_InstallDisk=
                        _T('Specifies the disk ID of the disk to which the image is to be installed','imaging').
                        "\n".
                        _T('This sequence starts with 0','imaging').
                        "\n".
                        _T('If you are installing to a computer with a single disk, you must specify 0','imaging').
                        "\n".
                        _T('Disk_ID is an integer','imaging');

        $InfoBule_Format=
                        _T('Specifies whether to erase the partition, and which file system to apply to the partition','imaging').
                        "\n".
                        _T('NTFS','imaging').
                        " : ".
                        _T('Formats the partition for the NTFS file system','imaging').
                        "\n".
                        _T('FAT32','imaging').
                        " : ".
                        _T('Formats the partition for the File Allocation Table (FAT) file system','imaging');

        $InfoBule_DriveLetter=  
                        _T('Specifies the drive letter to apply to a partition. Drive_letter is an uppercase letter, C through Z','imaging');
 
        $InfoBule_PartitionOrder=
                        _T('Specifies the order in which the ModifyPartition command is to be run at first logon','imaging').
                        "\n".
                        _T('Synchronous commands start in the order specified in the unattended installation answer file, and each command must finish before the next command starts','imaging').
                        "\n".
                        _T('Synchronous commands are always run before asynchronous commands in the same configuration pass','imaging');
                        
        $InfoBule_Administrators_Account= 
                        _T("Configure Administrators Account", "imaging");
                        
        $InfoBule_PasswordAdmin=
                        _T('Specifies the administrator password of the computer and whether it is hidden in the unattended installation answer file','imaging');
                        
        $InfoBule_Group=
                        _T('Specifies the name of an existing local security group to which a new LocalAccount will be added during installation','imaging');              
                        
                        
        $InfoBule_Description=
                        _T('Specifies a LocalAccount','imaging');
        
        $InfoBule_Password= 
                        _T('Specifies the password for a LocalAccount and whether the password is hidden in the unattended installation answer file','imaging');
        
        $InfoBule_FullName=
                        _T('Specifies the name of the end user. User_name is a string with a maximum length of 63 characters','imaging');
        
        $InfoBule_Autologon=
                        _T('Specifies the account to use to log on to the computer automatically. Autologon credentials are deleted from the unattended installation answer file after Windows Setup is complete','imaging').
                        "\n".
                        _T('Important','imaging').
                        "\n".
                        _T('Make sure Autologon is disabled on computers that are delivered to customers','imaging').
                        "\n".
                        _T('By default, the built-in administrator account is disabled in all default, clean installations','imaging');

        $InfoBule_EnableUAC= 
                        _T('Specifies whether Windows® User Account Controls (UAC) notifies the user when programs try to make changes to the computer. UAC was formerly known as Limited User Account (LUA)','imaging').
                        "\n".
                        _T('true','imaging').
                        " : ".
                        _T('Windows notifies the user when programs try to make changes to the computer','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Windows does not notify the user when programs try to install software or make changes to the computer','imaging').
                        "\n\n".
                        _T('To provide better protection for computers connected to any kind of network (such as the Internet, a home network, or an organization network), the Windows operating system enables Windows Firewall on all network connections by default','imaging');

        $InfoBule_EnableFirewall= 
                        _T('Windows Firewall is a stateful host firewall that discards unsolicited incoming traffic, providing a level of protection for computers against malicious users or programs','imaging').
                        "\n".
                        _T('To provide better protection for computers connected to any kind of network (such as the Internet, a home network, or an organization network), the Windows operating system enables Windows Firewall on all network connections by default','imaging').
                        "\n".   
                        _T('true','imaging').
                        " : ".
                        _T('Enables Windows Firewall for Windows PE','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Disables Windows Firewall for Windows PE','imaging');

        $InfoBule_CopyProfile=
                        _T('Use the following steps to use CopyProfile to set customized user profiles','imaging').
                        " : ".
                        "\n".
                        _T('Log on as a user whose profile you can customize (for example, the built-in-administrator account)','imaging').
                        "\n".
                        _T('Customize the desired user profile settings','imaging').
                        "\n".
                        _T('Set CopyProfile to true in the Unattend.xml file that you will use with Sysprep in the next step','imaging').
                        "\n".
                        _T('Run sysprep /generalize /unattend:unattend.xml to copy the customized user profile settings over the default user profile','imaging').
                        "\n".   
                        _T('true','imaging').
                        " : ".
                        _T('Changes the default user profile with customizations made . You must set this value to true only if you have made customizations to the logged-on user profile that you need to apply to all new users','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Does not change the default user profile','imaging');

        $InfoBule_ShowWindowsLive= 
                        _T('ShowWindowsLive specifies whether to display a link to Windows Live on the Start menu','imaging').
                        "\n".  
                        _T('If the Windows Live shortcut has been removed from the Start menu, this setting cannot be used to put it back on the Start menu','imaging').
                        "\n".   
                        _T('true','imaging').
                        " : ".
                        _T('Specifies that a link to Windows Live is displayed on the Start menu','imaging').
                        "\n".
                        _T('false','imaging').
                        " : ".
                        _T('Specifies that a link to Windows Live is not displayed on the Start menu','imaging');

        $InfoBule_ExtendOSPartition=
                        _T("Specifies whether to extend the partition to fill the entire hard disk", "imaging");
                        
                        
                        
        $InfoBule_backgroundWin8=
                        _T("In Windows 8, SystemDefaultBackgroundColor must be a value from 0 to 24, as shown in the following image, which represents the index of the color scheme as viewed in the SystemSettings", "imaging");
                        

        $InfoBule_backgroundWin81=
                        _T("In Windows 8.1, SystemDefaultBackgroundColor must be a value from 0 to 24 which represents the index of the color scheme as viewed in the out-of-box experience (OOBE) phase. The colors are indexed in the same manner as Windows 8 colors, from left to right. Samples of the color choices are shown in the following image", "imaging");
                        
        $InfoBule_showxml=
                        _T("Show file XML AWFG", "imaging");   
                        
    class  TrFormElementcollapse extends TrFormElement{
        function TrFormElementcollapse( $tpl, $extraInfo = array()){
            parent::TrFormElement($desc, $tpl, $extraInfo);
        }
        
        function display($arrParam = array()) {
            if (empty($arrParam))
                $arrParam = $this->options;
            if (!isset($this->cssErrorName))
                $this->cssErrorName = isset($this->template->name) ? $this->template->name : "";
            printf('<tr');
            if ($this->class !== null)
                printf(' class="%s"', $this->class);
    //         if ($this->style !== null)
    //             printf(' style="%s"', $this->style);
            printf('><td colspan="2"');
            if ($this->style !== null){
                printf(' style="%s" ', $this->style);
            }
            printf('>');
            $this->template->display($arrParam);
            print "</td></tr>";
        }
        
    }
   
    
    function attribut($val,$val1=null){
        if(isset($val1)){
            $valeur[0]=$val;
            $valeur[1]=$val1;
        }
        else{
            $valeur=explode ( "=", $val );
        }
        if(isset($valeur[1])){
            $valeur[0] = trim ( $valeur[0], "\"' " );
            $valeur[1] = trim ( $valeur[1], "\"' " );
            if($valeur[1]!="")
                return $valeur[0]."="."'$valeur[1]'";
            else
                return "";
        }
        return "";
    }
    
    function add_attribut($attribut){
        $valattribut="";
        if (isset($attribut)) {
            if (is_array($attribut)){
                foreach ($attribut as $k => $v) {
                    if (! is_int ( $k )){
                        $valattribut.=' '.$k.'="'. $v . '"';
                    }
                    elseif ($v != "" ){
                        $valattribut.= ' '. $v;
                    }
                }
            }
        }elseif ($attribut != "") {
            $valattribut.=' id="'. $id . '"';
        } 
        return $valattribut;
    }

    function add_element($element,$name="",$id="",$attribut="",$value="",$stylebalise="xhtml"){
        $elementhtml.="<".$element;
        if (isset($name) && $name!="") {
            $elementhtml.=' name="'. $name . '"';
        }
        if (isset($id) && $id != "") {
            $valid="";
            if (is_array($id)){
                $id=implode ( " " , $id );
            }  
            $elementhtml.=' id="'. $id . '"';
        }
        if ($attribut != "") {
            $elementhtml.= ' '. add_attribut($attribut);
        }
        if(!isset($value)){
            $value="";
        }
        if(isset($stylebalise) && $stylebalise=="xhtml"){
            $elementhtml.=">".$value."</".$element.">";
        }
        else{
            $elementhtml.=">";
        }
        return $elementhtml;
    }   
/**
 * simple input template
 */
class InputTplTitle extends InputTpl {
    var $title;
    function InputTplTitle($name,$title=null,$regexp = '/.+/'){
        $this->title=$title;
        parent::InputTpl($name,$regexp);
    }

    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if ($arrParam == '') {
            $arrParam = $_POST[$this->name];
        }
        if (!isset($arrParam['disabled'])) {
            $arrParam['disabled'] = '';
        }
        if (!isset($arrParam['placeholder'])) {
            $arrParam['placeholder'] = '';
        }

        $attrs = array(
            attribut('type',$this->fieldType),
            attribut('size',$this->size),
            attribut('value',$arrParam["value"]),
            attribut('placeholder="' . $arrParam["placeholder"].'"'),
            attribut($arrParam["disabled"]),
            attribut("title",$this->title),
            attribut( isset($arrParam["required"]) ? ' rel="required" ' : ''),
            attribut( isset($arrParam["required"]) ? ' required="required" ' : ''), 
            attribut("data-regexp",$this->regexp),
            attribut("maxlength",$arrParam["maxlength"]),
            attribut("title",$this->title),           
            attribut('autocomplete="off"')
        );
      
        echo add_element('span',
                "" ,
                "container_input_$this->name",
                "" ,
                add_element('input', $this->name, $this->name,$attrs, "", "html" ),
                "xhtml" );
        if (isset($arrParam["onchange"])) {
            print '<script type="text/javascript">';
            print 'jQuery(\'#' . $this->name . '\').change( function() {' . $arrParam["onchange"] . '});';
            print '</script>';
        }
    }
}

class SelectItemtitle extends SelectItem {
    var $title;
    /**
     * constructor
     */
    function SelectItemtitle($idElt, $title=null, $jsFunc = null, $style = null) {
        $this->title=$title;
        parent::SelectItem($idElt, $jsFunc, $style);
    }
    function to_string($paramArray = null) {
        $ret = "<select";
        if ($this->title){
            $ret .= " title=\"" . $this->title . "\"";
        }
        if ($this->style) {
            $ret .= " class=\"" . $this->style . "\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"" . $this->jsFunc . "(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        $ret .= isset($paramArray["required"]) ? ' rel="required"' : '';
        $ret .= " name=\"" . $this->name . "\" id=\"" . $this->id . "\">\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        return $ret;
    }
}

 /**
 * class add icone clikable as a HtmlElement
 * click launch function fn_"id_element"
 */
class IconeElement extends HtmlElement {
    function IconeElement($id, $src, $alt="", $title="", $params = array()) {
        $this->id = $id;
        $this->src = $src;
        $this->alt = $alt;
        $this->params = $params;
        $this->title = $title;
        $this->style= "";
    }
    function setstyle($sty){
        $this->style=$sty;
    }
    function display($arrParam = array()) {
        echo '<img src="'.$this->src.'" id="'.$this->id.'" ';
        echo ($this->alt != "") ? "alt='$this->alt'" : "alt='image' ";
        echo ($this->title != "") ? "title='$this->title' " : " ";
        if( $this->style != "")
            echo " style='position:relative; top: 3px;cursor: s-resize;' />";
        else
            echo " style='".$this->style."' />";
                      echo "<script type='text/javascript'>
                        jQuery('#".$this->id."').click(function(){fn_".$this->id."()});
                        </script>\n";
    }
}
class Iconereply extends IconeElement {
    function Iconereply($id,$title){
        parent::IconeElement($id,'modules/imaging/graph/images/imaging-add.png',"",$title);
    }
}
/*
class buttonTpl extends AbstractTpl {
    var $class = '';
    var $cssClass = 'btn btn-small';

    function buttonTpl($id, $value, $class='', $infobulle='') {
        $this->id = $id;
        $this->value = $value;
        $this->class = $class;
        $this->infobulle = $infobulle;
    }

    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam) {      
        if (isset($this->id,$this->value))
            printf('<input id="%s" title= "%s" type="button" value="%s" class="%s %s" />',
                    $this->id,
                    $this->infobulle,
                    $this->value,
                    $this->cssClass,
                    $this->class);
    }
}*/



class buttonTpl extends HtmlElement {
    var $class = '';
    var $cssClass = 'btn btn-small';

    function buttonTpl($id, $value, $class='', $infobulle='', $params = array()) {
        $this->id = $id;
        $this->value = $value;
        $this->class = $class;
        $this->infobulle = $infobulle;
        $this->params = $params;
        $this->style='';
    }
    
    function setstyle($sty){
        $this->style=$sty;
    }
    
    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam = array()) {      
        if (isset($this->id,$this->value))
            printf('<span style="color : red;" id="msg_%s">title missing</span><br><input id="%s" title="%s" type="button" value="%s" class="%s %s" />',
                    $this->id,$this->id,
                    $this->infobulle,
                    $this->value,
                    $this->cssClass,
                    $this->class);
    }
}

class SpanElementtitle extends HtmlElement {

    function SpanElementtitle($content, $class = Null,$title=Null,$id=null) {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
        $this->title = $title;
        $this->id=$id;
    }

    function display($arrParam = array()) {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<span%s id="%s" title="%s" >%s</span>', $class, $this->id, $this->title, $this->content);
    }
}

?>
