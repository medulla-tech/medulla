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

function existAclAttr($attr) {
    global $aclArray;
    foreach ($aclArray as $items) {
        if (array_key_exists($attr,$items)) {
            return true;
        }
    }
    return false;
}

/**
 * return wich module correspond an attribute
 */
function getAclAttrModule($attr) {
    global $aclArray;
    foreach ($aclArray as $key=>$items) {
        if (array_key_exists($attr,$items)) {
            return $key;
        }
    }
    return false;
}

function getAclAttr($attr) {
    if ($_SESSION["login"]=="root") {
        return "rw";
    } else { 
        return $_SESSION["aclattr"][$attr];
    }
}

function hasCorrectAcl($module,$submod,$action) {
    global $noAclArray;
    if (isset($noAclArray[$module][$submod][$action]) && 
        ($noAclArray[$module][$submod][$action] == 1)) {
        return true;
    }
    if ($_SESSION["login"]=="root") {return true;}
    if (isset($_SESSION["acl"][$module][$submod][$action]["right"])) {return true;}
    return false;
}

function hasCorrectTabAcl($module, $submod, $action, $tab) {
    return (($_SESSION["login"] == "root")
            || (isset($_SESSION["acltab"][$module][$submod][$action][$tab]["right"])));
}

function hasCorrectModuleAcl($module) {
  global $redirArray;
  /* if you are root */
  if ($_SESSION["login"]=="root") {return true;}
  /* if you have an ACL set for this module */
  if (isset($_SESSION["acl"][$module])) {return true;}
  /* FIXME: the next line may be wrong */
  if (empty($redirArray[$module])) { return true; }
  return false;
}

function getDefaultPage() {
    $base = "";
    if (isset($_SESSION["acl"])) {
        foreach(array_keys($_SESSION["acl"]) as $key => $value) {
            if ($value != "") {
                $base = $value;
                break;
            }
        }
    }

    $submod = "";
    if ((strlen($base)) && (isset($_SESSION["acl"][$base]))) {
        foreach(array_keys($_SESSION["acl"][$base]) as $key => $value) {
            if ($value != "") {
                $submod = $value;
                break;
            }
        }
    }

    $action = "";
    if ((strlen($submod)) && (isset($_SESSION["acl"][$base][$submod]))) {
        foreach(array_keys($_SESSION["acl"][$base][$submod]) as $key => $value) {
            if ($value != "") {
                $action = $value;
                break;
            }
        }
    }

    if (!$base) return "index.php?error=".urlencode(_("You do not have required rights"));

    return "main.php?module=$base&submod=$submod&action=$action";
}

?>