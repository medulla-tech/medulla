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


/**
 * module declaration
 */

$mod = new Module("pulse2");
$mod->setVersion("1.3.0");
$mod->setRevision('$Rev$');
$mod->setDescription(_T("Pulse2", "pulse2"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);

 
/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

$page = new Page("computers_list", _T("Computers list", "pulse2"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/pulse2/pulse2/computers_list.php");
$submod->addPage($page);

$page = new Page("select_location", _T("Location selection in computer edit", "pulse2"));
$page->setOptions(array("visible"=>False));
$page->setFile("modules/pulse2/includes/select_location.php");
$submod->addPage($page);

unset($submod);


?>
