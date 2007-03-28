<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

require_once("ModulesGenerator.php");

/**
 * return an array of all subdirs in a dir
 *
 * @param $dir directory usually "modules/"
 * @return an array of String with a list of dirs
 */
function fetchModulesList($dir) {
    $ret = array();
    $registerList = array();
    if (is_dir($dir)) {
        if ($dh = opendir($dir)) {
            while (($file = readdir($dh)) !== false) {
                $support = array_search($file,$_SESSION["supportModList"]) !== false;
                $aclright = hasCorrectModuleAcl($file);
                if (file_exists("$dir$file/infoPackage.inc.php") && $support && $aclright) {
                    $ret[] = "$dir$file";
                    $registerList[] = "$file";
                }
            }
            closedir($dh);
        }
    }
    sort($ret);
    sort($registerList);
    /* register modulesList in $_SESSION */
    $_SESSION["modulesList"]=$registerList;
    return $ret;
}

/**
 *	get all .ini file
 * 	in	/etc/lmc/ but lmc-agent.ini
 */
function fetchIniFile() {
    global $conf;
    $INI = "/etc/lmc/lmc.ini";
    $conf = array();
    if (is_readable($INI)) {
        $conf = array_merge_recursive(parse_ini_file($INI, TRUE),$conf);
    } else {
        print "LMC: Can't read $INI configuration file. Please check your installation.";
	exit();
    }
}


/**
 * include navbar module
 * @param $dirA directory array returned by fetchModulesList
 */
function includeNavbarModule($dirA) {
	foreach ($dirA as $path) {
            if (file_exists("$path/localNavbar.php")) {
                include("$path/localNavbar.php");
            }
        }
}

/**
 * include infoPackage.inc.php from directory
 * @param $dirA directory array returned by fetchModulesList
 */
function includeInfoPackage($dirA) {
foreach ($dirA as $path) {
	if (file_exists("$path/infoPackage.inc.php")) {
			   require_once("$path/infoPackage.inc.php");
			}
	       }

    $LMCApp =& LMCApp::getInstance();
    $LMCApp->process();
}


function insert_without_delete($arr,$ind,$value) {
    if (isset($arr[$ind])) {
        return insert_without_delete($arr,$ind+1,$value);
    } else {
        $arr[$ind] = $value;
        return $arr;
    }
}

function getSorted($objlist) {
    $prio = array();
   foreach ($objlist as $obj) {
            $prio = insert_without_delete($prio,$obj->getPriority(),$obj);
    }

    ksort($prio);
    return $prio;
}

function autoGenerateNavbar() {
    $LMCApp =& LMCApp::getInstance();

    $prio = array();

    foreach ($LMCApp->getModules() as $mod) {
        foreach ($mod->getSubmodules() as $submod) {
            $prio = insert_without_delete($prio,$submod->getPriority(),$submod);
        }
    }

    ksort($prio);

    foreach ($prio as $submod) {
        $submod->generateNavbar();
    }
}

/**
 * include publicFunc.php
 * @param $dirA directory array returned by fetchModulesList
 */
function includePublicFunc($dirA) {
    /* We use a global variable to check if the file has not been already included */
    if (!isset($GLOBALS["included"])) $GLOBALS["included"] = array();
        foreach ($dirA as $path) {
            $path = str_replace("//", "/", $path);
            if (file_exists("$path/includes/publicFunc.php") && ! in_array("$path/includes/publicFunc.php", $GLOBALS["included"])) {
            array_push($GLOBALS["included"], "$path/includes/publicFunc.php");
            include("$path/includes/publicFunc.php");
            }
    }
}

/**
 * include localCss from directory /!\ deprecated
 * @param $dirA directory array returned by fetchModulesList
 */
function includeLocalCss($dirA) {
foreach ($dirA as $path) {
	if (file_exists("$path/localCss.php")) {
			   include("$path/localCss.php");
			   print"\n";
			}
	       }
}

/**
 * @param $modules modules like base or samba
 * @param $submod sub modules like "users"
 * @param $action action like index or add
 * @return if action require noheader send
 */
function isNoHeader($pModules,$pSubmod,$pAction) {
    $LMCApp =&LMCApp::getInstance();
    $mod = $LMCApp->getModule($pModules);

    $submodo = $mod->_submod[$pSubmod];
    $actiono = $submodo->_pages[$pAction];
    return ($actiono->_options["noHeader"]||$actiono->_options["AJAX"]);
}

/**
 * call all plugin function if possible
 * $function, function name
 * $paramArr, array of parameters
 *
 * this function will try to call all _$plugins_$functionName function
 */
function callPluginFunction($function,$paramArr = null) {
  $list=$_SESSION["modulesList"];

  $LMCApp =& LMCApp::getInstance();
  foreach(getSorted($LMCApp->getModules()) as $key => $mod) { //fetch and order plugin
        if (array_search($mod->getName(),$list)!==FALSE){
            $ordered_list[] = $mod->getName();
        }
  }

  $list = $ordered_list; //set $ordered_list as $list;

  // If the user try to change his/her password, we do it for each available
  // module, and we bypass all ACL check
  if (($function == "changeUserPasswd")||($function == "baseEdit")) {
      /* Change password for all modules, even those where the user has no right. */
      $list = $_SESSION["supportModList"];
      global $conf;
      foreach($list as $module) {
          if (!function_exists("_" . $module . "_" . "changeUserPasswd")) includePublicFunc(array($conf["global"]["rootfsmodules"] . "/$module"));
      }
  }

  $result = array();

  foreach($list as $item) {

    $functionName="_".$item."_".$function;

    if(function_exists($functionName)) {
      $result[$item] =  call_user_func_array($functionName,$paramArr);
    }
    else {
      // print "Call : \"".$functionName."\" not exist<br />";
    }
  }

  return $result;

}


/**
 * render template view in template corresponding module
 * ex: module samba $view = add
 * render /modules/samba/views/add.tpl.php
 */
function renderTPL($view,$module = null) {
    if (!$module) {
        $module = $_GET["module"];
    }

    $template = "modules/$module/views/$view.tpl.php";

    if (file_exists($template)) {
        global $__TPLref;
        extract($__TPLref);
        //print_r($__TPLref);

        //print_r($users);
        require($template);
    } else {
        echo "<b>template render error Cannot find file \"$template\"</b>";

    }
}



    /**
     * some functions for template, render etc...
     */

    /**
     * array of value for template
     */
    $__TPLref = array();

    function setVar($name, $value) {
        global $__TPLref;
        $__TPLref[$name]=$value;
    }

    function getVar($name) {
        global $__TPLref;
        return $__TPLref[$name];
    }

    function eT($name) {
        global $__TPLref;
        echo $__TPLref[$name];
    }

    function redirectTo($url) {
        header('Location: '.$url);
    }

/**
 * list possible locale
 */
function list_system_locales($dir){
   if(!$_SESSION['__locale']) {
   $ret = array();
   $ret[] = "C";
   if (is_dir($dir)) {
	   if ($dh = opendir($dir)) {
	       while (($file = readdir($dh)) !== false) {
                        if (file_exists("$dir/$file/LC_MESSAGES/base.mo")) {
                            $ret[]=$file;
                            }
			}
	       }
	       closedir($dh);
    }
    $_SESSION['__locale'] = $ret;
    }
    return $_SESSION['__locale'];
}

?>
