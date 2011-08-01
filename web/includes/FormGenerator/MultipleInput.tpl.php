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

require_once("../config.inc.php");

$name = $_POST['minputname'];

require_once("../i18n.inc.php");
require_once("../acl.inc.php");
require_once("../session.inc.php");

require_once ("../PageGenerator.php");
require_once ("../FormGenerator.php");

if (isset($_POST[$name])) {
    $arr = $_POST[$name];
} else {
    $arr = array();
}

if (isset($_POST['del'])) {
    if (count($arr)>1) {
        unset($arr[$_POST['del']]);
    }
    else if (count($arr) == 1) {
        $arr[$_POST['del']] = '';
    }
} else {
    $arr[]= '';
}

$arr = array_values($arr);

global $aclArray;
if (!isset($aclArray)) {
    /*
     * When this template is reloaded, we loose $aclArray, and this triggesr a PHP warning on some PHP version.
     * We can safely set it to an empty array.
     */
    $aclArray = array();
}

$mtpl = new MultipleInputTpl($name, urldecode($_POST['desc']), true);
$mtpl->setRegexp(stripslashes(rawurldecode($_POST['regexp'])));
$fe = new FormElement(_T($name,"mail"), $mtpl);
$fe->setCssError($name);
$fe->display($arr);
