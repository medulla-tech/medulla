<?php

/**
 * (c) 2025 Siveo, http://siveo.net/
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

/**
 *
 * This page is used work on the new MVC system without modifying the current bootmenu page
 * === PARAMS ===
 * debug : launch the generation of bootmenu in debug mode.
 * ==============
 *
 * STEP 1 : Create route in include/routes.php file
 * --------
 */

// Load automatically the called classes
$rootPath = __DIR__;
require_once($rootPath."/autoload.php");

// Wrap incomming SERVER and datas
$request = \Core\Request::getInstance();

// Handle some automatic preprocessing, like debug mode
require_once($rootPath.'/include/preprocess.php');

// Load the databases PDO objects and the config
$db = \Core\Config::getDb();
$config = \Core\Config::getConfig();

// Load the routes
require_once($rootPath.'/include/routes.php');

// Challenge the called uri and load the corresponding page
\Core\Route::test($request->config('method'), array_keys($_GET));
?>
