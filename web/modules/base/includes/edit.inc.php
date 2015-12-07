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
?>
<?php

/**
 *  convert an aclString to an aclArray
 */
function createAclArray($aclString) {
    $acl = "";
    $aclattr = "";
    if (strpos($aclString, '/') === False) {
        $acl = $aclString;
    } else {
        list($acl, $aclattr) = split('/', $aclString);
    }

    $retacl = array();
    $retacltab = array();
    $retaclattr = array();

    /* get pages ACL */
    $arrayMod = preg_split(':', $acl);
    foreach($arrayMod as $items) {
        if (substr_count($items, "#") == 2) {
            list($mod, $submod, $action) = split('#', $items);
            $retacl[$mod][$submod][$action]["right"] = "on";
        } else if (substr_count($items, "#") == 3) {
            list($mod, $submod, $action, $tab) = split('#', $items);
            $retacltab[$mod][$submod][$action][$tab]["right"] = "on";
        }
    }

    /* get attribute ACL */
    if (strlen($aclattr)) {
        $arrayAttr=split(':',$aclattr);
        foreach($arrayAttr as $items) {
            if (!empty($items)) {
                list($attrName,$value) = split('=',$items);
                $retaclattr[$attrName]=$value;
            }
        }
    }

    return array($retacl, $retacltab, $retaclattr);
}

/**
 * convert an acl array to an acl String
 */
function createAclString($arrAcl, $arrAclTab, $arrAclAttr) {
    $res = "";
    //fetch all modules in $arrAcl
    foreach ($arrAcl as $modKey => $valKey ){
        if (isset($arrAcl[$modKey]["right"])) {
            $res.=":$modKey";
        }
        //fetch all submodules in $valKey
        else foreach ($valKey as $submodKey => $submodvalKey ){
            if (isset($arrAcl[$modKey][$submodKey]["right"])) {
                $res.=":$modKey#$submodKey";
            }

            //fetch all action in
            else foreach ($submodvalKey as $actionKey => $actionvalKey) {
                if (isset($arrAcl[$modKey][$submodKey][$actionKey]["right"])) {
                    $res.=":$modKey#$submodKey#$actionKey";
                }
            }
        }
    }
    foreach($arrAclTab as $modKey => $valKey ){
        foreach ($valKey as $submodKey => $submodvalKey ){
            foreach ($submodvalKey as $actionKey => $actionvalKey) {
                /* Only set tabs access if the corresponding page access is
                   set too */
                if (isset($arrAcl[$modKey][$submodKey][$actionKey])) {
                    foreach ($actionvalKey as $tabKey => $tabValue) {
                        if (isset($arrAclTab[$modKey][$submodKey][$actionKey][$tabKey]["right"])) {
                            $res.=":$modKey#$submodKey#$actionKey#$tabKey";
                        }
                    }
                }
            }
        }
    }


    if ($res=='') { $res = ':'; }

    //partit attribut
    $resAttr='';
    foreach ($arrAclAttr as $attr => $value) {
        if (($value=="ro")or($value=="rw")) {
            $resAttr.=":$attr=$value";
        }
    }
    $combineRes = $res."/".$resAttr;
    return $combineRes;
}

/**
 * Set the current interface mode.
 * A cookie that expires in 30 days is used to keep user interface mode between
 * two MMC sessions.
 *
 * @param $value 0 to set standard mode, 1 to set expert mode
 */
function setExpertMode($value) {
    global $conf;
    setcookie("expertMode", $value, time() + 3600 * 24 * 30, $conf["global"]["root"]);
}

/**
 * Returns 0 if the interface is in standard mode, or 1 if in expert mode.
 */
function isExpertMode() {
    $ret = 0;
    if (isset($_COOKIE["expertMode"])) {
        $ret = $_COOKIE["expertMode"];
    }
    return $ret;
}

function displayExpertCss() {
    if (isExpertMode()) {
        print ' style="display: inline;"';
    } else {
        print ' style="display: none;"';
    }
}
?>
