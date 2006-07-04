<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
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
/* $Id$ */
/*
 * section which
 */

/**
 * function who optimize code of html page
 * source : php.net
 */
function callback($buffer){
   $buffer = str_replace("\n", "", $buffer);
   $buffer = str_replace("\t", "", $buffer);
   $buffer = str_replace(chr(13), "", $buffer);
   $buffer = ereg_replace("<!\-\- [\/\ a-zA-Z]* \-\->", "", $buffer);
   return $buffer;
}

global $conf;

if ($conf["global"]["compress"]) {
		ob_start("callback"); //optimize weight of html code
	}
	else {
		ob_start(); //code readable
	}


require("includes/session.inc.php");
require("includes/config.inc.php");



require_once("includes/i18n.inc.php");
require("modules/base/includes/edit.inc.php");
require("includes/acl.inc.php");


//procedure d'inclusion des modules
function autoInclude() {

	global $redirArray;
        global $redirAjaxArray;
	global $conf;
	includeInfoPackage(fetchModulesList($conf["global"]["rootfsmodules"]));
        includePublicFunc(fetchModulesList($conf["global"]["rootfsmodules"]));

	if (isset($_GET["module"])) {
		$__module = $_GET["module"];
	} else { $module="default"; }

	if (isset($_GET["submod"])) {
		$__submod = $_GET["submod"];
	} else { $submod="default"; }

	if (isset($_GET["action"])) {
		$__action = $_GET["action"];
	} else { $action="default"; }


        if ((!isset($redirArray[$__module][$__submod][$__action]))&&(!isset($redirAjaxArray[$__module][$__submod][$__action])))  {
	$__module="base"; $__submod="main"; $__action="default";   } //default page
    		if (!isNoHeader($__module,$__submod,$__action)) {
		  require_once("graph/header.inc.php");

                /* include CSS code for mains navigation bar for module that are not defined in global.css */
                foreach(fetchModulesList($conf["global"]["rootfsmodules"]) as $idx => $modroot) {
                    $css = $modroot . "/graph/navbar.css";
                    if (file_exists($css)) {
                        print '<style type="text/css"><!--';
                        include($css);
                        print '--></style>';
                    }
                }

		?>

		<style type="text/css">
		<!--

		<?php
                if (!isNoHeader($__module,$__submod,$__action)) {
		  require("graph/dynamicCss.php");
                }
		?>

		-->
		</style>


		<?
                }
                //ACL VERIFICATION

                if (!hasCorrectAcl($__module,$__submod,$__action))
                {
                  $__module="base"; $__submod="main"; $__action="default";
                  global $acl_error;
                  $acl_error = _("Error, you don't have correct rights !");
                  //if (!isNoHeader($module,$submod,$action)) {
		  //header("Location: " . getDefaultPage());
                  //} else {
                  if (!$_SESSION['login']) {
                    echo "<script>\n";
                        echo "window.location = '".getDefaultPage()."';";
                    echo "</script>\n";
                    return;
                  }
                  else {
                        //$n = new NotifyWidget();
                        //$n->add(_("Error, you don't have correct rights !"));
                    //echo _("Error, you don't have correct rights !");
                    echo "<script>\n";
                        //echo "window.location = '".$_SERVER['HTTP_REFERER']."';";
                        echo "window.location = '".getDefaultPage()."';";
                    echo "</script>\n";
                    return;
                  }
                  //}
		  exit;
                }

                if ($redirArray[$__module][$_GET["submod"]][$__action]) {
		require($redirArray[$__module][$_GET["submod"]][$__action]);
                } else {
                    if ($redirAjaxArray[$__module][$_GET["submod"]][$__action]) {
                    require($redirAjaxArray[$__module][$_GET["submod"]][$__action]);
                    }
                    else {
                        require("main_content.php");
                    }
                }


		if (!isNoHeader($__module,$_GET["submod"],$__action)) {require_once("graph/footer.inc.php");}
		//require("graph/footer.inc.php");


}


	global $maxperpage;       //necesaire pour la migration de template

	$root = $conf["global"]["root"];
	$maxperpage = $conf["global"]["maxperpage"];

//include PageGenerator primitives
require("includes/PageGenerator.php");



autoInclude();

ob_end_flush();
?>
