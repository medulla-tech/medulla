<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

global $conf;
require("modules/base/includes/users.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

class TrAclFormElement extends FormElement{
    var $template;
    var $desc;
    var $cssErrorName;

    function TrAclFormElement($desc,$tpl=NULL,$rownum="",$arrparam = array(),$extraInfo = array()) {
        $this->desc=$desc;
        $this->template=&$tpl;
        $this->rowNum=$rownum;
        $this->arrparam=$arrparam;
        foreach ($extraInfo as $key => $value) {
            $this->key = $value;
        }
        $this->tab = False;
    }

    function setTab(){
        $this->tab=True;
    }
    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if (empty($arrParam)) $arrParam = $this->options;
        if (!isset($this->cssErrorName)) $this->cssErrorName = $this->template->name;
        if ($this->rowNum%2) {
            print '
            <tr class="alternate"><td width="50%" ';
        }
        else {
            print '<tr><td ';
        }

        print displayErrorCss($this->cssErrorName);
        print 'style = "text-align: left;">';
        if ($this->tab)
        {
            print '<dd>';
        }
        //if we got a tooltip, we show it
        if ($this->tooltip) {
            print "<a href=\"#\" class=\"tooltip\">".$this->desc."<span>".$this->tooltip."</span></a>";
        } else {
            if(!isset($this->template))
                print '<h2>'.$this->desc.'</h2>';
            else
                print $this->desc;
        }
        print '</td><td style = "text-align: left;">';
        if(isset($this->template)){
            if(!empty($this->arrparam)){
                parent::display($this->arrparam);
            }
            else{
                parent::display($arrParam);
            }
        }

        if (isset($arrParam["extra"])) {
            print "&nbsp;" . $arrParam["extra"];
        }
        print "</td></tr>
        ";

    }
}

class AclRadioTpl extends RadioTpl {

    function display($arrParam) {
        if (!isset($this->choiceVal)) {
            $this->choiceVal = $this->choices;
        }

        if (!isset($this->selected)) {
            $this->selected = $this->choiceVal[0];
        }
        $first=0;
        foreach ($this->choiceVal as $key => $value) {
            if ($first!=0)
            {
                print '<td >';
            }
            if ($this->selected == $value) {
                $selected = "checked";
            } else {
                $selected = "";
            }
            print '<input name="'.$this->name.'" value="'.$this->choiceVal[$key].'" id="'.$this->name.'" type="radio" '.$selected.'>'.$this->choices[$key];
            print "</td>";
            $first++;
        }
    }
}

$aclString = getAcl($_GET["user"]);
list($acl, $acltab, $aclattr) = createAclArray($aclString);

if (isset($_POST["buser"])) {
    foreach ($_SESSION['supportModList'] as $mod) {
        unset($acl[$mod]);
    }

    /* Set POST arrays as empty when not set */
    foreach(array("acl", "aclattr", "acltab") as $postvar) {
        if (!isset($_POST[$postvar])) {
            $_POST[$postvar] = array();
        }
    }
    foreach ($_POST["acl"] as $key => $value) {
        $acl[$key] = $value;
    }
    foreach ($_POST["acltab"] as $key => $value) {
        $acltab[$key] = $value;
    }
    foreach ($_POST["aclattr"] as $key => $value) {
        $aclattr[$key] = $value;
    }

    setAcl($_GET["user"], createAclString($acl, $acltab, $aclattr));
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(_("User ACLs successfully modified."));
    }
    $aclString = getAcl($_GET["user"]);
    list($acl, $acltab, $aclattr) = createAclArray($aclString);
} elseif (isset($_POST["bgetacl"])) {
    ob_end_clean();
    header("Pragma: ");
    header("Cache-Control: ");
    header("Content-type: text/txt");
    header('Content-Disposition: attachment; filename="'.$_GET["user"].'-acl.txt"');
    print $aclString;
    exit;
}

