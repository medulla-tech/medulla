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

global $conf;

ob_start();

require("includes/assert.inc.php");
require("includes/session.inc.php");
require("includes/config.inc.php");
require_once("includes/i18n.inc.php");
require("includes/acl.inc.php");
require("includes/utils.inc.php");
require("includes/PageGenerator.php");
require("modules/base/includes/edit.inc.php");

/**
  Lookup and load all MMC modules
 */
function autoInclude() {
    global $redirArray;
    global $redirAjaxArray;
    global $conf;
    global $filter;

    $modules = fetchModulesList($conf["global"]["rootfsmodules"]);
    includeInfoPackage($modules);
    includePublicFunc($modules);

    if (isset($_GET["module"])) {
        $__module = $_GET["module"];
    } else {
        $__module = "default";
    }

    if (isset($_GET["submod"])) {
        $__submod = $_GET["submod"];
    } else {
        $__submod = "default";
    }

    if (isset($_GET["action"])) {
        $__action = $_GET["action"];
    } else {
        $__action = "default";
    }

    /* Check filter info */
    // we must be in a ajax call
    if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) and
            $_SERVER['HTTP_X_REQUESTED_WITH'] == "XMLHttpRequest" and
            isset($_GET['filter'])) {
        // get the page who called us
        preg_match('/module=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1]))
            $module = $matches[1];
        else
            $module = "default";
        preg_match('/submod=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1]))
            $submod = $matches[1];
        else
            $submod = "default";
        preg_match('/action=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1]))
            $action = $matches[1];
        else
            $action = "default";
        preg_match('/tab=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1]))
            $tab = $matches[1];
        else
            $tab = "default";

        // extra arguments of the request so we don't cache filters for another
        // page
        $extra = "";
        foreach ($_GET as $key => $value) {
            if (!in_array($key, array('module', 'submod', 'tab', 'action', 'filter', 'start', 'end', 'maxperpage')))
                $extra .= $key . "_" . $value;
        }
        // store the filter
        if (isset($_GET['filter']))
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_filter_" . $extra] = $_GET['filter'];
        // store pagination info
        if (isset($_GET['maxperpage']))
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_max_" . $extra] = $_GET['maxperpage'];
        if (isset($_GET['start']))
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_start_" . $extra] = $_GET['start'];
        if (isset($_GET['end']))
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_end_" . $extra] = $_GET['end'];

        unset($module);
        unset($submod);
        unset($action);
        unset($tab);
    }

    /* Redirect user to a default page. */
    if (!isset($redirArray[$__module][$__submod][$__action]) && !isset($redirAjaxArray[$__module][$__submod][$__action])
    ) {
        header("Location: " . getDefaultPage());
        exit;
    }

    if (!isNoHeader($__module, $__submod, $__action)) {
        require_once("graph/header.inc.php");
        /* Include specific module CSS if there is one */
        require("graph/dynamicCss.php");
    }

    /* ACL check */
    if (!hasCorrectAcl($__module, $__submod, $__action)) {
        header("Location: " . getDefaultPage());
        exit;
    }

    /* Warn user once at login if her account is expired. */
    if (in_array("ppolicy", $_SESSION["supportModList"])) {
        require_once("modules/ppolicy/default/warnuser.php");
    }

    if (!empty($redirArray[$__module][$__submod][$__action])) {
        require($redirArray[$__module][$__submod][$__action]);
        //debug($redirArray[$__module][$__submod][$__action]);
    } else if (!empty($redirAjaxArray[$__module][$__submod][$__action])) {
        require($redirAjaxArray[$__module][$__submod][$__action]);
    }

    require_once("includes/check_notify.inc.php");

    if (!isNoHeader($__module, $__submod, $__action)) {
        require_once("graph/footer.inc.php");
    }
}

global $maxperpage;
$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];

autoInclude();

//debug(get_included_files());

if (strlen(ob_get_contents()))
    ob_end_flush();
?>
