<?php
/*
 * (c) 2015-2023 Siveo, http://www.siveo.net
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

if(!isset($_GET['tab']) && $_GET['action']=='unattended')
{
require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');
}
define ("DIR_SYS_PREP", "/var/lib/pulse2/imaging/postinst/sysprep");
?>

<?php
    class ajaxSelectItem extends Form  {
        function __construct($idElt,$style = null) {
            $options = array();
            $this->idElt=$idElt;
            $this->idselect="select_$idElt";
            $this->idform="form_$idElt";
            $this->idchoixform="afficheform_$idElt";
            $options["id"]=$this->idform;
            $options["method"] = "";
            parent::__construct($options);
            $this->select = new SelectItem($this->idselect, "change".$idElt, $style);
        }

        function setElements($List){
            $this->select->setElements($List);
        }

        function setElementsVal($list_val){
            $this->select->setElementsVal($list_val);
        }

        function setJsFuncParams($arrayparam){
            $this->select->setJsFuncParams($arrayparam);
        }

        function display(){
            $this->push($this->select);
            parent::display();
        }

        function end() {
            $str = parent::end();
            $str .= "
            <div id=\"$this->idchoixform\"> </div>
            <script type=\"text/javascript\">
                loadpage".$this->idselect."=function(){
                    var selectval = jQuery( '#".$this->idselect."').val()
                    jQuery( '#".$this->idchoixform."' ).load( selectval,
                        function( response, status, xhr ) {
                            if ( status == 'error' ) {
                                var msg = '"._T("form not found", 'imaging').": ';
                                alert( msg + xhr.status + ' ' + xhr.statusText );
                            }
                        });
                }
                loadpage".$this->idselect."()
                change".$this->idElt."=function(val){
                    loadpage".$this->idselect."()
                }
            </script>\n";
            return $str;
        }
    }
    $p = new PageGenerator(_T("Windows Answer File Generator", 'imaging'));
    $p->setSideMenu($sidemenu);
    $p->display();
    if (isset($_POST['bvalid'])){
        $gg = $_POST['codeToCopy'];
        $dom = new DomDocument();
        $dom->preserveWhiteSpace = FALSE;
        $dom->loadXML($gg);
        $dom->formatOutput = true;
        $t=$dom->saveXML();
        $t1 = str_replace ("\r",'',$t);
        $new = htmlspecialchars( $t1, ENT_QUOTES);
        if( ! xmlrpc_Windows_Answer_File_Generator($t,$_POST['Location']))
        {
            echo '<p style="text-align : center; color : DarkRed ; font-size : 20px;" >';
            echo _T("error create file", 'imaging').'</p>';
        }else
        {
            echo '<pre>'.$new.'</pre>';
        }
        exit(0);
    }

	if(isset($_GET['edit']))
	{
		if(isset($_SESSION['parameters']))
			unset($_SESSION['parameters']);

		$_SESSION['parameters'] = xmlrpc_getWindowsAnswerFileParameters($_GET['edit']);
		$_SESSION['parameters']['Title'] = $_GET['edit'];
	}
	else
	{
		if(isset($_SESSION['parameters']))
			unset($_SESSION['parameters']);
	}

    $span = new SpanElement(_T("Choose package source", 'imaging')." : ", "pkgs-title");
    $List=array('Windows 7','Windows 8','Windows 8-uefi', 'Windows 10','Windows 10-uefi', 'Windows 11','Windows 11-uefi');
    $list_val=[ 'modules/imaging/manage/ajaxFormWin7.php',
                'modules/imaging/manage/ajaxFormWin8.php',
                'modules/imaging/manage/ajaxFormWin8-uefi.php',
                'modules/imaging/manage/ajaxFormWin10.php',
                'modules/imaging/manage/ajaxFormWin10-uefi.php',
                'modules/imaging/manage/ajaxFormWin11.php',
                'modules/imaging/manage/ajaxFormWin11-uefi.php'];

    $combine = array_combine($List,$list_val);

    $default_value= (isset($_GET['edit'])) ? $_SESSION['parameters']['os'] : '\'Windows 7\'';
    $selectpapi = new ajaxSelectItem('unattended');
    $selectpapi->push($span);
    $selectpapi->setElements((isset($_GET['edit'])) ? [$_SESSION['parameters']['Os']] : $List);
    $selectpapi->setElementsVal((isset($_GET['edit'])) ? [$combine[$_SESSION['parameters']['Os']]] : $list_val);
    $selectpapi->setJsFuncParams([$default_value]);
    $selectpapi->display();
 ?>