function createAclAttrTemplate($module_name, $aclattr, $form) {
    global $aclArray;
    $rowNum=1;

    if (!empty($aclArray[$module_name])) {
        $MMCApp =&MMCApp::getInstance();
        $base = &$MMCApp->getModule($module_name);
        $form->add(new TitleElement(_($base->getDescription())));
        // Set all radiobutton
        $str = _('Set value for all radio buttons:&nbsp;&nbsp;');
        $str .= '<a href="javascript:void(0);" onclick="checkAllRadio(\'aclattr\', \'ro\');">'._("read only").'</a>&nbsp;&nbsp;';
        $str .= '<a href="javascript:void(0);" onclick="checkAllRadio(\'aclattr\', \'rw\');">'._("read/write").'</a>&nbsp;&nbsp;';
        $str .= '<a href="javascript:void(0);" onclick="checkAllRadio(\'aclattr\', \'\');">'._("hide").'</a><br /><br />';
        $form->add(new SpanElement($str));
        $form->push(new Table());
        $form->add(new TrTitleElement(array(0=>_("Attribute description"),1=>_("read only"),2=>_("read/write"),3=>_("hide"))));
        foreach ($aclArray[$module_name] as $key => $value) {
            $rowNum++;
            $radio=new AclRadioTpl("aclattr[".$key."]");
            $radio->setValues(array("0"=>"ro","1"=>"rw","2"=>""));
            $radio->setSelected("");
            if (isset($aclattr[$key])) {
                if ($aclattr[$key]=="ro") {
                    $radio->setSelected("ro");
                } else if ($aclattr[$key]=="rw"){
                    $radio->setSelected("rw");
                }
            }
            $form->add(new TrAclFormElement(_($value), $radio, $rowNum));
        }
        $form->pop();
    }
}

function createRedirectAclTemplate($module_name, $acl, $acltab, $form) {
    global $descArray;
    global $redirArray;
    global $tabDescArray;
    global $tabAclArray;
    $key = $module_name;
    $value = $redirArray[$module_name];
    $MMCApp =&MMCApp::getInstance();
    $base = &$MMCApp->getModule($module_name);
    $form->add(new TitleElement(_($base->getDescription()) . " " . sprintf(_(" (%s module)"), $module_name)));
    foreach ($value as $subkey => $subvalue) {
        $rowNum=1;
        $submod = &$base->getSubmod($subkey);
        $form->add(new TitleElement(_($submod->getDescription()), 3));
        if (sizeof($subvalue)>1)
        {
            $form->add(new SelectElement("acl[".$module_name."][".$subkey."]", "acltab[".$module_name."][".$subkey."]"));
        }
        $form->push(new Table());
        $form->add(new TrTitleElement(array(0=>_("Web page description"),1=>_("Authorization"))));
        foreach ($subvalue as $actionkey => $actionvalue) {
            if ($descArray[$key][$subkey][$actionkey]) {
                if (isset($acl[$key][$subkey][$actionkey]["right"]) && ($acl[$key][$subkey][$actionkey]["right"]=='on')) {
                    $form->add(new TrAclFormElement(_( $descArray[$key][$subkey][$actionkey]), new CheckboxTpl("acl[".$key."][".$subkey."][".$actionkey."][right]"), $rowNum, array("value" => "checked")));
                } else {
                    $form->add(new TrAclFormElement(_($descArray[$key][$subkey][$actionkey]),  new CheckboxTpl("acl[".$key."][".$subkey."][".$actionkey."][right]"),$rowNum,array("value" => "")));
                }
            } else {
                print _("Warning no desc found in infoPackage.inc.php :").$actionkey;
            }
            $rowNum++;
            if (isset($tabAclArray[$key][$subkey][$actionkey])) {
                foreach($tabAclArray[$key][$subkey][$actionkey] as $tabkey => $tabvalue) {
                   if ($acltab[$key][$subkey][$actionkey][$tabkey]["right"]=='on') {
                        $t=new TrAclFormElement(_($tabDescArray[$key][$subkey][$actionkey][$tabkey]), new CheckboxTpl("acltab[".$key."][".$subkey."][".$actionkey."][".$tabkey."][right]"), $rowNum);
                        $t->setTab();
                        $form->add($t, array("value"=>"checked"));
                    } else {
                        $t=new TrAclFormElement(_($tabDescArray[$key][$subkey][$actionkey][$tabkey]), new CheckboxTpl("acltab[".$key."][".$subkey."][".$actionkey."][".$tabkey."][right]"), $rowNum);
                        $t->setTab();
                        $form->add($t, array("value"=>""));
                    }
                    $rowNum++;
                }
            }
        }
        $form->pop();
    }

}

$p = new PageGenerator(sprintf(_("Edit ACL of user %s"), $_GET["user"]));
$sidemenu->forceActiveItem("index");
$p->setSideMenu($sidemenu);
$p->display();

global $descArray;

$f = new ValidatingForm();
foreach ($_SESSION["modulesList"] as $key) {
    $MMCApp =&MMCApp::getInstance();
    $mod = $MMCApp->getModule($key);
    if ($mod != null) {
        $mod_name = $mod->getDescription();
        if ($redirArray[$key])
            createRedirectAclTemplate($key,$acl, $acltab,$f);
        createAclAttrTemplate($key,$aclattr,$f);
    }

}
$f->pop();
$f->addExpertButton("bgetacl", _("Download ACL string"));
$f->addValidateButton("buser");
$f->display();
?>
